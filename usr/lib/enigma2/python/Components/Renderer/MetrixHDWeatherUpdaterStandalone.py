#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MetrixMODWeather for VU+
#    Coded by iMaxxx (c) 2013
#    Support: www.vuplus-support.com
#
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#  or send a letter to Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially
#  distributed other than under the conditions noted above.
#
#
#######################################################################

from Renderer import Renderer
from Components.VariableText import VariableText
#import library to do http requests:
import urllib2
from enigma import eLabel
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
from Components.config import config, configfile
from Plugins.Extensions.MyMetrixLite.__init__ import initWeatherConfig
from threading import Timer, Thread
from time import time, strftime, localtime
from twisted.web.client import getPage
import sys
#from twisted.python import log
#log.startLogging(sys.stdout)

import json


g_updateRunning = False
g_isRunning = False

initWeatherConfig()

class MetrixHDWeatherUpdaterStandalone(Renderer, VariableText):

	def __init__(self, once=False, check=False):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.once = once
		self.check = check
		self.timer = None
		self.refreshcnt = 0
		self.refreshcle = 0
		if not g_isRunning or self.once or self.check:
			self.getWeather()

	GUI_WIDGET = eLabel

	def __del__(self):
		try:
			if self.timer is not None:
				self.timer.cancel()
		except AttributeError:
			pass

	def startTimer(self, refresh=False, refreshtime=None):
		if not g_isRunning:
			self.setWeatherDataValid(0)
		if self.once or self.check:
			if self.once and refresh:
				self.setWeatherDataValid(2)
			return

		seconds = interval = int(config.plugins.MetrixWeather.refreshInterval.value) * 60
		if seconds > 1800:
			pausetime = seconds
		else:
			pausetime = 1800
		if not seconds:
			seconds = pausetime
		if refreshtime:
			seconds = refreshtime

		if refresh:
			datavalid = 0
			self.refreshcnt += 1
			if self.refreshcnt >= 6:
				self.refreshcnt = 0
				self.refreshcle += 1
				if interval:
					datavalid = 1
				else:
					datavalid = 2
				if self.refreshcle >= 6:
					datavalid = 2
				if datavalid == 1:
					print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " paused 5 mins, to many errors ..."
					seconds = 300
				else:
					print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " aborted, to many errors ..."
					seconds = pausetime

			self.setWeatherDataValid(datavalid)

		if self.timer:
			self.timer.cancel()
			#self.timer = None

		self.timer = Timer(seconds, self.getWeather)
		self.timer.start()

	def onShow(self):
		self.text = config.plugins.MetrixWeather.currentWeatherCode.value

	def setWeatherDataValid(self, val):
		config.plugins.MetrixWeather.currentWeatherDataValid.value = val # 0 = try to getting weather data, 1 = try to getting weather data paused, 2 = try to getting weather data aborted (to many error cycles), 3 = weather data valid
		config.plugins.MetrixWeather.currentWeatherDataValid.save()

	def getWeather(self):
		global g_updateRunning, g_isRunning

		# skip if weather-widget is disabled
		if config.plugins.MetrixWeather.enabled.getValue() is False:
			return

		self.woeid = config.plugins.MetrixWeather.woeid.value
		#self.verify = config.plugins.MetrixWeather.verifyDate.value #check for valid date
		self.startTimer()

		valdata = config.plugins.MetrixWeather.currentWeatherDataValid.value
		if ((valdata == 3 and (self.refreshcnt or self.refreshcle)) or (not int(config.plugins.MetrixWeather.refreshInterval.value) and valdata == 3) or valdata == 2) and not self.once and not self.check:
			return

		if g_updateRunning:
			print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " skipped, allready running..."
			return
		g_updateRunning = True
		g_isRunning = True
		Thread(target = self.getWeatherThread).start()

	def errorCallback(self, error = None, message = None):
		global g_updateRunning
		g_updateRunning = False
		errormessage = "unknown error"
		if error is not None:
			errormessage = str(error.getErrorMessage())
		elif message is not None:
			errormessage = str(message)
		print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " failed, error: %s" %errormessage
		if self.check:
			self.writeCheckFile(errormessage)
		else:
			nextcall = 30
			if not self.once:
				print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " failed, try next in %ds ..." %nextcall
			self.startTimer(True, nextcall)

	def getWeatherThread(self):
		text = "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid)
		if self.check:
			self.writeCheckFile(text)
		print text

		language = config.osd.language.value
		apikey = "&appid=%s" % config.plugins.MetrixWeather.apikey.value
		city="id=%s" % self.woeid
		feedurl = "http://api.openweathermap.org/data/2.5/forecast?%s&lang=%s&units=metric&cnt=1%s" % (city,language[:2],apikey)
		if self.check:
			feedurl = "http://api.openweathermap.org/data/2.5/weather?%s&lang=%s&units=metric%s" % (city,language[:2],apikey)
		#print feedurl
		getPage(feedurl).addCallback(self.jsonCallback).addErrback(self.errorCallback)

	def jsonCallback(self, jsonstring):
		global g_updateRunning
		g_updateRunning = False
		d = json.loads(jsonstring)
		if 'list' in d and 'cnt' in d:
			temp_min_cnt_0 = d['list'][0]['main']['temp_min']
			temp_max_cnt_0 = d['list'][0]['main']['temp_max']
			weather_code_cnt_0 = d['list'][0]['weather'][0]['id']
			config.plugins.MetrixWeather.forecastTomorrowTempMax.value = str(int(round(temp_max_cnt_0)))
			config.plugins.MetrixWeather.forecastTomorrowTempMin.value = str(int(round(temp_min_cnt_0)))
			config.plugins.MetrixWeather.forecastTomorrowCode.value = self.ConvertCondition(weather_code_cnt_0)
		elif 'message' in d:
			if self.check:
				text = d['message']
				self.writeCheckFile(text)
			else:
				self.errorCallback(message = d['message'])
			return
		else:
			if 'name' in d:
				name = d['name']
				config.plugins.MetrixWeather.currentLocation.value = str(name)
			if 'id' in d:
				id = d['id']
			if 'main' in d and 'temp' in d['main']:
				temp = d['main']['temp']
				config.plugins.MetrixWeather.currentWeatherTemp.value = str(int(round(temp)))
			if 'temp_max' in d['main']:
				temp_max = d['main']['temp_max']
				config.plugins.MetrixWeather.forecastTodayTempMax.value = str(int(round(temp_max)))
			if 'temp_min' in d['main']:
				temp_min = d['main']['temp_min']
				config.plugins.MetrixWeather.forecastTodayTempMin.value = str(int(round(temp_min)))
			if 'weather' in d:
				weather_code = d['weather'][0]['id']
				config.plugins.MetrixWeather.currentWeatherCode.value = self.ConvertCondition(weather_code)
			if self.check:
				text = "%s|%s|%s°|%s°|%s°" %(id,name,temp,temp_max,temp_min)
				self.writeCheckFile(text)
				return
		self.setWeatherDataValid(3)
		config.plugins.MetrixWeather.save()
		self.refreshcnt = 0
		self.refreshcle = 0

	def getText(self,nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		return ''.join(rc)

	def ConvertCondition(self, c):
		c = int(c)
		if c == 800:
			condition = "B" # Sonne am Tag 
		elif c == 801:
			condition = "H" # Bewoelkt Sonning 
		elif c == 802:
			condition = "J" # Nebel Sonning
		elif c == 711 or c == 721:
			condition = "L" # Bewoelkt Nebeling
		elif c == 701 or c == 731 or c == 741 or c == 751 or c == 761 or c == 762:
			condition = "M" # Nebel
		elif c == 803 or c == 804:
			condition = "N" # Bewoelkt
		elif c == 202 or c == 202 or c == 212 or c == 221:
			condition = "O" # Gewitter
		elif c == 200 or c == 200 or c == 210 or c == 230 or c == 231 or c == 232:
			condition = "P " # Gewitter leicht
		elif c == 500 or  c == 501:
			condition = "Q" # Leicher Regen
		elif c == 520 or c == 521 or c == 531 or c == 300 or c == 301 or c == 302 or c == 310 or c == 311 or c == 312 or c == 313 or c == 314 or c == 321:
			condition = "R" # Mittlere Regen
		elif c == 771 or c == 781:
			condition = "S" # Starker Wind
		elif c == 502:
			condition = "T" # Wind und Regen
		elif c == 531 or c == 531:
			condition = "U" # Normaler Regen
		elif c == 600 or c == 601 or c == 616 or c == 620:
			condition = "V" # Schnee
		elif c == 611 or c == 612 or c == 615:
			condition = "W" # Schnee gefahr
		elif c == 602 or c == 622 or c == 621 or c == 511:
			condition = "X" # Starker Schnee
		elif c == 504 or c == 503:
			condition = "Y" # Stark Regen
		elif c == 803 or c == 804:
			condition = "Y" # Stark Bewoelkt
		else:
			condition = ")"
		return str(condition)

	def getTemp(self,temp):
		if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit":
			return str(int(round(float(temp),0)))
		else:
			celsius = (float(temp) - 32 ) * 5 / 9
			return str(int(round(float(celsius),0)))

	def writeCheckFile(self,text):
		f = open('/tmp/weathercheck.txt', 'w')
		f.write(text)
		f.close()
