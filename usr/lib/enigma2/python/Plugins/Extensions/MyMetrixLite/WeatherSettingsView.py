# -*- coding: UTF-8 -*-
#######################################################################
#
#    MyMetrixLite by arn354 & svox & Mr.Servo & jbleyel
#    based on
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#    Full refactor by jbleyel (c) 2022
#    MSN weatherserivce nikolasi
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################
from os.path import join as pathjoin, isdir

from twisted.internet.reactor import callInThread

from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.Sources.StaticText import StaticText
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import defaultInhibitDirs, LocationBox
from Screens.Setup import Setup
from Screens.MessageBox import MessageBox
from Tools.Weatherinfo import Weatherinfo
from . import _

#############################################################


class WeatherSettingsView(Setup):
	def __init__(self, session):
		Setup.__init__(self, session, "WeatherSettings", plugin="Extensions/MyMetrixLite", PluginLanguageDomain="MyMetrixLite")
		self["key_blue"] = StaticText(_("Location Selection"))
		self["key_yellow"] = StaticText(_("Defaults"))
		self["blueActions"] = HelpableActionMap(self, ["ColorActions"], {
			"blue": (self.keycheckCity, _("Search for your City")),
			"yellow": (self.defaults, _("Set default values"))
		}, prio=0, description=_("Weather Settings Actions"))
		self.old_weatherservice = config.plugins.MetrixWeather.weatherservice.value
		self.citylist = []
		self.checkcity = False
		self.closeonsave = False

	def keycheckCity(self, closesave=False):
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		self["footnote"].setText(_("Search for City ID please wait..."))
		self.closeonsave = closesave
		callInThread(self.searchCity, weathercity)

	def searchCity(self, weathercity):
		services = {"MSN": "msn", "OpenMeteo": "omw", "openweather": "owm"}
		service = services.get(config.plugins.MetrixWeather.weatherservice.value, "msn")
		apikey = config.plugins.MetrixWeather.apikey.value
		if service == "owm" and len(apikey) < 32:
			self.session.open(MessageBox, text=_("The API key for OpenWeatherMap is not defined or invalid.\nPlease verify your input data.\nOtherwise your settings won't be saved."), type=MessageBox.TYPE_WARNING)
		else:
			WI = Weatherinfo(service, config.plugins.MetrixWeather.apikey.value)
			if WI.error:
				print("[WeatherSettingsView] Error in module 'searchCity': %s" % WI.error)
				self["footnote"].setText(_("Error in Weatherinfo"))
				self.session.open(MessageBox, text=WI.error, type=MessageBox.TYPE_ERROR)
			else:
				geodatalist = WI.getCitylist(weathercity, config.osd.language.value.replace('_', '-').lower())
				if WI.error or geodatalist is None or len(geodatalist) == 0:
					print("[WeatherSettingsView] Error in module 'searchCity': %s" % WI.error)
					self["footnote"].setText(_("Error getting City ID"))
					self.session.open(MessageBox, text=_("City '%s' not found! Please try another wording." % weathercity), type=MessageBox.TYPE_WARNING)
#				elif len(geodatalist) == 1:
#					self["footnote"].setText(_("Getting City ID Success"))
#					self.saveGeoCode(geodatalist[0])
				else:
					self.citylist = []
					for item in geodatalist:
						lon = " [lon=%s" % item[1] if float(item[1]) != 0.0 else ""
						lat = ", lat=%s]" % item[2] if float(item[2]) != 0.0 else ""
						try:
							self.citylist.append(("%s%s%s" % (item[0], lon, lat), item[0], item[1], item[2]))
						except Exception:
							print("[WeatherSettingsView] Error in module 'showMenu': faulty entry in resultlist.")
					self.session.openWithCallback(self.choiceIdxCallback, ChoiceBox, titlebartext=_("Select Your Location"), title="", list=tuple(self.citylist))

	def choiceIdxCallback(self, answer):
		if answer is not None:
			self["footnote"].setText(answer[1])
			self.saveGeoCode((answer[1].split(",")[0], answer[2], answer[3]))

	def saveGeoCode(self, value):
		config.plugins.MetrixWeather.weathercity.value = value[0]
		config.plugins.MetrixWeather.owm_geocode.value = "%s,%s" % (float(value[1]), float(value[2]))
		self.old_weatherservice = config.plugins.MetrixWeather.weatherservice.value
		self.checkcity = False
		if self.closeonsave:
			from .plugin import infobarmetrixweatherhandler  # import needs to be here
			infobarmetrixweatherhandler.reconfigure()
			config.plugins.MetrixWeather.owm_geocode.save()
			Setup.keySave(self)

	def keySelect(self):
		if self.getCurrentItem() == config.plugins.MetrixWeather.iconpath:
			self.session.openWithCallback(self.keySelectCallback, WeatherSettingsLocationBox, currDir=config.plugins.MetrixWeather.iconpath.value)
			return
		if self.getCurrentItem() == config.plugins.MetrixWeather.weathercity:
			self.checkcity = True
		Setup.keySelect(self)

	def selectionChanged(self):
		Setup.selectionChanged(self)
		self.pathStatus()

	def changedEntry(self):
		Setup.changedEntry(self)
		self.pathStatus()

	def keySelectCallback(self, path):
		if path is not None:
			path = pathjoin(path, "")
			config.plugins.MetrixWeather.iconpath.value = path
		self["config"].invalidateCurrent()
		self.changedEntry()

	def pathStatus(self):
		if config.plugins.MetrixWeather.icontype.value == "2":
			if self["config"].getCurrentIndex() == config.plugins.MetrixWeather.iconpath:
				path = self.getCurrentValue()
				if not isdir(path):
					footnote = _("Directory '%s' does not exist!") % path
				else:
					footnote = ""
				self.setFootnote(footnote)

	def keySave(self):
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		if len(weathercity) < 3:
			self["footnote"].setText(_("The city name is too short. More than 2 characters are needed for search."))
			return
		if self.checkcity or self.old_weatherservice != config.plugins.MetrixWeather.weatherservice.value:
			self.keycheckCity(True)
			return
		if self["config"].isChanged():
			from .plugin import infobarmetrixweatherhandler  # import needs to be here
			infobarmetrixweatherhandler.reconfigure()
		config.plugins.MetrixWeather.owm_geocode.save()
		Setup.keySave(self)

	def defaults(self, SAVE=False):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				if SAVE:
					x[1].save()
		config.plugins.MetrixWeather.owm_geocode.value = config.plugins.MetrixWeather.owm_geocode.default
		if SAVE:
			config.plugins.MetrixWeather.owm_geocode.save()
		if self.session:
			Setup.createSetup(self)

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)


class WeatherSettingsLocationBox(LocationBox):
	def __init__(self, session, currDir):
		inhibit = defaultInhibitDirs
		inhibit.remove("/usr")
		inhibit.remove("/share")
		if currDir == "":
			currDir = None
		LocationBox.__init__(
			self,
			session,
			text=_("Where do you want to get the MetrixWeather icons?"),
			currDir=currDir,
			inhibitDirs=inhibit,
		)
		self.skinName = ["WeatherSettingsLocationBox", "LocationBox"]
