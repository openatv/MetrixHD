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

from . import _, MAIN_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Console import Console
from Components.Label import Label
from enigma import ePicLoad, getBoxType
from os import path, statvfs, remove
from enigma import gMainDC, getDesktop
from ActivateSkinSettings import ActivateSkinSettings
from PIL import Image

BoxType = getBoxType()

#############################################################

class OtherSettingsView(ConfigListScreen, Screen):
	skin = """
	<screen name="MyMetrixLiteOtherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
	<widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
	<widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
	<widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="saveBtn" position="257,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="defaultsBtn" position="445,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="testBtn" position="631,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
	<eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
	<eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
	<eLabel position="616,635" size="5,40" backgroundColor="#000064c7" />
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
		self["titleText"].setText(_("Other settings"))

		self["cancelBtn"] = StaticText("")
		self["cancelBtn"].setText(_("Cancel"))

		self["saveBtn"] = StaticText("")
		self["saveBtn"].setText(_("Save"))

		self["testBtn"] = StaticText("")
		self["testBtn"].setText(_("Test Resolution"))

		self["defaultsBtn"] = StaticText("")
		self["defaultsBtn"].setText(_("Defaults"))

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
			"yellow": self.defaults,
			"blue": self.test,
			"cancel": self.exit
		}, -1)

		if self.session:
			self.checkEHDsettings()
			self.checkEHDtested()
		else:
			self.getEHDsettings()

		ConfigListScreen.__init__(
			self,
			self.getMenuItemList(),
			session = session,
			on_change = self.selectionChanged
		)

		self.onLayoutFinish.append(self.UpdatePicture)

	def getEHDsettings(self):
		if config.plugins.MyMetrixLiteOther.EHDenabled.value == '0':
			self.EHDenabled = False
			self.EHDfactor = 1
			self.EHDvalue = "0"
			self.EHDres = 'HD'
			self.EHDtxt = 'Standard HD'
		elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '1':
			self.EHDenabled = True
			self.EHDfactor = 1.5
			self.EHDvalue = "1"
			self.EHDres = 'FHD'
			self.EHDtxt = 'Full HD'
		elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '2':
			self.EHDenabled = True
			self.EHDfactor = 3
			self.EHDvalue = "2"
			self.EHDres = 'UHD'
			self.EHDtxt = 'Ultra HD'
		else:
			self.EHDenabled = False
			self.EHDfactor = 1
			self.EHDvalue = "0"
			self.EHDres = 'HD'
			self.EHDtxt = 'Standard HD'

	def checkEHDsettings(self):
		self.x = getDesktop(0).size().width()
		self.y = getDesktop(0).size().height()
		screenwidth = self.x

		if screenwidth and screenwidth == 1280:
			self.EHDvalue_old = "0"
			self.EHDres_old = 'HD'
			self.EHDtext_old = 'Standard HD'
		elif screenwidth and screenwidth == 1920 and not config.plugins.MyMetrixLiteOther.EHDenabled.value == '1':
			self.EHDvalue_old = "1"
			self.EHDres_old = 'FHD'
			self.EHDtext_old = 'Full HD'
		elif screenwidth and screenwidth == 3840  and not config.plugins.MyMetrixLiteOther.EHDenabled.value == '2':
			self.EHDvalue_old = "2"
			self.EHDres_old = 'UHD'
			self.EHDtext_old = 'Ultra HD'
		else:
			self.EHDvalue_old = "0"
			self.EHDres_old = 'HD'
			self.EHDtext_old = 'Standard HD'

	def selectionChanged(self):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == 'ENABLED_EHD':
			self.checkEHDtested()

		if cur == "PRESET":
			self.getPreset()

		if cur in ("ENABLED","ENABLED_EHD","PRESET","BUTTON"):
			self["config"].setList(self.getMenuItemList())

		self.ShowPicture(True)

	def checkEHDtested(self):
		self.getEHDsettings()
		tested = config.plugins.MyMetrixLiteOther.EHDtested.value.split('_|_')
		if self.EHDenabled and (len(tested) != 2 or not BoxType in tested[0] or not config.plugins.MyMetrixLiteOther.EHDenabled.value in tested[1]):
			if "green" in self["actions"].actions:
				del self["actions"].actions['green']
				self["saveBtn"].setText(_(" "))
			self["actions"].actions.update({"blue":self.test})
			self["testBtn"].setText(_("Test Resolution"))
		else:
			self["actions"].actions.update({"green":self.save})
			self["saveBtn"].setText(_("Save"))
			if "blue" in self["actions"].actions:
				del self["actions"].actions['blue']
				self["testBtn"].setText(_(" "))
			if self.EHDenabled:
				self.InstallCheck()
			else:
				self.UninstallCheck()

	def test(self):
		plustext=""
		#check hbbtv plugin - is sometimes or with some boxes not compatible with EHD-skin!
		if path.exists("/usr/lib/enigma2/python/Plugins/Extensions/HbbTV/plugin.pyo"):
			plustext = _("You have the'HbbTV Plugin' installed.\n")
		if plustext:
			text = plustext + _("\nMaybe is a compatibility issue with %s resolution.\nAttention: The osd-error occurs first after gui or system restart!\n\nDo you want really change from %s to %s - skin?") % (self.EHDtxt, self.EHDtext_old, self.EHDtxt)
			self.session.openWithCallback(self.resolutionQuestion, MessageBox, text, default = False, timeout = 10)
		else:
			self.resolutionQuestion(True)

	def resolutionQuestion(self, result):
		if not result:
			self.resetEHD()
			return
		import NavigationInstance
		import time
		rec = NavigationInstance.instance.RecordTimer.isRecording() or abs(NavigationInstance.instance.RecordTimer.getNextRecordingTime() - time.time()) <= 300
		plustext = ""
		if rec:
			plustext = _("!!! Recording(s) are in progress or coming up in few minutes !!!") + '\n'
		self.session.openWithCallback(self.resolutionTest, MessageBox, plustext + _("!!! If your receiver not compatible is a crash possible !!!\n\nChoose 'yes', then starts the resolution test.\nThe old resolution will automatically restored after 10 seconds."), default = False)

	def resolutionTest(self, result):
		if not result:
			self.resetEHD()
			return
		gMainDC.getInstance().setResolution(int(1280*self.EHDfactor), int(720*self.EHDfactor))
		self.session.openWithCallback(self.resolutionCheck, MessageBox, _("If you can see this then is your receiver compatible.\nDo you want change from %s to %s - skin resolution?") % (self.EHDtext_old, self.EHDtxt), default = False, timeout = 10)

	def resolutionCheck(self, result):
		gMainDC.getInstance().setResolution(self.x, self.y)
		if not result:
			self.resetEHD()
		else:
			if BoxType in config.plugins.MyMetrixLiteOther.EHDtested.value and len(config.plugins.MyMetrixLiteOther.EHDtested.value.split('_|_')) == 2:
				config.plugins.MyMetrixLiteOther.EHDtested.value += config.plugins.MyMetrixLiteOther.EHDenabled.value
			else:
				config.plugins.MyMetrixLiteOther.EHDtested.value = BoxType + '_|_' + config.plugins.MyMetrixLiteOther.EHDenabled.value
			config.plugins.MyMetrixLiteOther.save()
			configfile.save()
			ActivateSkinSettings().initConfigs()
			self.checkEHDtested()
			self["config"].setList(self.getMenuItemList())

	def freeFlashCheck(self):
		stat = statvfs("/usr/share/enigma2/MetrixHD/")
		freeflash = stat.f_bavail * stat.f_bsize / 1024 / 1024
		filesize = 10
		if self.EHDres == 'UHD':
			filesize = 25
		if freeflash < filesize:
			self.session.open(MessageBox, _("Not enough free flash memory to install the %s icons. ( %d MB is required )") % (self.EHDtxt, filesize), MessageBox.TYPE_ERROR)
			return False
		return True

	def resetEHD(self):
		config.plugins.MyMetrixLiteOther.EHDenabled.setValue(self.EHDvalue_old)
		self.checkEHDtested()
		self["config"].setList(self.getMenuItemList())

	def InstallCheck(self):
		self.Console = Console()
		self.service_name = 'enigma2-plugin-skins-metrix-vision-%s-icons' % self.EHDres.lower()
		if self.freeFlashCheck():
			self.Console.ePopen('/usr/bin/opkg list-installed ' + self.service_name, self.checkNetworkState)
		else:
			self.resetEHD()

	def checkNetworkState(self, str, retval, extra_args):
		if 'Collected errors' in str:
			self.session.open(MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
			self.resetEHD()
		elif not str:
			self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
			self.feedscheck.setTitle(_('Checking Feeds'))
			cmd1 = "opkg update"
			self.CheckConsole = Console()
			self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)

	def checkNetworkStateFinished(self, result, retval,extra_args=None):
		if 'bad address' in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s is not connected to the internet, please check your network settings and try again.") % (getBoxType(), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		else:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)

	def InstallPackage(self, val):
		if val:
			self.doInstall(self.installComplete, self.service_name)
		else:
			self.feedscheck.close()
			self.resetEHD()

	def InstallPackageFailed(self, val):
		self.feedscheck.close()
		self.resetEHD()

	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Installing ...'))
		self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

	def installComplete(self, result, retval = None, extra_args = None):
		if 'Unknown package' in result:
			self.session.open(MessageBox,_("Install Package not found!"), MessageBox.TYPE_ERROR, timeout=10)
			self.resetEHD()
		elif "Collected errors" in result:
			self.session.open(MessageBox,_("Installation error!\n\n%s") % result, MessageBox.TYPE_ERROR, timeout=10)
			self.resetEHD()
		self.feedscheck.close()
		self.message.close()

	def UninstallCheck(self):
		return #uninstall package disabled
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)

	def RemovedataAvail(self, str, retval, extra_args):
		if str:
			self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove %s ?') % self.service_name, MessageBox.TYPE_YESNO, default = False)

	def RemovePackage(self, val):
		if val:
			config.skin.primary_skin.setValue("MetrixHD/skin.xml")
			config.skin.save()
			configfile.save()
			self.doRemove(self.removeComplete, self.service_name)

	def doRemove(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Removing ...'))
		self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

	def removeComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()

	def getPreset(self):
		if config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_0":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "no"
		elif config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_1":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignRUCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignLUCposz.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value = 3
			config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value = 29
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposz.value = 1
			config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.value = 3
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposx.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposy.value = 696
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposz.value = 1
		elif config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_2":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "menus"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "screens"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "screens"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignLUCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth.value = 795
			config.plugins.MyMetrixLiteOther.SkinDesignLLCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignRUCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignLLCposz.value = 1
			config.plugins.MyMetrixLiteOther.SkinDesignRUCposz.value = 0
		elif config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_3":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth.value = 100
			config.plugins.MyMetrixLiteOther.SkinDesignLUCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth.value = 100
			config.plugins.MyMetrixLiteOther.SkinDesignRUCheight.value = 720
			config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value = 5
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value = 10
			config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.value = 5
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposx.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposy.value = 695
			config.plugins.MyMetrixLiteOther.SkinDesignLUCposz.value = 1
			config.plugins.MyMetrixLiteOther.SkinDesignRUCposz.value = 1
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposz.value = 0
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposz.value = 0
		elif config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_4":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "both"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth.value = 200
			config.plugins.MyMetrixLiteOther.SkinDesignLUCheight.value = 41
			config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth.value = 200
			config.plugins.MyMetrixLiteOther.SkinDesignLLCheight.value = 101
			config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth.value = 200
			config.plugins.MyMetrixLiteOther.SkinDesignRUCheight.value = 41
			config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth.value = 1280
			config.plugins.MyMetrixLiteOther.SkinDesignRLCheight.value = 101
			config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value = 200
			config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value = 41
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value = 540
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value = 0
		elif config.plugins.MyMetrixLiteOther.SkinDesignExamples.value == "preset_5":
			config.plugins.MyMetrixLiteOther.SkinDesignLUC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignLLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRUC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignRLC.value = "no"
			config.plugins.MyMetrixLiteOther.SkinDesignOLH.value = "screens"
			config.plugins.MyMetrixLiteOther.SkinDesignOLV.value = "menus"
			config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value = 1220
			config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value = 670
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value = 30
			config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value = 15
			config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.value = 883
			config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.value = 578
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposx.value = 254
			config.plugins.MyMetrixLiteOther.SkinDesignOLVposy.value = 41

	def getCPUSensor(self):
		temp = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			temp = f.read()
			f.close()
		elif path.exists('/proc/stb/power/avs'):
			f = open('/proc/stb/power/avs', 'r')
			temp = f.read()
			f.close()
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				temp = f.read()
				temp = temp[:-4]
				f.close()
			except:
				temp = ""
		elif path.exists('/proc/hisi/msp/pm_cpu'):
			try:
				for line in open('/proc/hisi/msp/pm_cpu').readlines():
					line = [x.strip() for x in line.strip().split(":")]
					if line[0] in ("Tsensor"):
						temp = line[1].split("=")
						temp = line[1].split(" ")
						temp = temp[2]
			except:
				temp = ""
		if temp and int(temp.replace('\n', '')) > 0:
			return True
		else:
			return False

	def getSYSSensor(self):
		temp = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			temp = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			temp = f.read()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			temp = f.read()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			return True
		else:
			return False

	def getMenuItemList(self):
		char = 150
		tab = " "*10
		sep = "-"
		list = []
		section = _("Enhanced HD Option")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Choose skin resolution"), config.plugins.MyMetrixLiteOther.EHDenabled, _("helptext"),"ENABLED_EHD"))
		if self.EHDenabled:
			list.append(getConfigListEntry(tab + _("All calculated values round down"), config.plugins.MyMetrixLiteOther.EHDrounddown, _("helptext")))
			#list.append(getConfigListEntry(_("Method of font scaling"), config.plugins.MyMetrixLiteOther.EHDfontsize))
			# EHDfontsize deactivated
			if config.plugins.MyMetrixLiteOther.EHDfontsize.value != "2":
				self.setInputToDefault(config.plugins.MyMetrixLiteOther.EHDfontsize)
			list.append(getConfigListEntry(tab + _("Additional offset for font scaling"), config.plugins.MyMetrixLiteOther.EHDfontoffset, _("helptext")))
			#list.append(getConfigListEntry(tab + _("Calculating additional files"), config.plugins.MyMetrixLiteOther.EHDadditionalfiles, _("File list:\n\n%s") % '"/etc/enigma2/antilogo.xml"', "ENABLED"))
		list.append(getConfigListEntry(tab + _("Experimental picon scaling"), config.plugins.MyMetrixLiteOther.piconresize_experimental, _("Set to 'Yes' if you have poor scaling quality - experimental.\n(no restart required)"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.piconresize_experimental.value:
			list.append(getConfigListEntry(tab + _("Experimental picon sharpness"), config.plugins.MyMetrixLiteOther.piconsharpness_experimental, _("Improved the scaling quality - experimental.\nInfo: < 1 = blurred and > 1 = sharpened image\n(no restart required)")))
		section = _("STB-Info")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Distance between the STB-Infos"), config.plugins.MyMetrixLiteOther.STBDistance, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show CPU-Load"), config.plugins.MyMetrixLiteOther.showCPULoad, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show free RAM"), config.plugins.MyMetrixLiteOther.showRAMfree, _("helptext")))
		if self.getCPUSensor():
			list.append(getConfigListEntry(tab + _("Show CPU-Temp"), config.plugins.MyMetrixLiteOther.showCPUTemp, _("helptext")))
		elif config.plugins.MyMetrixLiteOther.showCPUTemp.getValue() is not False:
			config.plugins.MyMetrixLiteOther.showCPUTemp.setValue(False)
			config.plugins.MyMetrixLiteOther.save()
		if self.getSYSSensor():
			list.append(getConfigListEntry(tab + _("Show SYS-Temp"), config.plugins.MyMetrixLiteOther.showSYSTemp, _("helptext")))
		elif config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is not False:
			config.plugins.MyMetrixLiteOther.showSYSTemp.setValue(False)
			config.plugins.MyMetrixLiteOther.save()
		section = _("InfoBar")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Show Extended-Info"), config.plugins.MyMetrixLiteOther.showExtendedinfo, _("After enabling, 'Apply changes' and restart needs never press 'Apply changes' (and restart) when you change subordinate options."), "ENABLED"))
		itext = _("Show only if available.\n\nPositions:\n")
		if config.plugins.MyMetrixLiteOther.showExtendedinfo.value:
			oscam = path.exists('/tmp/.oscam')
			list.append(getConfigListEntry(tab*2 + _("Show CAID"), config.plugins.MyMetrixLiteOther.showExtended_caid, itext + "(CAID - pid - source - protocol - hops - ecm time)", "ENABLED"))
			if config.plugins.MyMetrixLiteOther.showExtended_caid.value and oscam:
				list.append(getConfigListEntry(tab*3 + _("Show PROV"), config.plugins.MyMetrixLiteOther.showExtended_prov, itext + "(caid:PROV - pid - source - protocol - hops - ecm time)"))
			list.append(getConfigListEntry(tab*2 + _("Show PID"), config.plugins.MyMetrixLiteOther.showExtended_pid, itext + "(caid - PID - source - protocol - hops - ecm time)"))
			list.append(getConfigListEntry(tab*2 + _("Show SOURCE"), config.plugins.MyMetrixLiteOther.showExtended_source, itext + "(caid - pid - SOURCE - protocol - hops - ecm time)", "ENABLED"))
			if config.plugins.MyMetrixLiteOther.showExtended_source.value and oscam:
				list.append(getConfigListEntry(tab*3 + _("Show READER"), config.plugins.MyMetrixLiteOther.showExtended_reader, itext + "(caid - pid - READER - protocol - hops - ecm time)"))
			list.append(getConfigListEntry(tab*2 + _("Show PROTOCOL"), config.plugins.MyMetrixLiteOther.showExtended_protocol, itext + "(caid - pid - source - PROTOCOL - hops - ecm time)"))
			list.append(getConfigListEntry(tab*2 + _("Show HOPS"), config.plugins.MyMetrixLiteOther.showExtended_hops,  itext + "(caid - pid - source - protocol - HOPS - ecm time)"))
			list.append(getConfigListEntry(tab*2 + _("Show ECM TIME"), config.plugins.MyMetrixLiteOther.showExtended_ecmtime, itext + "(caid - pid - source - protocol - hops - ECM TIME)"))
		#list.append(getConfigListEntry(tab + _("Enable Color Gradient"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarColorGradient, _("helptext")))
		list.append(getConfigListEntry(tab + _("Choose Picon Type"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon.value == "1":
			if self.EHDenabled:
				list.append(getConfigListEntry(tab + _("Show picons zoomed ?"), config.plugins.MyMetrixLiteOther.EHDpiconzoom, _("helptext")))
			list.append(getConfigListEntry(tab + _("Offset picon position x"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosX, _("helptext")))
			list.append(getConfigListEntry(tab + _("Offset picon position y"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosY, _("helptext")))
		else:
			list.append(getConfigListEntry(tab + _("Offset picon size"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize, _("helptext")))
			list.append(getConfigListEntry(tab + _("Offset picon position x"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosX, _("helptext")))
			list.append(getConfigListEntry(tab + _("Offset picon position y"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosY, _("helptext")))
		section = _("InfoBar/SecondInfobar")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Show Clock"), config.plugins.MyMetrixLiteOther.showInfoBarClock, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show ChannelName"), config.plugins.MyMetrixLiteOther.showChannelName, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show ChannelNumber"), config.plugins.MyMetrixLiteOther.showChannelNumber, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show ServiceIcons"), config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Record-State"), config.plugins.MyMetrixLiteOther.showRecordstate, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Screen-Resolution"), config.plugins.MyMetrixLiteOther.showInfoBarResolution, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.showInfoBarResolution.getValue() is True:
			list.append(getConfigListEntry(tab + _("Show extended Screen-Resolution"), config.plugins.MyMetrixLiteOther.showInfoBarResolutionExtended, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Orbital-Position"), config.plugins.MyMetrixLiteOther.showOrbitalposition, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show SNR-Info"), config.plugins.MyMetrixLiteOther.showSnr, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Tuner-Info"), config.plugins.MyMetrixLiteOther.showTunerinfo, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.showTunerinfo.getValue() is True:
			list.append(getConfigListEntry(tab + _("Set number of tuner automatically"), config.plugins.MyMetrixLiteOther.setTunerAuto, _("helptext"), "ENABLED"))
			if config.plugins.MyMetrixLiteOther.setTunerAuto.getValue() is False:
				list.append(getConfigListEntry(tab + _("Set number of tuner manually"), config.plugins.MyMetrixLiteOther.setTunerManual, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show STB-Info"), config.plugins.MyMetrixLiteOther.showSTBinfo, _("After enabling, 'Apply changes' and restart needs never press 'Apply changes' (and restart) when you change subordinate entrys in 'STB-Info'.")))
		section = _("InfoBar/SecondInfobar/Moviebar")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		helptext = _("Show running text for event. If it flickers, try increasing the start delay.")
		list.append(getConfigListEntry(tab + _("Show running text?"), config.plugins.MyMetrixLiteOther.showInfoBarRunningtext, helptext, "ENABLED"))
		list.append(getConfigListEntry(tab + _("ChannelName/Number FontSize"), config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize, _("helptext")))
		section = _("EMC")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Show Cover in Media Center"),config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover.getValue() == "small" and config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
			list.append(getConfigListEntry(tab + _("Show Cover in Infobar"), config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Cover in Movie Selection"),config.plugins.MyMetrixLiteOther.showEMCSelectionCover, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.showEMCSelectionCover.getValue() == "large":
			list.append(getConfigListEntry(tab + _("Show Movie Description"), config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Picon in Movie Selection?"), config.plugins.MyMetrixLiteOther.showEMCSelectionPicon, _("helptext")))
		list.append(getConfigListEntry(tab + _("Change Number of Rows in Movie Selection"),config.plugins.MyMetrixLiteOther.showEMCSelectionRows, _("helptext")))
		list.append(getConfigListEntry(tab + _("Change field size 'Date' in Movie Selection"),config.plugins.MyMetrixLiteOther.setEMCdatesize, _("Change field size or hide")))
		list.append(getConfigListEntry(tab + _("Change field size 'Count/Size' in Movie Selection"),config.plugins.MyMetrixLiteOther.setEMCdirinfosize, _("Change field size or hide")))
		list.append(getConfigListEntry(tab + _("Change field size 'Progressbar' in Movie Selection"),config.plugins.MyMetrixLiteOther.setEMCbarsize, _("Change field size or hide")))
		section = _("EMC/MovieList")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		if not config.movielist.useslim.value:
			list.append(getConfigListEntry(tab + _("Movie List style"), config.plugins.MyMetrixLiteOther.movielistStyle, _("Info: Setting applies not for EMC.")))
		help_scrollbar = _("Show Scrollbar if more than one pages are available.")
		help_runningtext = _("Show running text for description of the event.")
		list.append(getConfigListEntry(tab + _("Show scrollbar?"), config.plugins.MyMetrixLiteOther.showMovieListScrollbar, help_scrollbar))
		list.append(getConfigListEntry(tab + _("Show running text?"), config.plugins.MyMetrixLiteOther.showMovieListRunningtext, help_runningtext, "ENABLED"))
		section = _("EMC/MoviePlayer")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Hide PVR State"), config.usage.movieplayer_pvrstate, _("Setting is the same as\n'") + _("Show PVR status in MoviePlayer infobar") + _("'\nin\n'") + _("OSD settings") + "'", "ENABLED"))
		if not config.usage.movieplayer_pvrstate.value:
			list.append(getConfigListEntry(tab*2 + _("Position PVR State"), config.plugins.MyMetrixLiteOther.showPVRState, _("helptext")))
		list.append(getConfigListEntry(tab + _("Style"), config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
			list.append(getConfigListEntry(tab + _("Show extended Screen-Resolution"), config.plugins.MyMetrixLiteOther.showMoviePlayerResolutionExtended, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Clock"), config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show MovieName"), config.plugins.MyMetrixLiteOther.showMovieName, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Movie Playback Time"), config.plugins.MyMetrixLiteOther.showMovieTime, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show STB-Info"), config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer,  _("After enabling, 'Apply changes' and restart needs never press 'Apply changes' (and restart) when you change subordinate entrys in 'STB-Info'.")))
		section = _("mini TV")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Show in Channel selection?"), config.usage.servicelist_mode, _("Setting is the same as\n'") + _("Channel list service mode*") + _("'\nin\n'") + _("Channel selection settings") + _("'\n(") + _("Simple") + _(" = mini TV on)"), "ENABLED"))
		list.append(getConfigListEntry(tab + _("Show in graphical EPG?"), config.epgselection.graph_pig, _("Setting is the same as\n'") + _("Picture in graphics") + _("'\nin\n'") + _("GraphicalEPG settings") + "'"))
		list.append(getConfigListEntry(tab + _("Show in Movie Center?"), config.movielist.useslim, _("Setting is the same as\n'") + _("Use slim screen") + _("'\nin\n'") + _("Movie List Setup") + "'", "ENABLED"))
		section = _("ChannelSelection") + ", " + _("graphical EPG")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		if config.usage.servicelist_mode.value == 'standard':
			list.append(getConfigListEntry(tab + _("Channel selection style"), config.plugins.MyMetrixLiteOther.channelSelectionStyle, _("helptext"), "ENABLED"))
		list.append(getConfigListEntry(tab + _("Item Distance"), config.plugins.MyMetrixLiteOther.setItemDistance, _("Distance between Servicename and Eventname.")))
		list.append(getConfigListEntry(tab + _("Field Distance"), config.plugins.MyMetrixLiteOther.setFieldMargin, _("Distance between Servicenumber and Servicename or Eventname and Progressbar.")))
		if config.usage.servicelist_mode.value == 'standard' and int(config.plugins.MyMetrixLiteOther.SkinDesign.value) > 1 and (config.plugins.MyMetrixLiteOther.channelSelectionStyle.value == "CHANNELSELECTION-1" or config.plugins.MyMetrixLiteOther.channelSelectionStyle.value == "CHANNELSELECTION-2"):
			list.append(getConfigListEntry(tab + _("Show Primetime Event"), config.plugins.MyMetrixLiteOther.channelSelectionShowPrimeTime, _("Set primetime in graphical epg settings.")))
		list.append(getConfigListEntry(tab + _("Graphical EPG style"), config.plugins.MyMetrixLiteOther.graphicalEpgStyle, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show scrollbar?"), config.plugins.MyMetrixLiteOther.showChannelListScrollbar, help_scrollbar))
		list.append(getConfigListEntry(tab + _("Show running text?"), config.plugins.MyMetrixLiteOther.showChannelListRunningtext, help_runningtext, "ENABLED"))
		section = _("Running Text Parameter")
		if config.plugins.MyMetrixLiteOther.showChannelListRunningtext.value or config.plugins.MyMetrixLiteOther.showMovieListRunningtext.value or config.plugins.MyMetrixLiteOther.showInfoBarRunningtext.value:
			list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
			list.append(getConfigListEntry(tab + _("Startdelay"),config.plugins.MyMetrixLiteOther.runningTextStartdelay, _("helptext")))
			list.append(getConfigListEntry(tab + _("Speed"),config.plugins.MyMetrixLiteOther.runningTextSpeed, _("A higher value results in a slow movement.")))
		section = _("Skin Design")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Chose Skin Design"),config.plugins.MyMetrixLiteOther.SkinDesign, _("helptext"), "ENABLED"))
		list.append(getConfigListEntry(tab + _("Scrollbar Slider width"), config.plugins.MyMetrixLiteOther.SkinDesignScrollbarSliderWidth, _("helptext")))
		list.append(getConfigListEntry(tab + _("Scrollbar Border width"), config.plugins.MyMetrixLiteOther.SkinDesignScrollbarBorderWidth, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Space between Layer A and B"),config.plugins.MyMetrixLiteOther.SkinDesignSpace, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show Menu Buttons"),config.plugins.MyMetrixLiteOther.SkinDesignMenuButtons, _("Show color buttons at top of the screen.")))
		list.append(getConfigListEntry(tab + _("Show Menu Scrollinfo"),config.plugins.MyMetrixLiteOther.SkinDesignMenuScrollInfo, _("Show info in main menu and context menu if more entries on next side.\n(no restart required)")))
		list.append(getConfigListEntry(tab + _("Show large Text on bottom of the screen"),config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText, _("helptext")))
		list.append(getConfigListEntry(tab + _("Chose Extended-Info Style"), config.plugins.MyMetrixLiteOther.ExtendedinfoStyle, _("helptext")))
		section = _("Skin Design Buttons")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Skin Design Buttons"),config.plugins.MyMetrixLiteOther.SkinDesignButtons, _("helptext"), "BUTTON"))
		if config.plugins.MyMetrixLiteOther.SkinDesignButtons.value:
			list.append(getConfigListEntry(tab + _("Back Color"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColor, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Back Color Transparency"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColorTransparency, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Frame Size"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameSize, _("helptext"), "BUTTON"))
			if config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameSize.value:
				list.append(getConfigListEntry(tab + _("Frame Color"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColor, _("helptext"), "BUTTON"))
				list.append(getConfigListEntry(tab + _("Frame Color Transparency"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColorTransparency, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Text Color"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColor, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Text Color Transparency"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColorTransparency, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Text Font"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextFont, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Text Size"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextSize, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Text Position"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextPosition, _("helptext"), "BUTTON"))
			list.append(getConfigListEntry(tab + _("Glossy Effect"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect, _("helptext"), "BUTTON"))
			if config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value != 'no':
				list.append(getConfigListEntry(tab + _("Glossy Effect Size"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectSize, _("helptext"), "BUTTON"))
				if 'circle' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value:
					list.append(getConfigListEntry(tab + _("Glossy Effect Position X"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosX, _("helptext"), "BUTTON"))
					list.append(getConfigListEntry(tab + _("Glossy Effect Position Y"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosY, _("helptext"), "BUTTON"))
				list.append(getConfigListEntry(tab + _("Glossy Effect Color"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectColor, _("helptext"), "BUTTON"))
				list.append(getConfigListEntry(tab + _("Glossy Effect Intensity"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectIntensity, _("helptext"), "BUTTON"))
				list.append(getConfigListEntry(tab + _("Glossy Effect Over Text"),config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectOverText, _("helptext"), "BUTTON"))
		return list

	def getButtonPreview(self):
		if not config.plugins.MyMetrixLiteOther.SkinDesignButtons.value or not path.exists(MAIN_IMAGE_PATH % "other/template"):
			return
		ret = ActivateSkinSettings().makeButtons('/tmp/button.png', _('TEST'))
		if ret:
			img = Image.open(MAIN_IMAGE_PATH % "other/template")
			imga = Image.open('/tmp/button.png')
			imgwidth, imgheight = img.size
			imgawidth, imgaheight = imga.size
			img.paste(imga,((imgwidth-imgawidth)/2,(imgheight-imgaheight)/3))
			img.save("/tmp/template.png")

	def GetPicturePath(self):
		return MAIN_IMAGE_PATH % "MyMetrixLiteOther"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self, update=False):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]
		if cur == "BUTTON" and config.plugins.MyMetrixLiteOther.SkinDesignButtons.value:
			if not path.exists("/tmp/template.png") or update:
				self.getButtonPreview()
			self["helperimage"].instance.setPixmapFromFile("/tmp/template.png")
		else:
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

	def save(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()

		configfile.save()
		self.exit()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
		if path.exists("/tmp/template.png"):
			remove("/tmp/template.png")
		self.close()

	def defaults(self, SAVE = False):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				if SAVE: x[1].save()
		if self.session:
			self["config"].setList(self.getMenuItemList())
			self.ShowPicture()

	def setNewValue(self, configItem, newValue):
		configItem.setValue(newValue)

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

	def showHelperText(self):
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")
