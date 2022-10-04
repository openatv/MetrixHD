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
from os import system

from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config
from Components.MenuList import MenuList
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Setup import Setup
from Tools.Directories import fileExists
from Tools.Weatherinfo import Weatherinfo

from . import _, MAIN_IMAGE_PATH

#############################################################


class WeatherSettingsLocation(Screen):
	skin = """
		<screen position="center,center" size="380,80" title="%s">
		<widget name="menu" position="5,5" size="370,80" />
		</screen>""" % _('Select Your Location')

	def __init__(self, session, weathercity):
		Screen.__init__(self, session)
		self.setTitle(_('Select Your Location'))
		self.session = session
		self.weathercity = weathercity
		self.citylist = []
		self['menu'] = MenuList(self.citylist)
		self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'ok': self.okClicked,
			'cancel': self.close,
			'up': self.pageUp,
			'down': self.pageDown}, -1)
		self.onLayoutFinish.append(self.onLayoutFinished)  # ToDo: das habe ich wegen dem Modal-Fehler eingebaut, nutzt aber nix

	def onLayoutFinished(self):  # ToDo: das habe ich wegen dem Modal-Fehler eingebaut, nutzt aber nix
		self.showMenu(self.weathercity)

	def pageUp(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveUp)

	def pageDown(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveDown)

	def showMenu(self, weathercity):
		self.geodatalist = self.searchCity(weathercity)
#		ToDo: Messagebox macht BS mit Fehler: "Modal open are allowed only from a screen which is modal!"
#		self.geodatalist = None     erzwinge den Fehler
		if self.geodatalist is None or len(self.geodatalist) == 0:
			self.session.open(MessageBox, _("""Server access error! Try again, possibly a few hours later.\n
											MSN-Weather: without specifying an exact position, the weather forecast\n
											may possibly apply to a different location.\n
											Openweathermap: without specifying an exact position, the weather forecast\n
											is made for a completely wrong location."""), MessageBox.TYPE_INFO, close_on_any_key=True)
			print("[WeatherSettingsView] Error in module 'showMenu': no results found.")
			return False
		if len(self.geodatalist) == 1:
			self.close(self.geodatalist[0])
		self.citylist = []
		for item in self.geodatalist:
			lon = " [lon=%s" % item[1] if float(item[1]) != 0.0 else ""
			lat = ", lat=%s]" % item[2] if float(item[2]) != 0.0 else ""
			try:
				self.citylist.append("%s%s%s" % (item[0], lon, lat))
			except Exception:
				print("[WeatherSettingsView] Error in module 'showMenu': faulty entry in resultlist.")
		self['menu'].l.setList(self.citylist)

	def okClicked(self):
		idx = self['menu'].getSelectedIndex()
		if idx is not None and self.geodatalist is not None:
			if len(self.geodatalist[idx][0]) > 30:  # reduce weathercity when too long
				cityparts = self.geodatalist[idx][0].split(",")
				if len(cityparts) == 3:
					weathercity = "%s,%s" % (cityparts[0], cityparts[2])
			else:
				weathercity = self.geodatalist[idx][0]
			print("[WeatherSettingsView] set new owm_geocode: %s" % config.plugins.MetrixWeather.owm_geocode.value)
			if fileExists('/tmp/weathermsn.xml'):  # ToDo: kann das weg? Evtl. eine Altlast?
				system('rm /tmp/weathermsn.xml')
			self.close((weathercity, self.geodatalist[idx][1], self.geodatalist[idx][2]))

	def searchCity(self, weathercity):
		service = "msn" if config.plugins.MetrixWeather.weatherservice.value == "MSN" else "owm"
		WI = Weatherinfo(service, config.plugins.MetrixWeather.apikey.value)
		if WI.error:
			print("[WeatherSettingsView] Error in module 'searchCity': %s" % WI.error)
			return None
		citylist = WI.getCitylist(weathercity, config.osd.language.value.replace('_', '-').lower())
		if WI.error:
			print("[WeatherSettingsView] Error in module 'searchCity': %s" % WI.error)
			return None
		return citylist


class WeatherSettingsView(Setup):
	def __init__(self, session):
		Setup.__init__(self, session, "WeatherSettings", plugin="Extensions/MyMetrixLite")
		self["key_blue"] = StaticText()
		self["blueActions"] = HelpableActionMap(self, ["ColorActions"], {
			"blue": (self.checkID, _("Get ID for your City"))
		}, prio=0, description=_("Weather Settings Actions"))
		self.old_weatherservice = config.plugins.MetrixWeather.weatherservice.value
		self.old_weathercity = config.plugins.MetrixWeather.weathercity.value

	def checkID(self):
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		self.session.openWithCallback(self.locationCallback, WeatherSettingsLocation, weathercity)

	def locationCallback(self, value):
		if value:
			config.plugins.MetrixWeather.weathercity.value = value[0]
			config.plugins.MetrixWeather.owm_geocode.value = "%s,%s" % (float(value[1]), float(value[2]))
			Setup.keySave(self)
			self.close()

	def keySave(self):
		weathercity = config.plugins.MetrixWeather.weathercity.value.split(",")[0]
		if len(weathercity) < 3:
			self["footnote"].setText(_("The city name is too short. More than 2 characters are needed for search."))
			return
		if self.old_weatherservice != config.plugins.MetrixWeather.weatherservice.value or self.old_weathercity != config.plugins.MetrixWeather.weathercity.value:
			self.checkID()
			return
		Setup.keySave(self)
