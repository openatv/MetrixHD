#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MetrixWeather for Enigma2
#    Coded by iMaxxx (c) 2013
#    Support: www.vuplus-support.com
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################
from Components.Converter.Converter import Converter
from Components.config import config, ConfigText, ConfigNumber, ConfigDateTime
from Components.Element import cached
from Poll import Poll

class MetrixHDWeather(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
		Poll.__init__(self)
		self.poll_interval = 60000
		self.poll_enabled = True

	@cached
	def getText(self):
		try:
			if self.type == "currentLocation":
				return config.plugins.MetrixWeather.currentLocation.value
			elif self.type == "currentWeatherTemp":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.currentWeatherTemp.value.startswith("-") or config.plugins.MetrixWeather.currentWeatherTemp.value.startswith("0"):
						return config.plugins.MetrixWeather.currentWeatherTemp.value
					else:
						return "+" + config.plugins.MetrixWeather.currentWeatherTemp.value
				else:
					return config.plugins.MetrixWeather.currentWeatherTemp.value
			elif self.type == "currentWeatherTempgetCF":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.currentWeatherTemp.value.startswith("-") or config.plugins.MetrixWeather.currentWeatherTemp.value.startswith("0"):
						return config.plugins.MetrixWeather.currentWeatherTemp.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.currentWeatherTemp.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.currentWeatherTemp.value + " " + self.getCF()
			elif self.type == "currentWeatherText":
				return config.plugins.MetrixWeather.currentWeatherText.value
			elif self.type == "currentWeatherTempheigh_low":
				if config.plugins.MetrixWeather.tempplus.value:
					tempmax = "" 
					templov = ""
					if config.plugins.MetrixWeather.forecastTodayTempMax.value.startswith("-") or config.plugins.MetrixWeather.forecastTodayTempMax.value.startswith("0"):
						tempmax = config.plugins.MetrixWeather.forecastTodayTempMax.value 
					else:
						tempmax = "+" + config.plugins.MetrixWeather.forecastTodayTempMax.value
					if config.plugins.MetrixWeather.forecastTodayTempMin.value.startswith("-") or config.plugins.MetrixWeather.forecastTodayTempMin.value.startswith("0"):
						templov = config.plugins.MetrixWeather.forecastTodayTempMin.value 
					else:
						templov = "+" + config.plugins.MetrixWeather.forecastTodayTempMin.value
						return tempmax + " " + self.getCF() + " - " + templov + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTodayTempMax.value + " " + self.getCF() + " - " + config.plugins.MetrixWeather.forecastTodayTempMin.value + " " + self.getCF()
			elif self.type == "currentWeatherCode":
				return config.plugins.MetrixWeather.currentWeatherCode.value
			elif self.type == "currenthumidity":
				return config.plugins.MetrixWeather.currentWeatherhumidity.value
			elif self.type == "currentwinddisplay":
				return config.plugins.MetrixWeather.currentWeatherwinddisplay.value
			elif self.type == "currentwindspeed":
				return config.plugins.MetrixWeather.currentWeatherwindspeed.value
			elif self.type == "currentshortday":
				return config.plugins.MetrixWeather.currentWeathershortday.value
			elif self.type == "currenthdate":
				return config.plugins.MetrixWeather.currentWeatherdate.value
			elif self.type == "currenthday":
				return config.plugins.MetrixWeather.currentWeatherday.value
			elif self.type == "currentfeelslike":
				return config.plugins.MetrixWeather.currentWeatherfeelslike.value + " " + self.getCF()
			elif self.type == "currentobservationtime":
				return config.plugins.MetrixWeather.currentWeatherobservationtime.value
			elif self.type == "forecastTodayCode":
				return config.plugins.MetrixWeather.forecastTodayCode.value
			elif self.type == "forecastTodayTempMin":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTodayTempMin.value.startswith("-") or config.plugins.MetrixWeather.forecastTodayTempMin.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTodayTempMin.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTodayTempMin.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTodayTempMin.value + " " + self.getCF()
			elif self.type == "forecastTodayTempMax":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTodayTempMax.value.startswith("-") or config.plugins.MetrixWeather.forecastTodayTempMax.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTodayTempMax.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTodayTempMax.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTodayTempMax.value + " " + self.getCF()
			elif self.type == "forecastTodayText":
				return config.plugins.MetrixWeather.forecastTodayText.value
			elif self.type == "forecastTomorrowCode":
				return config.plugins.MetrixWeather.forecastTomorrowCode.value
			elif self.type == "forecastTomorrowdate":
				return config.plugins.MetrixWeather.forecastTomorrowdate.value
			elif self.type == "forecastTomorrowday":
				return config.plugins.MetrixWeather.forecastTomorrowday.value
			elif self.type == "forecastTomorrowshortday":
				return config.plugins.MetrixWeather.forecastTomorrowshortday.value
			elif self.type == "forecastTomorrowTempMin":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMin.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMin.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMin.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMin.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMin.value + " " + self.getCF()
			elif self.type == "forecastTomorrowTempMax":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMax.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMax.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMax.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMax.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMax.value + " " + self.getCF()
			elif self.type == "forecastTomorrowText":
				return config.plugins.MetrixWeather.forecastTomorrowText.value
			elif self.type == "forecastTomorrowCode2":
				return config.plugins.MetrixWeather.forecastTomorrowCode2.value
			elif self.type == "forecastTomorrowTempMin2":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMin2.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMin2.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMin2.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMin2.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMin2.value + " " + self.getCF()
			elif self.type == "forecastTomorrowTempMax2":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMax2.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMax2.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMax2.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMax2.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMax2.value + " " + self.getCF()
			elif self.type == "forecastTomorrowText2":
				return config.plugins.MetrixWeather.forecastTomorrowText2.value
			elif self.type == "forecastTomorrowdate2":
				return config.plugins.MetrixWeather.forecastTomorrowdate2.value
			elif self.type == "forecastTomorrowday2":
				return config.plugins.MetrixWeather.forecastTomorrowday2.value
			elif self.type == "forecastTomorrowshortday2":
				return config.plugins.MetrixWeather.forecastTomorrowshortday2.value
			elif self.type == "forecastTomorrowCode3":
				return config.plugins.MetrixWeather.forecastTomorrowCode3.value
			elif self.type == "forecastTomorrowTempMin3":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMin3.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMin3.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMin3.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMin3.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMin3.value + " " + self.getCF()
			elif self.type == "forecastTomorrowTempMax3":
				if config.plugins.MetrixWeather.tempplus.value:
					if config.plugins.MetrixWeather.forecastTomorrowTempMax3.value.startswith("-") or config.plugins.MetrixWeather.forecastTomorrowTempMax3.value.startswith("0"):
						return config.plugins.MetrixWeather.forecastTomorrowTempMax3.value + " " + self.getCF()
					else:
						return "+" + config.plugins.MetrixWeather.forecastTomorrowTempMax3.value + " " + self.getCF()
				else:
					return config.plugins.MetrixWeather.forecastTomorrowTempMax3.value + " " + self.getCF()
			elif self.type == "forecastTomorrowText3":
				return config.plugins.MetrixWeather.forecastTomorrowText3.value
			elif self.type == "forecastTomorrowdate3":
				return config.plugins.MetrixWeather.forecastTomorrowdate3.value
			elif self.type == "forecastTomorrowday3":
				return config.plugins.MetrixWeather.forecastTomorrowday3.value
			elif self.type == "forecastTomorrowshortday3":
				return config.plugins.MetrixWeather.forecastTomorrowshortday3.value
			elif self.type == "title":
				return self.getCF() + " | " + config.plugins.MetrixWeather.currentLocation.value
			elif self.type == "CF":
				return self.getCF() 
			else:
				return ""
		except:
			return ""

	@cached
	def getValue(self):
		if self.type == "currentDataValid":
			try:
				return config.plugins.MetrixWeather.currentWeatherDataValid.value
			except ValueError:
				return 0
		return -1

	def getCF(self):
		if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit":
			return "°F"
		else: 
			return "°C"

	value = property(getValue)
	text = property(getText)