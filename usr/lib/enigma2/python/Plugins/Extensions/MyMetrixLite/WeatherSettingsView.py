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
from os.path import isdir, join
from twisted.internet.threads import deferToThread

from enigma import eTimer

from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.Sources.StaticText import StaticText
from Screens.ChoiceBox import ChoiceBox
from Screens.LocationBox import LocationBox, defaultInhibitDirs
from Screens.MessageBox import MessageBox
from Screens.Setup import Setup
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
		self.citySearch = None
		self.cityResults = None
		self.cityResultTimer = eTimer()
		self.cityResultTimer.callback.append(self.showCityResults)
		self.onExecBegin.append(self.queueCityResults)
		self.onClose.append(self.cancelCitySearch)

	def keycheckCity(self, closesave=False):
		if self.citySearch is not None:
			self.closeonsave = self.closeonsave or closesave
			return
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		self.setFootnote(_("Search for City ID please wait..."))
		self.closeonsave = closesave
		self.searchCity(weathercity)

	def searchCity(self, weathercity):
		if self.citySearch is not None:
			return
		services = {"MSN": "msn", "OpenMeteo": "omw", "openweather": "owm"}
		service = services.get(config.plugins.MetrixWeather.weatherservice.value, "msn")
		apiKey = config.plugins.MetrixWeather.apikey.value
		if service == "owm" and len(apiKey) < 32:
			self.closeonsave = False
			self.setFootnote(_("Error in Weatherinfo"))
			self.session.open(MessageBox, text=_("The API key for OpenWeatherMap is not defined or invalid.\nPlease verify your input data.\nOtherwise your settings won't be saved."), type=MessageBox.TYPE_WARNING)
		else:
			language = config.osd.language.value.replace("_", "-").lower()
			# Pass a snapshot to the worker; it must not access settings or GUI objects.
			search = self.citySearch = deferToThread(self.lookupCity, weathercity, service, apiKey, language)
			search.addCallbacks(self.citySearchFinished, self.citySearchFailed, callbackArgs=(search, weathercity), errbackArgs=(search, weathercity))

	@staticmethod
	def lookupCity(weatherCity, service, apiKey, language):
		weatherInfo = Weatherinfo(service, apiKey)
		geoData = None if weatherInfo.error else weatherInfo.get_citylist(weatherCity, language)
		return geoData, weatherInfo.error

	def citySearchFinished(self, result, search, weatherCity):
		# Screen.doClose clears all attributes, so late callbacks must use getattr.
		if getattr(self, "citySearch", None) is search:
			self.cityResults = (weatherCity, result)
			self.queueCityResults()

	def citySearchFailed(self, failure, search, weatherCity):
		self.citySearchFinished((None, str(failure.value)), search, weatherCity)

	def queueCityResults(self):
		if getattr(self, "cityResults", None) is not None:
			# Let pending dialog callbacks (including confirmed cancellation) finish first.
			self.cityResultTimer.start(0, True)

	def showCityResults(self):
		if getattr(self, "cityResults", None) is None or not self.session.in_exec or self.session.current_dialog is not self:
			return
		weatherCity, (geoData, error) = self.cityResults
		self.cityResults = None
		if error:
			self.citySearch = None
			self.closeonsave = False
			print(f"[WeatherSettingsView] Error in module 'searchCity': {error}")
			self.setFootnote(_("Error in Weatherinfo"))
			self.session.open(MessageBox, text=error, type=MessageBox.TYPE_ERROR)
		else:
			self.citylist = []
			for item in geoData or ():
				try:
					cityName, longitude, latitude = item
					if not isinstance(cityName, str):
						continue
					lon = f" [lon={longitude}" if float(longitude) != 0.0 else ""
					lat = f", lat={latitude}]" if float(latitude) != 0.0 else ""
					self.citylist.append((f"{cityName}{lon}{lat}", cityName, longitude, latitude))
				except (TypeError, ValueError):
					print("[WeatherSettingsView] Error in module 'showMenu': faulty entry in resultlist.")
			if self.citylist:
				self.session.openWithCallback(self.choiceIdxCallback, ChoiceBox, titlebartext=_("Select Your Location"), title="", list=tuple(self.citylist))
			else:
				self.citySearch = None
				self.closeonsave = False
				self.setFootnote(_("Error getting City ID"))
				self.session.open(MessageBox, text=_("City '%s' not found! Please try another wording.") % weatherCity, type=MessageBox.TYPE_WARNING)

	def cancelCitySearch(self):
		search = getattr(self, "citySearch", None)
		self.citySearch = None
		self.cityResults = None
		self.closeonsave = False
		if getattr(self, "cityResultTimer", None) is not None:
			self.cityResultTimer.stop()
		if search is not None:
			search.cancel()

	def choiceIdxCallback(self, answer):
		if not getattr(self, "session", None):
			return
		self.citySearch = None
		if answer is not None:
			self.setFootnote(answer[1])
			self.saveGeoCode((answer[1].split(",")[0], answer[2], answer[3]))
		else:
			self.closeonsave = False
			self.setFootnote("")

	def saveGeoCode(self, value):
		config.plugins.MetrixWeather.weathercity.value = value[0]
		config.plugins.MetrixWeather.owm_geocode.value = f"{float(value[1])},{float(value[2])}"
		self.old_weatherservice = config.plugins.MetrixWeather.weatherservice.value
		self.checkcity = False
		if self.closeonsave:
			from .plugin import infobarmetrixweatherhandler  # Avoid circular imports while plugin.py initializes the settings.
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
		self.cancelCitySearch()
		Setup.changedEntry(self)
		self.pathStatus()

	def keySelectCallback(self, path):
		if path is not None:
			path = join(path, "")
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
		if self.citySearch is not None:
			self.closeonsave = True
			return
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		if len(weathercity) < 3:
			self.setFootnote(_("The city name is too short. More than 2 characters are needed for search."))
			return
		if self.checkcity or self.old_weatherservice != config.plugins.MetrixWeather.weatherservice.value:
			self.keycheckCity(True)
			return
		if self["config"].isChanged():
			from .plugin import infobarmetrixweatherhandler  # Avoid circular imports while plugin.py initializes the settings.
			infobarmetrixweatherhandler.reconfigure()
		config.plugins.MetrixWeather.owm_geocode.save()
		Setup.keySave(self)

	def defaults(self, SAVE=False):
		self.cancelCitySearch()
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
		inhibit = defaultInhibitDirs[:]
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
