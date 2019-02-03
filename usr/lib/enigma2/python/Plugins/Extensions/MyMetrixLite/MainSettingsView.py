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

from . import _, MAIN_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, getDesktop, eTimer
from os import path, remove
from ColorsSettingsView import ColorsSettingsView
from WeatherSettingsView import WeatherSettingsView
from OtherSettingsView import OtherSettingsView
from FontsSettingsView import FontsSettingsView
from BackupSettingsView import BackupSettingsView
from SkinpartSettingsView import SkinpartSettingsView
from ActivateSkinSettings import ActivateSkinSettings

#############################################################

class MainMenuList(MenuList):
	def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 50, enableWrapAround = True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		screenwidth = getDesktop(0).size().width()
		if screenwidth and screenwidth == 3840:
			self.l.setFont(0, gFont("Regular", int(font0*3)))
			self.l.setFont(1, gFont("Regular", int(font1*3)))
			self.l.setItemHeight(int(itemHeight*3))
		elif screenwidth and screenwidth == 1920:
			self.l.setFont(0, gFont("Regular", int(font0*1.5)))
			self.l.setFont(1, gFont("Regular", int(font1*1.5)))
			self.l.setItemHeight(int(itemHeight*1.5))
		else:
			self.l.setFont(0, gFont("Regular", font0))
			self.l.setFont(1, gFont("Regular", font1))
			self.l.setItemHeight(itemHeight)

#############################################################

def MenuEntryItem(itemDescription, key, helptext):
	res = [(itemDescription, key, helptext)]
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 3840:
		res.append(MultiContentEntryText(pos=(30, 15), size=(1320, 135), font=0, text=itemDescription, ))
	elif screenwidth and screenwidth == 1920:
		res.append(MultiContentEntryText(pos=(15, 8), size=(660, 68), font=0, text=itemDescription, ))
	else:
		res.append(MultiContentEntryText(pos=(10, 5), size=(440, 45), font=0, text=itemDescription))
	return res

#############################################################

class MainSettingsView(Screen):
	skin = """
  <screen name="MyMetrixLiteMainSettingsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
	<widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
	<widget name="menuList" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
	<widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="applyBtn" position="257,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
	<eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
	<widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
	<widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
  </screen>
"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["helpertext"] = Label()

		self["titleText"] = StaticText("")
		self["titleText"].setText(_("MyMetrixLite"))

		self["cancelBtn"] = StaticText("")
		self["cancelBtn"].setText(_("Cancel"))

		self["applyBtn"] = StaticText("")
		self["applyBtn"].setText(_("Apply changes"))

		ActivateSkinSettings().initConfigs()

		self["actions"] = ActionMap(
			[
				"OkCancelActions",
				"DirectionActions",
				"InputActions",
				"ColorActions"
			],
			{
				"ok": self.ok,
				"red": self.exit,
				"green": self.applyChanges,
				"cancel": self.exit
			}, -1)

		list = []
		list.append(MenuEntryItem(_("Font settings"), "FONT", _("helptext")))
		list.append(MenuEntryItem(_("Color settings"), "COLOR", _("helptext")))
		list.append(MenuEntryItem(_("Weather settings"), "WEATHER", _("Powered by\n-----------------\nmsn weather\n(https://www.msn.com)\nand\nOpenWeatherMap\n(https://openweathermap.org)")))
		list.append(MenuEntryItem(_("Other settings"), "OTHER", _("helptext")))
		if path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/DesignSettings.py"):
			from DesignSettingsView import DesignSettingsView
			list.append(MenuEntryItem(_("Design settings"), "DESIGN", _("helptext")))
		list.append(MenuEntryItem(_("Skinpart settings"), "SKINPART", _("helptext")))
		list.append("")
		list.append(MenuEntryItem(_("Backup & Restore my settings"), "BACKUP", _("helptext")))

		self["menuList"] = MainMenuList([], font0=24, font1=16, itemHeight=50)
		self["menuList"].l.setList(list)

		if not self.selectionChanged in self["menuList"].onSelectionChanged:
			self["menuList"].onSelectionChanged.append(self.selectionChanged)

		self.onChangedEntry = []
		self.onLayoutFinish.append(self.UpdatePicture)

		self.checkEHDsettingsTimer = eTimer()
		self.checkEHDsettingsTimer.callback.append(self.checkEHDsettings)
		self.checkEHDsettingsTimer.start(1000, True)

	#def __del__(self):
	#	self["menuList"].onSelectionChanged.remove(self.selectionChanged)

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		if self["helperimage"] is None or self["helperimage"].instance is None:
			return

		cur = self["menuList"].getCurrent()
		imageUrl = MAIN_IMAGE_PATH % "FFFFFF"

		if cur:
			selectedKey = cur[0][1]

			if selectedKey == "COLOR":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteColor"
			elif selectedKey == "WEATHER":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteWeather"
			elif selectedKey == "OTHER":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteOther"
			elif selectedKey == "FONT":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteFont"
			elif selectedKey == "BACKUP":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteBackup"
			elif selectedKey == "SKINPART":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteSkinpart"
			elif selectedKey == "DESIGN":
				imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteSkinpart"

		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
		self.PicLoad.startDecode(imageUrl)
		self.showHelperText()

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def ok(self):
		cur = self["menuList"].getCurrent()

		if cur:
			selectedKey = cur[0][1]

			if selectedKey == "COLOR":
				self.session.open(ColorsSettingsView)
			elif selectedKey == "WEATHER":
				self.session.open(WeatherSettingsView)
			elif selectedKey == "OTHER":
				self.session.open(OtherSettingsView)
			elif selectedKey == "FONT":
				self.session.open(FontsSettingsView)
			elif selectedKey == "BACKUP":
				self.session.open(BackupSettingsView)
			elif selectedKey == "SKINPART":
				self.session.open(SkinpartSettingsView)
			elif selectedKey == "DESIGN":
				self.session.open(DesignSettingsView)

	def applyChanges(self):
		ret = ActivateSkinSettings().WriteSkin()
		if not type(ret) == tuple:
			self.session.open(MessageBox, _('Unknown error occurred!'), MessageBox.TYPE_ERROR)
		elif ret[0] == 'ErrorCode_2':
			self.session.open(MessageBox, ret[1], MessageBox.TYPE_ERROR)
		elif ret[0] == 'reboot':
			self.reboot(ret[1])
		elif ret[0] == 'error':
			self.session.open(MessageBox, ret[1], MessageBox.TYPE_ERROR)
		elif type(ret) == tuple and ret[0] == 'checkEHDsettings':
			self.session.openWithCallback(self.checkEHDsettingsCallback, MessageBox, ret[1], MessageBox.TYPE_INFO, timeout=10)

	def checkEHDsettings(self):
		ret = ActivateSkinSettings().CheckSettings(True)
		if type(ret) == tuple and ret[0] == 'checkEHDsettings':
			self.session.openWithCallback(self.checkEHDsettingsCallback, MessageBox, ret[1], MessageBox.TYPE_INFO, timeout=10)

	def checkEHDsettingsCallback(self, ret = None):
		self.session.open(OtherSettingsView)

	def reboot(self, message = None):
		if message is None:
			message = _("Do you really want to reboot now?")

		restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, message, MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart GUI"))

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close()

	def exit(self):
		self["menuList"].onSelectionChanged.remove(self.selectionChanged)
		self.close()

	def selectionChanged(self):
		self.ShowPicture()

	def showHelperText(self):
		cur = self["menuList"].getCurrent()
		if cur and len(cur[0]) > 2 and cur[0][2] and cur[0][2] != _("helptext"):
			self["helpertext"].setText(cur[0][2])
		else:
			self["helpertext"].setText(" ")
