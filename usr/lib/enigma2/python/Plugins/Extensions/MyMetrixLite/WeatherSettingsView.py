# -*- coding: UTF-8 -*-
#######################################################################
#
#    MyMetrixLite by arn354 & svox
#    based on
#    MyMetrix
#    Coded by iMaxxx (c) 2013
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

from . import _, MAIN_IMAGE_PATH
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap
from urllib2 import Request, urlopen, URLError, HTTPError
from xml.etree.cElementTree import fromstring as cet_fromstring
from Tools.Directories import fileExists
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from enigma import ePicLoad, eTimer
from os import path, listdir, system
from Components.Renderer.MetrixHDWeatherUpdaterStandalone import MetrixHDWeatherUpdaterStandalone
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists

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

		ConfigListScreen.__init__(self, self.getMenuItemList(), session = session, on_change = self.changedEntry)

		self["actions"] = ActionMap(
		[
			"OkCancelActions",
			"DirectionActions",
			"InputActions",
			"ColorActions",
			"VirtualKeyboardActions"
		],
		{
			"left": self.keyLeft,
			"down": self.keyDown,
			"up": self.keyUp,
			"right": self.keyRight,
			"red": self.exit,
			"green": self.save,
			"yellow": self.defaults,
			"blue": self.checkID,
			"showVirtualKeyboard": self.checkIDmy,
			"ok": self.checkIDmy,
			"cancel": self.exit
		}, -1)
		self.onLayoutFinish.append(self.UpdatePicture)

	def getMenuItemList(self):
		list = [ ]

		list.append(getConfigListEntry(_("Enabled"), config.plugins.MetrixWeather.enabled, _("Cycle/failure indicator colors on widget:\ngreen - 6 times try to fetch weather data\nyellow - fetch weather data paused 5 mins\nred - fetch weather data aborted after 6 times green and yellow\n(if red -> press 'save' for refresh)"), "ENABLED"))
		self.check_enable = False
		norestart = _(" (no restart required)")
		if config.plugins.MetrixWeather.enabled.getValue() is True:
			list.append(getConfigListEntry(_("Show in MoviePlayer"), config.plugins.MetrixWeather.MoviePlayer, _("helptext")))

			list.append(getConfigListEntry(_("MetrixWeather Service"), config.plugins.MetrixWeather.weatherservice , _("Choose your preferred weather service"),"ENABLED"))
			if config.plugins.MetrixWeather.weatherservice.value == "MSN":
				list.append(getConfigListEntry(_("MetrixWeather City Name"), config.plugins.MetrixWeather.weathercity , _("Your place for weather determination. Press TEXT or OK to enter the city name")))
				#list.append(getConfigListEntry(_("Show '+' before temperature"), config.plugins.MetrixWeather.tempplus, _("If actively output '+' before temperature.") + norestart))
				info = ""
			else:
				list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid , _("Get your local MetrixWeather ID from https://openweathermap.org/")))
				list.append(getConfigListEntry(_("MetrixWeather APIKEY"), config.plugins.MetrixWeather.apikey , _("Get your local MetrixWeather APIKEY from https://openweathermap.org/")))
				info = _("If the file 'ID_APIKEY.apidata' exists in the '/tmp/' folder,\nimported these data automatically on '") + _("Check ID") + _("' function.\n\n(e.g. '2911298_a4bd84726035d0ce2c6185740617d8c5.apidata')")
			list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit, _("Set your preferred temperature unit.") + norestart))
			list.append(getConfigListEntry(_("MetrixWeather animatedWeather type"), config.plugins.MetrixWeather.type, _("Get your MetrixWeather AnimatedWeather."),"ENABLED"))
			if config.plugins.MetrixWeather.type.value:
				list.append(getConfigListEntry(_("MetrixWeather animations speed"),config.plugins.MetrixWeather.animationspeed, _("Set your animations speed.") + norestart))
			list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval, _("If set to '0', fetch weather data only at system(gui) start.")))
			#list.append(getConfigListEntry(_("Check is Weather date local date"), config.plugins.MetrixWeather.verifyDate, _("helptext")))
			self["resulttext"].setText(info)
			self.check_enable = True
		return list

	def GetPicturePath(self):
		picturepath = resolveFilename(SCOPE_CURRENT_SKIN, "mymetrixlite/MyMetrixLiteWeather.png")
		if not fileExists(picturepath):
			picturepath = MAIN_IMAGE_PATH % "MyMetrixLiteWeather"
		return picturepath

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

	def keyRight(self):
		ConfigListScreen.keyRight(self)

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
				text = _("Current weather id:   %s\n") %tmp[0]
				text += _("City:   %s,   ") %tmp[1]
				text += _("Temp:   %s,   ") %tmp[2]
				text += _("max:   %s,   ") %tmp[3]
				text += _("min:   %s") %tmp[4]
			elif tmp and len(tmp) > 1:
				text = _("Cant get weather id:\n%s") %tmp[0]

			self["resulttext"].setText(text)
			self.checkTimer.stop()

	def checkID(self):
		if self.checkTimer.isActive() or not self.check_enable or not self.loadAPIdata():
			return
		self["resulttext"].setText(_("Please wait, get weather data ..."))
		MetrixHDWeatherUpdaterStandalone(check=True)
		self.checkTimer.start(3000,False)

	def loadAPIdata(self):
		ret = True
		for file in listdir('/tmp/'):
			if path.isfile('/tmp/'+file) and file.endswith('.apidata'):
				try:
					id, key = file.replace('.apidata','').split('_')
				except:
					self["resulttext"].setText(_("Wrong import file ..."))
					ret = False
					break
				config.plugins.MetrixWeather.woeid.setValue(id)
				config.plugins.MetrixWeather.apikey.setValue(key)
				self["config"].setList(self.getMenuItemList())
				break
		return ret

	def checkIDmy(self):
		if self["config"].getCurrent() and self["config"].getCurrent()[0] == _("MetrixWeather City Name"):
			self.session.openWithCallback(self.ShowsearchBarracuda, VirtualKeyBoard, title=_('Enter text to search city'))

	def ShowsearchBarracuda(self, name):
		if name is not None:
			self.session.open(WeatherSettingsLocation, name)
		return

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()

		configfile.save()
		MetrixHDWeatherUpdaterStandalone(once=True)
		self.exit()

	def defaults(self, SAVE = False):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				if SAVE: x[1].save()
		if self.session:
			self["config"].setList(self.getMenuItemList())
			self.ShowPicture()

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
		self.close()

	def changedEntry(self):
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

class WeatherSettingsLocation(Screen):
	skin = """
		<screen position="center,center" size="380,80" title="%s">
		<widget name="menu" position="5,5" size="370,80" />
		</screen>""" % _('Select Your Location')

	def __init__(self, session, name):
		Screen.__init__(self, session)
		self.setTitle(_('Select Your Location'))
		self.session = session
		self.eventname = name
		self.resultlist = []
		self['menu'] = MenuList(self.resultlist)
		self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions'], {'ok': self.okClicked,
			'cancel': self.close,
			'up': self.pageUp,
			'down': self.pageDown}, -1)
		self.showMenu()

	def pageUp(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveUp)

	def pageDown(self):
		self['menu'].instance.moveSelection(self['menu'].instance.moveDown)

	def showMenu(self):
		try:
			results = search_title(self.eventname)
		except:
			results = []

		if len(results) == 0:
			return False
		self.resultlist = []
		for searchResult in results:
			try:
				self.resultlist.append(searchResult)
			except:
				pass

		self['menu'].l.setList(self.resultlist)

	def okClicked(self):
		id = self['menu'].getCurrent()
		if id:
			config.plugins.MetrixWeather.weathercity.value = id.replace(', ', ',')
			config.plugins.MetrixWeather.weathercity.save()
			if fileExists('/tmp/weathermsn.xml'):
				system('rm /tmp/weathermsn.xml')
			self.close()

def search_title(id):
	url = 'http://weather.service.msn.com/find.aspx?outputview=search&weasearchstr=%s&culture=en-US&src=outlook' % id
	msnrequest = Request(url)
	try:
		msnpage = urlopen(msnrequest)
	except (URLError) as err:
		print '[WeatherSettingsView] Error: Unable to retrieve page - Error code: ', str(err)
		return "error"

	content = msnpage.read()
	msnpage.close()
	root = cet_fromstring(content)
	search_results = []
	if content:
		for childs in root:
			if childs.tag == 'weather':
				locationcode = childs.attrib.get('weatherlocationname').encode('utf-8', 'ignore')
				search_results.append(locationcode)
	return search_results
