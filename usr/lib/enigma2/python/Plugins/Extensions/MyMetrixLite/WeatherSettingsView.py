# -*- coding: UTF-8 -*-
#######################################################################
#
#    MyMetrixLite by arn354 & svox
#    based on
#    MyMetrix
#    Coded by iMaxxx (c) 2013
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

from . import _, initWeatherConfig, MAIN_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from enigma import ePicLoad, eTimer
from os import path
from Components.Renderer.MetrixHDWeatherUpdaterStandalone import MetrixHDWeatherUpdaterStandalone

#############################################################

class WeatherSettingsView(ConfigListScreen, Screen):
	skin = """
	<screen name="MyMetrixLiteWeatherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
	<widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
	<widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
	<widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="saveBtn" position="257,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="defaultsBtn" position="445,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="checkBtn" position="631,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
	<eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
	<eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
	<eLabel position="616,635" size="5,40" backgroundColor="#000064c7" />
	<ePixmap position="838,100" size="258,58" zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/MyMetrixLiteWeatherLogo.png" alphatest="blend" />
	<widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
	<widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
	<widget name="resulttext" position="61,430" size="590,200" font="Regular; 20" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" transparent="1"/>
	</screen>
"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["helpertext"] = Label()
		self["resulttext"] = Label()

		self["titleText"] = StaticText("")
		self["titleText"].setText(_("Weather settings"))

		self["cancelBtn"] = StaticText("")
		self["cancelBtn"].setText(_("Cancel"))

		self["saveBtn"] = StaticText("")
		self["saveBtn"].setText(_("Save"))

		self["defaultsBtn"] = StaticText("")
		self["defaultsBtn"].setText(_("Defaults"))

		self["checkBtn"] = StaticText("")
		self["checkBtn"].setText(_("Check ID"))

		self.check_enable = False
		self.checkTimer = eTimer()
		self.checkTimer.callback.append(self.readCheckFile)

		initWeatherConfig()

		ConfigListScreen.__init__(
			self,
			self.getMenuItemList(),
			session = session,
			on_change = self.__changedEntry
		)

		self["actions"] = ActionMap(
		[
			"OkCancelActions",
			"DirectionActions",
			"InputActions",
			"ColorActions"
		],
		{
			"left": self.keyLeft,
			"down": self.keyDown,
			"up": self.keyUp,
			"right": self.keyRight,
			"red": self.exit,
			"green": self.save,
			"yellow": self.__defaults,
			"blue": self.checkID,
			"cancel": self.exit
		}, -1)

		self.onLayoutFinish.append(self.UpdatePicture)

	def getMenuItemList(self):
		list = []

		list.append(getConfigListEntry(_("Enabled"), config.plugins.MetrixWeather.enabled, _("Cycle/failure indicator colors on widget:\ngreen - 6 times try to fetch weather data\nyellow - fetch weather data paused 5 mins\nred - fetch weather data aborted after 6 times green and yellow\n(if red -> press 'save' for refresh)"), "ENABLED"))

		self["resulttext"].setText("")
		self.check_enable = False
		if config.plugins.MetrixWeather.enabled.getValue() is True:
			list.append(getConfigListEntry(_("Show in MoviePlayer"), config.plugins.MetrixWeather.MoviePlayer, _("helptext")))
			list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid , _("Get your local MetrixWeather ID from www.mymetrix.de")))
			list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit, _("helptext")))
			list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval, _("If set to '0', fetch weather data only at system(gui) start.")))
			list.append(getConfigListEntry(_("Check is Weather date local date"), config.plugins.MetrixWeather.verifyDate, _("helptext")))
			self.check_enable = True
		return list

	def GetPicturePath(self):
		return MAIN_IMAGE_PATH % "MyMetrixLiteWeather"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
		self.PicLoad.startDecode(self.GetPicturePath())
		self.showHelperText()

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		#self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		#self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def readCheckFile(self):
		try:
			f = open('/tmp/weathercheck.txt', 'r')
			text = f.read()
			f.close()
		except Exception as error:
			text = _("Get weather data failure:\n%s") %str(error)

		if not "MetrixHDWeatherStandalone lookup for ID" in text:
			tmp = text.split('|')
			if tmp and len(tmp) > 2:
				text = _("Current weather data:   %s\n") %tmp[0]
				text += _("City:   %s,   ") %tmp[1]
				text += _("Temperature:   %s") %tmp[2]
				if config.plugins.MetrixWeather.verifyDate.value and len(tmp) > 3:
					text += _(",   Date is valid:   %s") %[_("No"),_("Yes")][int(tmp[3])]
			elif tmp and len(tmp) > 1:
				text = _("Cant get weather data:\n%s") %tmp[0]

			self["resulttext"].setText(text)
			self.checkTimer.stop()

	def checkID(self):
		if self.checkTimer.isActive() or not self.check_enable:
			return
		self["resulttext"].setText(_("Please wait, get weather data ..."))
		MetrixHDWeatherUpdaterStandalone(check=True)
		self.checkTimer.start(3000,False)

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()

		configfile.save()
		MetrixHDWeatherUpdaterStandalone(once=True)
		self.exit()

	def defaults(self):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				x[1].save()
		configfile.save()

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

	def __defaults(self):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
		self["config"].setList(self.getMenuItemList())
		self.ShowPicture()
		#self.save()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
		self.close()

	def __changedEntry(self):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == "ENABLED":
			self["config"].setList(self.getMenuItemList())

	def showHelperText(self):
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")
