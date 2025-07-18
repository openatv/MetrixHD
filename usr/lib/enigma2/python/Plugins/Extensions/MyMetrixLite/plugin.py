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
from pickle import dump, load
from os import remove
from os.path import getmtime, isfile, join
from time import time
from datetime import datetime, timezone
from enigma import eTimer

from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, ConfigSelectionNumber, ConfigText, ConfigNumber, NoSave
from Components.Label import Label
from Components.Pixmap import MultiPixmap
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import BoxInfo
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import SCOPE_CONFIG, SCOPE_SKINS, resolveFilename
from Tools.Weatherinfo import Weatherinfo

from . import _
from .MainSettingsView import MainSettingsView
from .ActivateSkinSettings import applySkinSettings

#############################################################
config.plugins.MetrixWeather = ConfigSubsection()
config.plugins.MetrixWeather.enabled = ConfigYesNo(default=True)
config.plugins.MetrixWeather.detail = ConfigYesNo(default=False)
config.plugins.MetrixWeather.type = ConfigYesNo(default=False)
config.plugins.MetrixWeather.icontype = ConfigSelection(default="0", choices=[("0", _("Meteo Icons")), ("1", _("Animated Icons")), ("2", _("Static Icons"))])
if config.plugins.MetrixWeather.type.value:  # Restore old setting
	config.plugins.MetrixWeather.icontype.value = "1"
	config.plugins.MetrixWeather.icontype.save()
	config.plugins.MetrixWeather.type.value = False
	config.plugins.MetrixWeather.type.save()
config.plugins.MetrixWeather.animationspeed = ConfigSelection(default="100", choices=[("0", _("Off")), ("20", _("+ 4")), ("40", _("+ 3")), ("60", _("+ 2")), ("80", _("+ 1")), ("100", _("Default")), ("125", _("- 1")), ("150", _("- 2")), ("200", _("- 3")), ("300", _("- 4"))])
config.plugins.MetrixWeather.iconpath = ConfigText(default=join(resolveFilename(SCOPE_SKINS), "WeatherIconSets"))
config.plugins.MetrixWeather.nighticons = ConfigYesNo(default=True)
config.plugins.MetrixWeather.cachedata = ConfigSelection(default="60", choices=[("0", _("Disabled"))] + [(str(x), _("%d Minutes") % x) for x in (30, 60, 120)])
config.plugins.MetrixWeather.MoviePlayer = ConfigYesNo(default=True)
config.plugins.MetrixWeather.refreshInterval = ConfigSelectionNumber(0, 1440, 30, default=120, wraparound=True)
config.plugins.MetrixWeather.apikey = ConfigText(default="", fixed_size=False)
# Beyonwiz - marketed only in Australia
GEODATA = ("Sydney, New South Wales, AU", "151.2082848,-33.8698439") if BoxInfo.getItem("machinebuild").startswith("beyonwiz") else ("Hamburg, DE", "10.000654,53.550341")
config.plugins.MetrixWeather.weathercity = ConfigText(default=GEODATA[0], visible_width=250, fixed_size=False)
config.plugins.MetrixWeather.owm_geocode = ConfigText(default=GEODATA[1])
config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices=[("Celsius", _("Celsius")), ("Fahrenheit", _("Fahrenheit"))])
config.plugins.MetrixWeather.weatherservice = ConfigSelection(default="MSN", choices=[("MSN", _("MSN weather")), ("OpenMeteo", _("Open-Meteo Wetter")), ("openweather", _("OpenWeatherMap"))])
config.plugins.MetrixWeather.forecast = ConfigSelectionNumber(0, 5, 1, default=1, wraparound=True)
config.plugins.MetrixWeather.currentWeatherDataValid = NoSave(ConfigNumber(default=3))
config.plugins.MetrixWeather.cityVisible = ConfigYesNo(default=True)

# omw migration
config.plugins.MetrixWeather.woeid = ConfigNumber(default=0)

# fallback for old code can be removed in next version
config.plugins.MetrixWeather.currentLocation = ConfigText("")
if config.plugins.MetrixWeather.currentLocation.value:
	config.plugins.MetrixWeather.weathercity.value = config.plugins.MetrixWeather.currentLocation.value
	config.plugins.MetrixWeather.currentLocation.value = ""
	config.plugins.MetrixWeather.currentLocation.save()


# support old MetrixHDWeather Converter
config.plugins.MetrixWeather.currentWeatherTemp = NoSave(ConfigText(default="0"))
config.plugins.MetrixWeather.currentWeatherCode = NoSave(ConfigText(default="("))
config.plugins.MetrixWeather.forecastTodayTempMin = NoSave(ConfigText(default="0"))
config.plugins.MetrixWeather.forecastTodayTempMax = NoSave(ConfigText(default="0"))
config.plugins.MetrixWeather.forecastTomorrowCode = NoSave(ConfigText(default="("))
config.plugins.MetrixWeather.forecastTomorrowTempMin = NoSave(ConfigText(default="0"))
config.plugins.MetrixWeather.forecastTomorrowTempMax = NoSave(ConfigText(default="0"))

#######################################################################

MODULE_NAME = "InfoBarMetrixWeather"

CACHEFILE = resolveFilename(SCOPE_CONFIG, "MetrixWeather.dat")


class InfoBarMetrixWeatherNoData(Screen):
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		self["Temp"] = Label("N/A")
		InfoBarMetrixWeatherNoData.instance = self


class InfoBarMetrixWeather(Screen):
	instance = None

	def __init__(self, session):
		Screen.__init__(self, session)
		modes = {"MSN": "msn", "openweather": "owm", "OpenMeteo": "omw"}
		mode = modes.get(config.plugins.MetrixWeather.weatherservice.value, "msn")
		self.WI = Weatherinfo(mode, config.plugins.MetrixWeather.apikey.value)
		self.geocode = config.plugins.MetrixWeather.owm_geocode.value.split(",")
		self.oldmode = mode
		self.weathercity = None
		self.forecast = config.plugins.MetrixWeather.forecast.value
		if config.plugins.MyMetrixLiteOther.showExtendedinfo.value and config.plugins.MyMetrixLiteOther.ExtendedinfoStyle.value in ("2", "3"):  # Weather enabled with normal symbols and extended info enabled between clock and weather enclosed or centered
			self.skinName = [f"InfoBarMetrixWeather{config.plugins.MyMetrixLiteOther.ExtendedinfoStyle.value}"]
			if self.forecast > 1:
				self.forecast = 1
		else:
			self.skinName = ["InfoBarMetrixWeather1"]

		self["Temp"] = Label("")
		self["Tempsign"] = Label()
		self["IconCode"] = StaticText("")
		self["FontCode"] = StaticText("")
		self["ShortDay"] = Label("")
		self["MinTemp"] = Label()
		self["MaxTemp"] = Label()

		if config.plugins.MetrixWeather.detail.value:
			if config.plugins.MetrixWeather.cityVisible.value:
				self["LocationIcon"] = Label(",")
			else:
				self["NoLocation"] = Label()
			self["Location"] = Label("")
			self["logo"] = MultiPixmap()
			self["logo"].hide()
			self["Observationtime"] = Label("")
			self["Feelslike"] = Label("")
			self["Humidity"] = Label("")
			self["WindDisplay"] = Label("")
			self["WindSpeed"] = Label("")
			# self["Shorttext"] = Label("")
			self["WindArrow"] = Label("")

		for day in range(1, self.forecast + 1):  # define user-demanded forecasts only
			self["ShortDay_%d" % day] = Label("")
			self["IconCode_%d" % day] = StaticText("")
			self["FontCode_%d" % day] = StaticText("")
			self["MinTemp_%d" % day] = Label("")
			self["MaxTemp_%d" % day] = Label("")

		self.trialcounter = 0
		self.refreshTimer = eTimer()
		self.refreshTimer.callback.append(self.refreshWeatherData)
		self.onLayoutFinish.append(self.getCacheData)
		self.onClose.append(self.__onClose)
		InfoBarMetrixWeather.instance = self

	def __onClose(self):
		self.WI.stop()
		self.refreshTimer.stop()

	def getCacheData(self):
		#self.setWeatherDataValid(1)  # 0= green (data available), 1= yellow (still working), 2= red (no data available, wait on next refresh)
		cacheminutes = int(config.plugins.MetrixWeather.cachedata.value)
		if cacheminutes and isfile(CACHEFILE):
			timedelta = (time() - getmtime(CACHEFILE)) / 60
			if cacheminutes > timedelta:
				with open(CACHEFILE, "rb") as fd:
					cache_data = load(fd)
				self.writeData(cache_data)
				return

		self.refreshTimer.start(3000, True)

	def refreshWeatherData(self, entry=None):
		self.refreshTimer.stop()
		if config.misc.firstrun.value:  # don't refresh on firstrun try again after 10 seconds
			print(f"[{MODULE_NAME}] DEBUG firstrun")
			self.refreshTimer.start(600000, True)
			return
		if config.plugins.MetrixWeather.enabled.value:
			self.weathercity = config.plugins.MetrixWeather.weathercity.value
			geocode = config.plugins.MetrixWeather.owm_geocode.value.split(",")
			# DEPRECATED, will be removed in April 2023
			if geocode == ['0.0', '0.0']:
				geodatalist = self.WI.getCitylist(config.plugins.MetrixWeather.weathercity.value.split(",")[0], config.osd.language.value.replace('_', '-').lower())
				if geodatalist is not None and len(geodatalist[0]) == 3:
					geocode = [geodatalist[0][1], geodatalist[0][2]]
					config.plugins.MetrixWeather.weathercity.value = geodatalist[0][0]
					config.plugins.MetrixWeather.weathercity.save()
					config.plugins.MetrixWeather.owm_geocode.value = f"{float(geocode[0])},{float(geocode[1])}"
					config.plugins.MetrixWeather.owm_geocode.save()
			# DEPRECATED, will be removed in April 2023
			if geocode and len(geocode) == 2:
				geodata = (self.weathercity, geocode[0], geocode[1])  # tuple ("Cityname", longitude, latitude)
			else:
				geodata = None
			language = config.osd.language.value.replace("_", "-")
			unit = "imperial" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "metric"
			# DEPRECATED woid will be removed in April 2023
			woid = None
			if config.plugins.MetrixWeather.weatherservice.value == "openweather" and config.plugins.MetrixWeather.woeid.value != 0:
				woid = config.plugins.MetrixWeather.woeid.value
				print(f"[{MODULE_NAME}] lookup for CityID {str(woid)}, try #{self.trialcounter}...")
			else:
				print(f"[{MODULE_NAME}] lookup for City {self.weathercity}, try #{self.trialcounter}...")
			if geodata or woid:
				self.WI.start(geodata=geodata, cityID=woid, units=unit, scheme=language, reduced=True, callback=self.refreshWeatherDataCallback)
			else:
				print(f"[{MODULE_NAME}] error in MetrixWeather config")
				self.setWeatherDataValid(2)

	def refreshWeatherDataCallback(self, data, error):
		if error or data is None:
			self.trialcounter += 1
			if self.trialcounter < 2:
				print(f"[{MODULE_NAME}] lookup for city '{self.weathercity}' paused, try again in 10 secs...")
				self.setWeatherDataValid(1)
				self.refreshTimer.start(10000, True)
			elif self.trialcounter > 5:
				print(f"[{MODULE_NAME}] lookup for city '{self.weathercity}' paused 1 h, to many errors...")
				self.setWeatherDataValid(2)
				self.refreshTimer.start(3600000, True)
			else:
				print(f"[{MODULE_NAME}] lookup for city '{self.weathercity}' paused 5 mins, to many errors...")
				self.setWeatherDataValid(2)
				self.refreshTimer.start(300000, True)
			return
		self.writeData(data)
		# TODO write cache only on close
		if config.plugins.MetrixWeather.cachedata.value != "0":
			with open(CACHEFILE, "wb") as fd:
				dump(data, fd, protocol=5)

	def writeData(self, data):
		self.wetterdata = data
		skydirs = {"N": _("North"), "NE": _("Northeast"), "E": _("East"), "SE": _("Southeast"), "S": _("South"), "SW": _("Southwest"), "W": _("West"), "NW": _("Northwest")}
		windarrow = {8593: "a", 8599: "b", 8594: "c", 8600: "d", 8595: "e", 8601: "f", 8592: "g", 8598: "h"}
		YAHOOnightswitch = {
						"3": "47", "4": "47", "11": "45", "12": "45", "13": "46", "14": "46", "15": "46", "16": "46", "28": "27",
						"30": "29", "32": "31", "34": "33", "37": "47", "38": "47", "40": "45", "41": "46", "42": "46", "43": "46"
						}
		METEOnightswitch = {"1": "2", "3": "4", "B": "C", "H": "I", "J": "K"}
		if config.plugins.MetrixWeather.weatherservice.value == "openweather":
			geocode = f"{data['longitude']},{data['latitude']}"
			if geocode != self.geocode:
				config.plugins.MetrixWeather.owm_geocode.value = geocode
				config.plugins.MetrixWeather.owm_geocode.save()
			# remove old woeid settings
			if config.plugins.MetrixWeather.woeid.value != 0:
				config.plugins.MetrixWeather.woeid.value = 0
				config.plugins.MetrixWeather.woeid.save()
				config.plugins.MetrixWeather.weathercity.value = data["name"]
				config.plugins.MetrixWeather.weathercity.save()
		speedsign = "mph" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "km/h"
		tempsign = "°F" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "°C"
		now = datetime.now()
		sunrise = datetime.fromisoformat(data["current"]["sunrise"])
		sunset = datetime.fromisoformat(data["current"]["sunset"])
		isnight = now < sunrise or now > sunset
		# data for panel "infoBarWeather"
		self["Temp"].setText(f"{data['current']['temp']}")
		self["Tempsign"].setText(tempsign)
		if config.plugins.MetrixWeather.icontype.value == "0":
			iconcode = data["current"]["meteoCode"]
			if config.plugins.MetrixWeather.nighticons.value and isnight and iconcode in METEOnightswitch:
				iconcode = METEOnightswitch[iconcode]
			self["FontCode"].setText(iconcode)
			self["IconCode"].setText("")
		else:
			iconcode = data["current"]["yahooCode"]
			if config.plugins.MetrixWeather.nighticons.value and isnight and iconcode in YAHOOnightswitch:
				iconcode = YAHOOnightswitch[iconcode]
			self["IconCode"].setText(iconcode)
			self["FontCode"].setText("")
		self["ShortDay"].setText(data["current"]["shortDay"])
		# self["Shorttext"].setText(data["current"]["text"])
		self["MinTemp"].setText(f"{data['forecast'][0]['minTemp']} {tempsign}")
		self["MaxTemp"].setText(f"{data['forecast'][0]['maxTemp']} {tempsign}")
		# data for panel "infoBarWeatherDetails"
		if config.plugins.MetrixWeather.detail.value:
			logos = {"MSN": 0, "openweather": 1, "OpenMeteo": 2}
			self["logo"].setPixmapNum(logos.get(config.plugins.MetrixWeather.weatherservice.value, 0))
			self["logo"].show()
			location = data["name"]
			print(f"[{MODULE_NAME}] DEBUG writeData location = {location}")
			if len(location) > 26:  # if too long for skin, reduce stepweise
				location = location.split(",")
				location = f"{location[0]}, {location[2]}" if len(location) > 2 else location[0]
				if len(location) > 26:
					location = f"{location[:26]}…"
			if config.plugins.MetrixWeather.cityVisible.value:
				self["Location"].setText(location)  # trigger "on" for panel "infoBarWeatherDetails"
			self["Observationtime"].setText(data["current"]["observationTime"][11:19])
			self["Feelslike"].setText(f"{data['current']['feelsLike']} {tempsign}")
			self["Humidity"].setText(f"{data['current']['humidity']} %")
			skydirection = data["current"]["windDirSign"].split(" ")
			self["WindDisplay"].setText(skydirs[skydirection[1]] if skydirection[1] in skydirs else skydirection[1])
			self["WindArrow"].setText(windarrow[ord(skydirection[0])])
			self["WindSpeed"].setText(f"{data['current']['windSpeed']} {speedsign}")
		# data for panels "forecast"
		for day in range(1, self.forecast + 1):  # only user-demanded forecasts
			if config.plugins.MetrixWeather.icontype.value == "0":
				self["FontCode_%d" % day].setText(data["forecast"][day]["meteoCode"])
				self["IconCode_%d" % day].setText("")
			else:
				self["IconCode_%d" % day].setText(data["forecast"][day]["yahooCode"])
				self["FontCode_%d" % day].setText("")
			self["ShortDay_%d" % day].setText(data["forecast"][day]["shortDay"])
			self["MinTemp_%d" % day].setText(f"{data['forecast'][day]['minTemp']} {tempsign}")
			self["MaxTemp_%d" % day].setText(f"{data['forecast'][day]['maxTemp']} {tempsign}")
		self.trialcounter = 0

		iconcode = data["current"]["meteoCode"]
		if config.plugins.MetrixWeather.nighticons.value and isnight and iconcode in METEOnightswitch:
			iconcode = METEOnightswitch[iconcode]

		config.plugins.MetrixWeather.currentWeatherTemp.value = data["current"]["temp"]
		config.plugins.MetrixWeather.currentWeatherCode.value = iconcode
		config.plugins.MetrixWeather.forecastTodayTempMin.value = data["forecast"][0]["minTemp"]
		config.plugins.MetrixWeather.forecastTodayTempMax.value = data["forecast"][0]["maxTemp"]
		config.plugins.MetrixWeather.forecastTomorrowCode.value = data["forecast"][1]["meteoCode"]
		config.plugins.MetrixWeather.forecastTomorrowTempMin.value = data["forecast"][1]["minTemp"]
		config.plugins.MetrixWeather.forecastTomorrowTempMax.value = data["forecast"][1]["maxTemp"]

		self.setWeatherDataValid(0)
		seconds = int(config.plugins.MetrixWeather.refreshInterval.value * 60)
		self.refreshTimer.start(seconds * 1000, True)

	def setWeatherDataValid(self, value):
		config.plugins.MetrixWeather.currentWeatherDataValid.value = value
		if value == 0:
			InfoBarMetrixWeatherNoData.instance.hide()


class InfoBarMetrixWeatherHandler():
	def sessioninit(self, session):
		if config.plugins.MetrixWeather.enabled.value:
			session.instantiateDialog(InfoBarMetrixWeatherNoData)
			session.instantiateDialog(InfoBarMetrixWeather)
		self.session = session

	def processDisplay(self, state):
		if config.plugins.MetrixWeather.enabled.value and config.plugins.MetrixWeather.currentWeatherDataValid.value != 3:
			try:
				if config.plugins.MetrixWeather.currentWeatherDataValid.value != 0:
					if state:
						InfoBarMetrixWeatherNoData.instance.show()
					else:
						InfoBarMetrixWeatherNoData.instance.hide()
				else:
					if state:
						InfoBarMetrixWeather.instance.show()
					else:
						InfoBarMetrixWeather.instance.hide()
			except Exception:
				pass

	def hookInfoBar(self, reason, instanceInfoBar):
		if reason:
			instanceInfoBar.connectShowHideNotifier(self.processDisplay)
		else:
			instanceInfoBar.disconnectShowHideNotifier(self.processDisplay)

	def reconfigure(self):
		try:
			InfoBarMetrixWeather.instance.close()
			if isfile(CACHEFILE):
				remove(CACHEFILE)
			self.session.instantiateDialog(InfoBarMetrixWeather)
		except Exception:
			pass


def main(session, **kwargs):
	session.open(MainSettingsView)


def sessionmain(reason, session, **kwargs):
	if reason == 0:
		infobarmetrixweatherhandler.sessioninit(session)


def autostart(reason, **kwargs):
	if reason == 0:
		applySkinSettings(fullInit=True)


def info(reason, session, **kwargs):
	typeInfoBar = kwargs["typeInfoBar"]
	if config.plugins.MetrixWeather.enabled.value:
		if typeInfoBar == "InfoBar" or (config.plugins.MetrixWeather.MoviePlayer.value and typeInfoBar in ("MoviePlayer", "EMCMediaCenter")):
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
