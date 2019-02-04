#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#######################################################################
#
#    MetrixMODWeather for openTV
#    Coded by iMaxxx (c) 2013
#    changes by openATV Team
#    MSN Part from nikolasi
#
#
#######################################################################

from Renderer import Renderer
from Components.VariableText import VariableText
#import library to do http requests:
from urllib2 import Request, URLError, HTTPError, urlopen as urlopen2, quote as urllib2_quote, unquote as urllib2_unquote
from enigma import eLabel
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
from Components.config import config, configfile
from Plugins.Extensions.MyMetrixLite.__init__ import initWeatherConfig
from threading import Timer, Thread
from time import time, strftime, localtime
from twisted.web.client import getPage
from datetime import datetime, timedelta

import sys
#from twisted.python import log
#log.startLogging(sys.stdout)

import json

g_updateRunning = False
g_isRunning = False

std_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.53.11 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10',
 'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.7',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3'}

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
					if config.plugins.MetrixWeather.weatherservice.value == "MSN":
						print "MetrixHDWeatherStandalone lookup for City " + str(self.cityname) + " paused 5 mins, to many errors ..."
					else:
						print "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid) + " paused 5 mins, to many errors ..."
					seconds = 300
				else:
					if config.plugins.MetrixWeather.weatherservice.value == "MSN":
						print "MetrixHDWeatherStandalone lookup for City " + str(self.cityname) + " aborted, to many errors ..."
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
		if val == 3:
			config.plugins.MetrixWeather.save()
			self.refreshcnt = 0
			self.refreshcle = 0

	def getWeather(self):
		global g_updateRunning, g_isRunning

		# skip if weather-widget is disabled
		if config.plugins.MetrixWeather.enabled.getValue() is False:
			return

		self.woeid = config.plugins.MetrixWeather.woeid.value
		self.cityname = config.plugins.MetrixWeather.weathercity.value
		#self.verify = config.plugins.MetrixWeather.verifyDate.value #check for valid date
		self.startTimer()

		valdata = config.plugins.MetrixWeather.currentWeatherDataValid.value
		if ((valdata == 3 and (self.refreshcnt or self.refreshcle)) or (not int(config.plugins.MetrixWeather.refreshInterval.value) and valdata == 3) or valdata == 2) and not self.once and not self.check:
			return

		if g_updateRunning:
			if config.plugins.MetrixWeather.weatherservice.value == "MSN":
				print "MetrixHDWeatherStandalone lookup for City " + str(self.cityname) + " skipped, allready running..."
			else:
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
		print "MetrixHDWeatherStandalone get weather data failed - Error code: %s" %errormessage
		if self.check:
			self.writeCheckFile(errormessage)
		else:
			nextcall = 30
			if not self.once:
				print "MetrixHDWeatherStandalone try next in %d sec ..." %nextcall
			self.startTimer(True, nextcall)

	def getWeatherThread(self):
		global g_updateRunning
		id = ""
		name = ""
		temp = ""
		temp_max = ""
		temp_min = ""
		if config.plugins.MetrixWeather.weatherservice.value == "MSN":
			text = "MetrixHDWeatherStandalone lookup for City " + str(self.cityname)
		else:
			text = "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid)
		if self.check:
			self.writeCheckFile(text)
		print text

		if config.plugins.MetrixWeather.weatherservice.value == "MSN":
			units = 'C'
			if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit":
				units ='F'
			language = config.osd.language.value.replace('_', '-')
			if language == 'en-EN':
				language = 'en-US'
			city="%s" % self.cityname
			feedurl = "http://weather.service.msn.com/data.aspx?weadegreetype=%s&culture=%s&weasearchstr=%s&src=outlook" % (units,language,urllib2_quote(city))
			msnrequest = Request(feedurl, None, std_headers)
			try:
				msnpage = urlopen2(msnrequest)
			except (URLError) as err:
				self.errorCallback(message = str(err))
				return
			g_updateRunning = False
			try:
				content = msnpage.read()
				msnpage.close()
				dom = parseString(content)
				currentWeather = dom.getElementsByTagName('weather')[0]
				titlemy = currentWeather.getAttributeNode('weatherlocationname')
				config.plugins.MetrixWeather.currentLocation.value = titlemy.nodeValue
				name = titlemy.nodeValue
				idmy =  currentWeather.getAttributeNode('weatherlocationcode')
				id = idmy.nodeValue
				currentWeather = dom.getElementsByTagName('current')[0]
				currentWeatherCode = currentWeather.getAttributeNode('skycode')
				config.plugins.MetrixWeather.currentWeatherCode.value = self.ConvertConditionMSN(currentWeatherCode.nodeValue)
				currentWeatherTemp = currentWeather.getAttributeNode('temperature')
				temp = currentWeatherTemp.nodeValue
				config.plugins.MetrixWeather.currentWeatherTemp.value = currentWeatherTemp.nodeValue
				currentWeatherText = currentWeather.getAttributeNode('skytext')
				config.plugins.MetrixWeather.currentWeatherText.value = currentWeatherText.nodeValue
				n = 1
				currentWeather = dom.getElementsByTagName('forecast')[n]
				currentWeatherCode = currentWeather.getAttributeNode('skycodeday')
				config.plugins.MetrixWeather.forecastTodayCode.value = self.ConvertConditionMSN(currentWeatherCode.nodeValue)
				currentWeatherTemp = currentWeather.getAttributeNode('high')
				temp_max  = currentWeatherTemp.nodeValue
				config.plugins.MetrixWeather.forecastTodayTempMax.value = currentWeatherTemp.nodeValue
				currentWeatherTemp = currentWeather.getAttributeNode('low')
				temp_min = currentWeatherTemp.nodeValue
				config.plugins.MetrixWeather.forecastTodayTempMin.value = currentWeatherTemp.nodeValue
				currentWeatherText = currentWeather.getAttributeNode('skytextday')
				config.plugins.MetrixWeather.forecastTodayText.value = currentWeatherText.nodeValue
				currentWeather = dom.getElementsByTagName('forecast')[n + 1]
				currentWeatherCode = currentWeather.getAttributeNode('skycodeday')
				config.plugins.MetrixWeather.forecastTomorrowCode.value = self.ConvertConditionMSN(currentWeatherCode.nodeValue)
				currentWeatherTemp = currentWeather.getAttributeNode('high')
				config.plugins.MetrixWeather.forecastTomorrowTempMax.value = currentWeatherTemp.nodeValue
				currentWeatherTemp = currentWeather.getAttributeNode('low')
				config.plugins.MetrixWeather.forecastTomorrowTempMin.value = currentWeatherTemp.nodeValue
				currentWeatherText = currentWeather.getAttributeNode('skytextday')
				config.plugins.MetrixWeather.forecastTomorrowText.value = currentWeatherText.nodeValue
				if self.check:
					text = "%s|%s|%s°|%s°|%s°" %(id,name,temp,temp_max,temp_min)
					self.writeCheckFile(text)
					return
			except IndexError, err:
				self.errorCallback(message = str(err))
				return
			self.setWeatherDataValid(3)
		else:
			units = 'metric'
			if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit":
				units ='imperial'
			language = config.osd.language.value
			apikey = "&appid=%s" % config.plugins.MetrixWeather.apikey.value
			city="id=%s" % self.woeid
			cnt = (24 + (24 - int(datetime.now().strftime('%H')))) / 3 + 1
			feedurl = "http://api.openweathermap.org/data/2.5/forecast?%s&lang=%s&units=%s&cnt=%d%s" % (city,language[:2],units,cnt,apikey)
			print feedurl
			getPage(feedurl).addCallback(self.jsonCallback).addErrback(self.errorCallback)

	def jsonCallback(self, jsonstring):
		global g_updateRunning
		d = json.loads(jsonstring)
		if 'code' in d and d['cod'] != "200":
			self.errorCallback(message = d['message'])
			return
		g_updateRunning = False
		try:
			#location
			id = str(d['city']['id'])
			name = str(d['city']['name'])
			#current
			code = d['list'][0]['weather'][0]['id']
			temp = str(int(round(d['list'][0]['main']['temp'])))
			temp_min = str(int(round(d['list'][0]['main']['temp_min'])))
			temp_max = str(int(round(d['list'][0]['main']['temp_max'])))

			tmin_today =[]
			tmax_today =[]
			tmin_tomorrow =[]
			tmax_tomorrow =[]
			now = datetime.now().strftime('%Y-%m-%d')
			tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
			code_tomorrow = tmp = ''
			for dict in d['list']:
				if now in dict['dt_txt']:
					tmin_today.append(int(round(dict['main']['temp_min'])))
					tmax_today.append(int(round(dict['main']['temp_max'])))
				elif tomorrow in dict['dt_txt']:
					if '00:00:00' in dict['dt_txt']:
						tmin_today.append(int(round(dict['main']['temp_min'])))
						tmax_today.append(int(round(dict['main']['temp_max'])))
					tmin_tomorrow.append(int(round(dict['main']['temp_min'])))
					tmax_tomorrow.append(int(round(dict['main']['temp_max'])))
					tmp = dict['weather'][0]['id']
					if '12:00:00' in dict['dt_txt']:
						code_tomorrow = tmp

			#no forecast temp data
			if not tmin_today:
				tmin_today = temp_min
			else:
				tmin_today = str(min(tmin_today))
			if not tmax_today:
				tmax_today = temp_max
			else:
				tmax_today = str(max(tmax_today))
			if not tmin_tomorrow:
				tmin_tomorrow = tmin_today
			else:
				tmin_tomorrow = str(min(tmin_tomorrow))
			if not tmax_tomorrow:
				tmax_tomorrow = tmax_today
			else:
				tmax_tomorrow = str(max(tmax_tomorrow))

			if self.check:
				text = "%s|%s|%s°|%s°|%s°" %(id,name,temp,tmax_today,tmin_today)
				self.writeCheckFile(text)
				return

			#name
			config.plugins.MetrixWeather.currentLocation.value = name
			#today
			config.plugins.MetrixWeather.currentWeatherTemp.value = temp
			config.plugins.MetrixWeather.currentWeatherCode.value = self.ConvertCondition(code)
			config.plugins.MetrixWeather.forecastTodayTempMin.value = tmin_today
			config.plugins.MetrixWeather.forecastTodayTempMax.value = tmax_today
			#tomrorrow
			if not code_tomorrow: code_tomorrow = tmp
			config.plugins.MetrixWeather.forecastTomorrowCode.value = self.ConvertCondition(code_tomorrow)
			config.plugins.MetrixWeather.forecastTomorrowTempMin.value = tmin_tomorrow
			config.plugins.MetrixWeather.forecastTomorrowTempMax.value = tmax_tomorrow
		except IndexError, err:
			self.errorCallback(message = str(err))
			return
		self.setWeatherDataValid(3)

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

	def ConvertConditionMSN(self, c):
		try:
			c = int(c)
		except:
			c = 49
		condition = "("
		if c == 0 or c == 1 or c == 2:
			condition = "S"
		elif c == 3 or c == 4:
			condition = "Z"
		elif c == 5  or c == 6 or c == 7 or c == 18:
			condition = "U"
		elif c == 8 or c == 10 or c == 25:
			condition = "G"
		elif c == 9:
			condition = "Q"
		elif c == 11 or c == 12 or c == 40:
			condition = "R"
		elif c == 13 or c == 14 or c == 15 or c == 16 or c == 41 or c == 46 or c == 42 or c == 43:
			condition = "W"
		elif c == 17 or c == 35:
			condition = "X"
		elif c == 19:
			condition = "F"
		elif c == 20 or c == 21 or c == 22:
			condition = "L"
		elif c == 23 or c == 24:
			condition = "S"
		elif c == 26 or c == 44:
			condition = "N"
		elif c == 27 or c == 29:
			condition = "I"
		elif c == 28 or c == 30:
			condition = "H"
		elif c == 31 or c == 33:
			condition = "C"
		elif c == 32 or c == 34:
			condition = "B"
		elif c == 36:
			condition = "B"
		elif c == 37 or c == 38 or c == 39 or c == 45 or c == 47:
			condition = "0"
		elif c == 49:
			condition = ")"
		else:
			condition = ")"
		return str(condition)

	def writeCheckFile(self,text):
		f = open('/tmp/weathercheck.txt', 'w')
		f.write(text)
		f.close()
