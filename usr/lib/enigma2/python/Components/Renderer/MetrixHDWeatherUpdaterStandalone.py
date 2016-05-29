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
        self.verify = config.plugins.MetrixWeather.verifyDate.value #check for valid date
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

    def getWeatherThread(self):
        global g_updateRunning
        text = "MetrixHDWeatherStandalone lookup for ID " + str(self.woeid)
        if self.check:
            self.writeCheckFile(text)
        print text

        url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(self.woeid)+"%22&format=xml"
        #url = "http://query.yahooapis.com/v1/public/yql?q=select%20item%20from%20weather.forecast%20where%20woeid%3D%22"+str(self.woeid)+"%22%20u%3Dc&format=xml"

        # where location in (select id from weather.search where query="oslo, norway")
        try:
            file = urllib2.urlopen(url, timeout=2)
            data = file.read()
            file.close()
        except Exception as error:
            print "Cant get weather data: %r" % error
            g_updateRunning = False
            self.startTimer(True,30)
            if self.check:
                text = "%s|" % str(error)
                self.writeCheckFile(text)
            return

        dom = parseString(data)
        try:
            title = self.getText(dom.getElementsByTagName('title')[0].childNodes)
        except IndexError as error:
            print "Cant get weather data: %r" % error
            g_updateRunning = False
            self.startTimer(True,30)
            if self.check:
                #text = "%s\n%s|" % (str(error),data)
                text = "%s|" % str(error)
                self.writeCheckFile(text)
            return

        if 'not found' in title:
            print "MetrixHDWeatherStandalone lookup for ID - " + title
            g_updateRunning = False
            self.startTimer(True,30)
            if self.check:
                text = "%s|" % title
                self.writeCheckFile(text)
            return
        city = str(title).split(',')[0].replace("Conditions for ","")
        currentWeather = dom.getElementsByTagName('yweather:condition')[0]
        currentWeatherDate = currentWeather.getAttributeNode('date').nodeValue
        currentWeatherCode = currentWeather.getAttributeNode('code')
        currentWeatherTemp = currentWeather.getAttributeNode('temp')
        currentWeatherText = currentWeather.getAttributeNode('text')

        #check returned date from weather values
        datevalid = True
        if self.verify:
            t=time()
            l=t-3600*24
            month = ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
            lastday = strftime("%d " + month[int(strftime('%m',localtime(l)))] + " %Y", localtime(l)).strip("0")
            currday = strftime("%d " + month[int(strftime('%m',localtime(t)))] + " %Y", localtime(t)).strip("0")
            if not (currday in currentWeatherDate or lastday in currentWeatherDate):
                datevalid = False

        if self.check:
            text = "%s|%s|%s°%s|%s" %(currentWeatherDate,city,self.getTemp(currentWeatherTemp.nodeValue),config.plugins.MetrixWeather.tempUnit.value[0],int(datevalid))
            self.writeCheckFile(text)
            g_updateRunning = False
            return

        if not datevalid:
            #print "MetrixHDWeatherStandalone - get weather data failed. (current date = %s, returned date = %s)" %(currday, currentWeatherDate)
            g_updateRunning = False
            self.startTimer(True,15)
            return
        #print "MetrixHDWeatherStandalone - get weather data successful. (current date = %s, returned date = %s)" %(currday, currentWeatherDate)

        config.plugins.MetrixWeather.currentLocation.value = city
        config.plugins.MetrixWeather.currentWeatherDataValid.value = 3
        config.plugins.MetrixWeather.currentWeatherCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        config.plugins.MetrixWeather.currentWeatherTemp.value = self.getTemp(currentWeatherTemp.nodeValue)
        config.plugins.MetrixWeather.currentWeatherText.value = currentWeatherText.nodeValue

        n = 0
        currentWeather = dom.getElementsByTagName('yweather:forecast')[n]
        if self.verify:
            if lastday in currentWeather.getAttributeNode('date').nodeValue and currday in currentWeatherDate:
                n = 1
                currentWeather = dom.getElementsByTagName('yweather:forecast')[n]
        currentWeatherCode = currentWeather.getAttributeNode('code')
        config.plugins.MetrixWeather.forecastTodayCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('high')
        config.plugins.MetrixWeather.forecastTodayTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('low')
        config.plugins.MetrixWeather.forecastTodayTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherText = currentWeather.getAttributeNode('text')
        config.plugins.MetrixWeather.forecastTodayText.value = currentWeatherText.nodeValue

        currentWeather = dom.getElementsByTagName('yweather:forecast')[n + 1]
        currentWeatherCode = currentWeather.getAttributeNode('code')
        config.plugins.MetrixWeather.forecastTomorrowCode.value = self.ConvertCondition(currentWeatherCode.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('high')
        config.plugins.MetrixWeather.forecastTomorrowTempMax.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherTemp = currentWeather.getAttributeNode('low')
        config.plugins.MetrixWeather.forecastTomorrowTempMin.value = self.getTemp(currentWeatherTemp.nodeValue)
        currentWeatherText = currentWeather.getAttributeNode('text')
        config.plugins.MetrixWeather.forecastTomorrowText.value = currentWeatherText.nodeValue

        config.plugins.MetrixWeather.save()
        g_updateRunning = False
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
