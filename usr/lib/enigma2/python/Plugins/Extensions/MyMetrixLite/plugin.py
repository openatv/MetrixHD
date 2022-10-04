#######################################################################
#
#    MetrixHD Plugin.py by arn354, svox, Mr.Servo and jbleyel
#    based on
#    MyMetrix
#    Coded by iMaxxx (c) 2013
#    Refactor by Mr.Servo and jbleyel (c) 2022
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

from . import _
from enigma import eTimer
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigSelectionNumber, ConfigText, ConfigNumber
from Components.Label import Label, MultiColorLabel
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import BoxInfo
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Weatherinfo import Weatherinfo
from .MainSettingsView import MainSettingsView
from .ActivateSkinSettings import applySkinSettings

#############################################################
config.plugins.MetrixWeather = ConfigSubsection()
config.plugins.MetrixWeather.enabled = ConfigYesNo(default=True)
config.plugins.MetrixWeather.detail = ConfigYesNo(default=False)
config.plugins.MetrixWeather.type = ConfigYesNo(default=False)
config.plugins.MetrixWeather.animationspeed = ConfigSelection(default="100", choices=[("0", _("Off")), ("20", _("+ 4")), ("40", _("+ 3")), ("60", _("+ 2")), ("80", _("+ 1")), ("100", _("Default")), ("125", _("- 1")), ("150", _("- 2")), ("200", _("- 3")), ("300", _("- 4"))])
config.plugins.MetrixWeather.MoviePlayer = ConfigYesNo(default=True)
config.plugins.MetrixWeather.verifyDate = ConfigYesNo(default=True)
config.plugins.MetrixWeather.refreshInterval = ConfigSelectionNumber(0, 1440, 30, default=120, wraparound=True)
config.plugins.MetrixWeather.apikey = ConfigText(default="a4bd84726035d0ce2c6185740617d8c5")
# Beyonwiz - marketed only in Australia
geodata = ("Sydney, New South Wales, AU", "151.2082848,-33.8698439") if BoxInfo.getItem("machinebuild").startswith("beyonwiz") else ("Hamburg, DE", "10.000654,53.550341")
config.plugins.MetrixWeather.weathercity = ConfigText(default=geodata[0], visible_width=250, fixed_size=False)
config.plugins.MetrixWeather.geoCode = ConfigText(default=geodata[1])
config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices=[("Celsius", _("Celsius")), ("Fahrenheit", _("Fahrenheit"))])
config.plugins.MetrixWeather.service = ConfigSelection(default="MSN", choices=[("MSN", _("MSN")), ("openweather", _("openweather"))])
config.plugins.MetrixWeather.forecast = ConfigSelectionNumber(0, 5, 1, default=1, wraparound=True)
config.plugins.MetrixWeather.currentWeatherDataValid = ConfigNumber(default=0)
config.plugins.MetrixWeather.weatherservice = ConfigSelection(default="MSN", choices=[
	("MSN", _("MSN")),
	("openweather", _("openweather"))
])

#######################################################################

MODULE_NAME = __name__.split(".")[-1]


class InfoBarMetrixWeather(Screen):
	overlay = None

	def __init__(self, session):
		Screen.__init__(self, session)
		if self.cleanUp not in self.onClose:
			self.onClose.append(self.cleanUp)
		mode = "msn" if config.plugins.MetrixWeather.service.value == "MSN" else "owm"
		self.WI = Weatherinfo(mode, config.plugins.MetrixWeather.apikey.value)
		self.oldmode = mode
		self.weathercity = None
		self.forecast = config.plugins.MetrixWeather.forecast.value
		if config.plugins.MyMetrixLiteOther.showExtendedinfo.value and config.plugins.MyMetrixLiteOther.ExtendedinfoStyle.value in ("2", "3") == "2":  # Weather enabled with normal symbols and extended info enabled between clock and weather enclosed or centered
			self.skinname = ["InfoBarMetrixWeatherMin"]
			if self.forecast > 1:
				self.forecast = 1
		else:
			self.skinname = ["InfoBarMetrixWeatherMax"]
		# init for screen "infoBarWeather"
		self["Temp"] = Label("")
		self["Tempsign"] = Label()
		self["IconCode"] = StaticText("")
		self["FontCode"] = StaticText("")
		self["ShortDay"] = Label("")
		self["Shorttext"] = Label("")  # Das gibt es nicht
		self["MinTemp"] = Label()
		self["MaxTemp"] = Label()
		self["Observationtime"] = Label("")
		self["Feelslike"] = Label("")
		self["Humidity"] = Label("")
		self["WindDisplay"] = Label("")
		self["WindArrow"] = Label("")  # Das gibt es nicht
		self["WindSpeed"] = Label("")
		self["WindDir"] = Label("")  # Das gibt es nicht
		self["currentDataValid"] = MultiColorLabel("")
		if config.plugins.MetrixWeather.detail.value:
			self["Location"] = Label("")
		for day in range(1, self.forecast + 1):  # define user-demanded forecasts only
			self["ShortDay_%d" % day] = Label("")
			self["IconCode_%d" % day] = StaticText("")
			self["FontCode_%d" % day] = StaticText("")
			self["MinTemp_%d" % day] = Label("")
			self["MaxTemp_%d" % day] = Label("")
		InfoBarMetrixWeather.overlay = self
		self.setWeatherDataValid(0)  # 0= try to getting weather data, 1= try to getting weather data paused, 2= try to getting weather data aborted (to many error cycles), 3= weather data valid
		self.trycounter = 0
		self.refreshTimer = eTimer()
		self.refreshTimer.callback.append(self.refreshWeatherData)
		self.refreshTimer.start(5000, True)

	def refreshWeatherData(self, entry=None):
		self.refreshTimer.stop()
		self.weathercity = config.plugins.MetrixWeather.weathercity.value
		geocode = config.plugins.MetrixWeather.geoCode.value.split(",")
		geodata = (self.weathercity, geocode[0], geocode[1])  # tuple ("Cityname", longitude, latitude)
		language = config.osd.language.value.replace("_", "-")
		unit = "imperial" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "metric"
		print("[%s] lookup for City %s, try #%s..." % (MODULE_NAME, self.weathercity, self.trycounter))
		self.WI.start(geodata=geodata, units=unit, scheme=language, reduced=True, callback=self.refreshWeatherDataCallback)

	def refreshWeatherDataCallback(self, data, error):
		if error:
			print(error)
			self.trycounter += 1
			if self.trycounter < 3:
				print("[%s] lookup for city '%s' paused, try again in 5 secs..." % (MODULE_NAME, self.weathercity))
				self.setWeatherDataValid(1)
				self.refreshTimer.callback.append(self.refreshWeatherData)
				self.refreshTimer.start(5000, True)
			else:
				print("[%s] lookup for city '%s' paused 5 mins, to many errors..." % (MODULE_NAME, self.weathercity))
				self.setWeatherDataValid(2)
				self.trycounter = 0
				self.refreshTimer.callback.append(self.refreshWeatherData)
				self.refreshTimer.start(30000, True)
			return
		skydirs = {"N": _("North"), "NE": _("Northeast"), "E": _("East"), "SE": _("Southeast"), "S": _("South"), "SW": _("Southwest"), "W": _("West"), "NW": _("Northwest")}
		if config.plugins.MetrixWeather.service.value == "openweather":
			geocode = "%s,%s" % (data["longitude"], data["latitude"])
			if geocode != self.geocode:
				config.plugins.MetrixWeather.owm_geocode.value = geocode
				config.plugins.MetrixWeather.owm_geocode.save()
		speedsign = "mph" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "km/h"
		tempsign = "°F" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "°C"
		# data for panel "infoBarWeather"
		self["Temp"].setText("%s" % data["current"]["temp"])
		self["Tempsign"].setText(tempsign)
		if config.plugins.MetrixWeather.type.value:
			self["IconCode"].setText(data["current"]["yahooCode"])
		else:
			self["FontCode"].setText(data["current"]["meteoCode"])
		self["ShortDay"].setText(data["current"]["shortDay"])
		self["Shorttext"].setText(data["current"]["text"])  # GEHT NICHT
		self["MinTemp"].setText("%s %s" % (data["forecast"][0]["minTemp"], tempsign))
		self["MaxTemp"].setText("%s %s" % (data["forecast"][0]["maxTemp"], tempsign))
		# data for panel "infoBarWeatherDetails"
		if config.plugins.MetrixWeather.detail.value:
			self["Location"].setText(data["name"])  # trigger "on" for panel "infoBarWeatherDetails"
			self["Observationtime"].setText(data["current"]["observationTime"][11:19])
			self["Feelslike"].setText("%s %s" % (data["current"]["feelsLike"], tempsign))
			self["Humidity"].setText("%s %s" % (data["current"]["humidity"], "%"))
			skydirection = data["current"]["windDirSign"].split(" ")
			self["WindDisplay"].setText(skydirs[skydirection[1]] if skydirection[1] in skydirs else skydirection[1])
			self["WindArrow"].setText(chr(ord(skydirection[0]) - 8496))
			self["WindSpeed"].setText("%s %s" % (data["current"]["windSpeed"], speedsign))
			self["WindDir"].setText("%s %s" % (data["current"]["windDir"], "°"))
		# data for panels "forecast"
		for day in range(1, self.forecast + 1):  # only user-demanded forecasts
			if config.plugins.MetrixWeather.type.value:
				self["IconCode_%d" % day].setText(data["forecast"][day]["yahooCode"])
			else:
				self["FontCode_%d" % day].setText(data["forecast"][day]["meteoCode"])
			self["ShortDay_%d" % day].setText(data["forecast"][day]["shortDay"])
			self["MinTemp_%d" % day].setText("%s %s" % (data["forecast"][day]["minTemp"], tempsign))
			self["MaxTemp_%d" % day].setText("%s %s" % (data["forecast"][day]["maxTemp"], tempsign))
		self.trycounter = 0
		self.setWeatherDataValid(2)

		seconds = int(config.plugins.MetrixWeather.refreshInterval.value * 60)
		self.refreshTimer.start(seconds * 1000, True)

	def setWeatherDataValid(self, value):
		config.plugins.MetrixWeather.currentWeatherDataValid.value = value
		config.plugins.MetrixWeather.currentWeatherDataValid.save()
		self["currentDataValid"].setText("")
		self["currentDataValid"].setBackgroundColorNum(value)
		self["currentDataValid"].hide()

	def cleanUp(self):
		self.refreshTimer.stop()
		if self.cleanUp in self.onClose:
			self.onClose.remove(self.cleanUp)
		InfoBarMetrixWeather.overlay = None


class InfoBarMetrixWeatherHandler():
	def sessioninit(self, session):
		print("InfoBarMetrixWeatherHandler sessioninit")
		session.instantiateDialog(InfoBarMetrixWeather)
		self.session = session

	def processDisplay(self, state):
		if config.plugins.MetrixWeather.enabled.value:
			if state:
				InfoBarMetrixWeather.overlay.show()
			else:
				InfoBarMetrixWeather.overlay.hide()

	def hookInfoBar(self, reason, instanceInfoBar):
		if reason:
			instanceInfoBar.connectShowHideNotifier(self.processDisplay)
		else:
			instanceInfoBar.disconnectShowHideNotifier(self.processDisplay)

	def reconfigure(self):
		InfoBarMetrixWeather.instance.close()
		self.session.instantiateDialog(InfoBarMetrixWeather)


def main(session, **kwargs):
	session.open(MainSettingsView)


def sessionmain(reason, session, **kwargs):
	print("InfoBarMetrixWeatherHandler sessionmain")
	if reason == 0:
		infobarmetrixweatherhandler.sessioninit(session)


def autostart(reason, **kwargs):
	if reason == 0:
		applySkinSettings(fullInit=True)


def info(reason, session, **kwargs):
	print("InfoBarMetrixWeatherHandler info")
	typeInfoBar = kwargs["typeInfoBar"]
	if config.plugins.MetrixWeather.enabled.value:
		if typeInfoBar == "InfoBar" or (config.plugins.MetrixWeather.moviePlayer.value and typeInfoBar == "moviePlayer"):
			infobarmetrixweatherhandler.hookInfoBar(reason, kwargs["instance"])


def Plugins(**kwargs):
	pluginList = []
	if "MetrixHD" in config.skin.primary_skin.value:
		pluginList.append(PluginDescriptor(name="MyMetrixLite", where=[PluginDescriptor.WHERE_INFOBARLOADED], fnc=info, needsRestart=False))
		pluginList.append(PluginDescriptor(name="MyMetrixLite", where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionmain, needsRestart=False))
		pluginList.append(PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART], fnc=autostart))
		pluginList.append(PluginDescriptor(name="MyMetrixLite", description=_("openATV configuration tool for MetrixHD"), icon="plugin.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=main))
	return pluginList


infobarmetrixweatherhandler = InfoBarMetrixWeatherHandler()
