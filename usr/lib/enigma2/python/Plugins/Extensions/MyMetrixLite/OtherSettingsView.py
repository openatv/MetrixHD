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

from . import _, initOtherConfig, OTHER_IMAGE_PATH, MAIN_IMAGE_PATH
from boxbranding import getBoxType, getMachineBrand, getMachineName
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Console import Console
from enigma import ePicLoad
from os import path, statvfs
from enigma import gMainDC, getDesktop

#############################################################

class OtherSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteOtherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
    <widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="saveBtn" position="257,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="defaultsBtn" position="445,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

        self["titleText"] = StaticText("")
        self["titleText"].setText(_("Other settings"))

        self["cancelBtn"] = StaticText("")
        self["cancelBtn"].setText(_("Cancel"))

        self["saveBtn"] = StaticText("")
        self["saveBtn"].setText(_("Save"))

        self["defaultsBtn"] = StaticText("")
        self["defaultsBtn"].setText(_("Defaults"))

        initOtherConfig()

        ConfigListScreen.__init__(
            self,
            self.getMenuItemList(),
            session = session,
            on_change = self.__selectionChanged
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
            "yellow": self.defaults,
            "cancel": self.exit
        }, -1)

        self.onLayoutFinish.append(self.UpdatePicture)

    def __selectionChanged(self):
        cur = self["config"].getCurrent()
        cur = cur and len(cur) > 2 and cur[2]

        if cur == "PRESET":
            self.getPreset()

        if cur == "ENABLED" or cur == "ENABLED_FHD" or cur == "PRESET":
            self["config"].setList(self.getMenuItemList())

        self.Console = Console()
        self.service_name = 'enigma2-plugin-skins-metrix-atv-fhd-icons'

        self.x = getDesktop(0).size().width()
        self.y = getDesktop(0).size().height()
        if cur == "ENABLED_FHD" and config.plugins.MyMetrixLiteOther.FHDenabled.value and self.x < 1920 and self.y < 1080:
            self.session.openWithCallback(self.resolutionTest, MessageBox, _("If you chose 'yes', then starts the resolution test.\n\nCan't you see the next message,\nthe old resolution will automatically after 10 seconds restored."), default = False)
        elif cur == "ENABLED_FHD" and not config.plugins.MyMetrixLiteOther.FHDenabled.value:
            self.UninstallCheck()
        elif cur == "ENABLED_FHD" and config.plugins.MyMetrixLiteOther.FHDenabled.value:
            self.InstallCheck()

    def resolutionTest(self, result):
        if not result:
            self.resetFHD()
            return
        gMainDC.getInstance().setResolution(1920, 1080)
        self.session.openWithCallback(self.resolutionCheck, MessageBox, _("Can you see this, then is the receiver ready for FHD - skin.\n\nDo you want to change from HD to FHD - skin?"), default = False, timeout = 10)

    def resolutionCheck(self, result):
        gMainDC.getInstance().setResolution(self.x, self.y)
        if not result:
            self.resetFHD()
        else:
            self.InstallCheck()

    def freeFlashCheck(self):
        stat = statvfs("/usr/share/enigma2/MetrixHD/")
        freeflash = stat.f_bavail * stat.f_bsize / 1024 / 1024
        filesize = 5
        if freeflash < filesize:
            self.session.open(MessageBox, _("Your free flash space is to small.\n%d MB is not enough to install the full-hd icons. ( %d MB is required )") % (freeflash, filesize), MessageBox.TYPE_ERROR)
            return False
        return True

    def resetFHD(self):
        config.plugins.MyMetrixLiteOther.FHDenabled.setValue(False)
        self["config"].setList(self.getMenuItemList())

    def InstallCheck(self):
        if self.freeFlashCheck():
            self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)
        else:
            self.resetFHD()

    def checkNetworkState(self, str, retval, extra_args):
        if 'Collected errors' in str:
            self.session.openWithCallback(self.close, MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif not str:
            self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
            self.feedscheck.setTitle(_('Checking Feeds'))
            cmd1 = "opkg update"
            self.CheckConsole = Console()
            self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)

    def checkNetworkStateFinished(self, result, retval,extra_args=None):
        if 'bad address' in result:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
            self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
        else:
            self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)

    def InstallPackage(self, val):
        if val:
            self.doInstall(self.installComplete, self.service_name)
        else:
            self.feedscheck.close()
            self.resetFHD()

    def InstallPackageFailed(self, val):
        self.feedscheck.close()
        self.resetFHD()

    def doInstall(self, callback, pkgname):
        self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
        self.message.setTitle(_('Installing ...'))
        self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

    def installComplete(self, result, retval, extra_args = None):
        if result.startswith('Unknown') or retval == "255":
            self.session.open(MessageBox,_("Install Package not found!"), MessageBox.TYPE_ERROR, timeout=10)
            self.resetFHD()
        self.feedscheck.close()
        self.message.close()

    def UninstallCheck(self):
        self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)

    def RemovedataAvail(self, str, retval, extra_args):
        if str:
            self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove %s ?') % self.service_name, MessageBox.TYPE_YESNO)

    def RemovePackage(self, val):
        if val:
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

    def getCPUSensor(self):
        temp = ""
        if path.exists('/proc/stb/fp/temp_sensor_avs'):
            f = open('/proc/stb/fp/temp_sensor_avs', 'r')
            temp = f.read()
            f.close()
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
        if temp and int(temp.replace('\n', '')) > 0:
            return True
        else:
            return False

    def getMenuItemList(self):
        
        list = []
        list.append(getConfigListEntry(_("FHD-Option   ------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Enable FHD"), config.plugins.MyMetrixLiteOther.FHDenabled, "ENABLED_FHD"))
        if config.plugins.MyMetrixLiteOther.FHDenabled.getValue() is True:
            list.append(getConfigListEntry(_("All calculated values round down"), config.plugins.MyMetrixLiteOther.FHDrounddown))
            #list.append(getConfigListEntry(_("Method of font scaling"), config.plugins.MyMetrixLiteOther.FHDfontsize))
            # FHDfontsize deactivated
            if config.plugins.MyMetrixLiteOther.FHDfontsize.value != "2":
                self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDfontsize)
            list.append(getConfigListEntry(_("Additional offset for font scaling"), config.plugins.MyMetrixLiteOther.FHDfontoffset))
            list.append(getConfigListEntry(_("Calculating additional files"), config.plugins.MyMetrixLiteOther.FHDadditionalfiles))
        list.append(getConfigListEntry(_("STB-Info   ------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Distance between the STB-Infos"), config.plugins.MyMetrixLiteOther.STBDistance))
        list.append(getConfigListEntry(_("Show CPU-Load"), config.plugins.MyMetrixLiteOther.showCPULoad))
        list.append(getConfigListEntry(_("Show free RAM"), config.plugins.MyMetrixLiteOther.showRAMfree))
        if self.getCPUSensor() or config.plugins.MyMetrixLiteOther.showCPUTemp.getValue() is not False:
            list.append(getConfigListEntry(_("Show CPU-Temp"), config.plugins.MyMetrixLiteOther.showCPUTemp))
        if self.getSYSSensor() or config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is not False:
            list.append(getConfigListEntry(_("Show SYS-Temp"), config.plugins.MyMetrixLiteOther.showSYSTemp))
        list.append(getConfigListEntry(_("InfoBar/SecondInfobar/MoviePlayer   ------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("ChannelName/Number FontSize"), config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize))
        list.append(getConfigListEntry(_("InfoBar/SecondInfobar   ------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show Clock"), config.plugins.MyMetrixLiteOther.showInfoBarClock))
        list.append(getConfigListEntry(_("Show ChannelName"), config.plugins.MyMetrixLiteOther.showChannelName))
        list.append(getConfigListEntry(_("Show ChannelNumber"), config.plugins.MyMetrixLiteOther.showChannelNumber))
        list.append(getConfigListEntry(_("Show ServiceIcons"), config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons))
        list.append(getConfigListEntry(_("Show Record-State"), config.plugins.MyMetrixLiteOther.showRecordstate))
        list.append(getConfigListEntry(_("Show Screen-Resolution"), config.plugins.MyMetrixLiteOther.showInfoBarResolution))
        list.append(getConfigListEntry(_("Show Orbital-Position"), config.plugins.MyMetrixLiteOther.showOrbitalposition))
        list.append(getConfigListEntry(_("Show SNR-Info"), config.plugins.MyMetrixLiteOther.showSnr))
        list.append(getConfigListEntry(_("Show Tuner-Info"), config.plugins.MyMetrixLiteOther.showTunerinfo, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.showTunerinfo.getValue() is True:
            list.append(getConfigListEntry(_("Set number of tuner automatically"), config.plugins.MyMetrixLiteOther.setTunerAuto, "ENABLED"))
            if config.plugins.MyMetrixLiteOther.setTunerAuto.getValue() is False:
                list.append(getConfigListEntry(_("Set number of tuner manually"), config.plugins.MyMetrixLiteOther.setTunerManual))
        list.append(getConfigListEntry(_("Show STB-Info"), config.plugins.MyMetrixLiteOther.showSTBinfo))
        list.append(getConfigListEntry(_("InfoBar   -------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show Extended-Info"), config.plugins.MyMetrixLiteOther.showExtendedinfo))
        list.append(getConfigListEntry(_("Enable Color Gradient"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarColorGradient))
        list.append(getConfigListEntry(_("Choose Picon Type"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon.value == "1":
            if config.plugins.MyMetrixLiteOther.FHDenabled.value:
                list.append(getConfigListEntry(_("Show picons zoomed ?"), config.plugins.MyMetrixLiteOther.FHDpiconzoom))
            list.append(getConfigListEntry(_("Offset picon position x"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosX))
            list.append(getConfigListEntry(_("Offset picon position y"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosY))
        else:
            list.append(getConfigListEntry(_("Offset picon size"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize))
            list.append(getConfigListEntry(_("Offset picon position x"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosX))
            list.append(getConfigListEntry(_("Offset picon position y"), config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosY))
        list.append(getConfigListEntry(_("EMC/MoviePlayer   ------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Style"), config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign, "ENABLED"))
        list.append(getConfigListEntry(_("Show Clock"), config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer))
        list.append(getConfigListEntry(_("Show MovieName"), config.plugins.MyMetrixLiteOther.showMovieName))
        list.append(getConfigListEntry(_("Show Movie Playback Time"), config.plugins.MyMetrixLiteOther.showMovieTime))
        list.append(getConfigListEntry(_("Show PVR State"), config.plugins.MyMetrixLiteOther.showPVRState))
        list.append(getConfigListEntry(_("Show STB-Info"), config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer))
        list.append(getConfigListEntry(_("EMC   ------------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show Cover in Media Center"),config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover.getValue() == "small" and config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
            list.append(getConfigListEntry(_("Show Cover in Infobar"), config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar))
        list.append(getConfigListEntry(_("Show Cover in Movie Selection"),config.plugins.MyMetrixLiteOther.showEMCSelectionCover, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.showEMCSelectionCover.getValue() == "large":
            list.append(getConfigListEntry(_("Show Movie Description"), config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription))
        list.append(getConfigListEntry(_("ChannelSelection   -----------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Channel selection style"), config.plugins.MyMetrixLiteOther.channelSelectionStyle))
        list.append(getConfigListEntry(_("Skin Design   ----------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Chose Skin Design"),config.plugins.MyMetrixLiteOther.SkinDesign))
        list.append(getConfigListEntry(_("Show Space between Layer A and B"),config.plugins.MyMetrixLiteOther.SkinDesignSpace))
        list.append(getConfigListEntry(_("Show large Text on bottom of the screen"),config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText))
        list.append(getConfigListEntry(_("Chose Extended-Info Style"), config.plugins.MyMetrixLiteOther.ExtendedinfoStyle))
        list.append(getConfigListEntry(_("Skin Design - additional Layers  ---------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Skin Design Examples"),config.plugins.MyMetrixLiteOther.SkinDesignExamples, "PRESET"))
        list.append(getConfigListEntry(_("Show upper left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLUC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignLUC.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignLUCheight))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLUCposz))
        list.append(getConfigListEntry(_("Show lower left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLLC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignLLC.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignLLCheight))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLLCposz))
        list.append(getConfigListEntry(_("Show upper right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRUC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignRUC.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignRUCheight))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRUCposz))
        list.append(getConfigListEntry(_("Show lower right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRLC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignRLC.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignRLCheight))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRLCposz))
        list.append(getConfigListEntry(_("Show optional horizontal Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLH, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignOLH.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignOLHheight))
            list.append(getConfigListEntry(_("   pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposx))
            list.append(getConfigListEntry(_("   pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposy))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposz))
        list.append(getConfigListEntry(_("Show optional vertical Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLV, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignOLV.getValue() is not "no":
            list.append(getConfigListEntry(_("   width"), config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth))
            list.append(getConfigListEntry(_("   height"), config.plugins.MyMetrixLiteOther.SkinDesignOLVheight))
            list.append(getConfigListEntry(_("   pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposx))
            list.append(getConfigListEntry(_("   pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposy))
            list.append(getConfigListEntry(_("   pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposz))

        return list

    def GetPicturePath(self):
        try:
            returnValue = self["config"].getCurrent()[1].value
            path = OTHER_IMAGE_PATH % returnValue
            return path
        except:
            pass

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(MAIN_IMAGE_PATH % "MyMetrixLiteOther")
        #self.PicLoad.startDecode(self.GetPicturePath())

    def DecodePicture(self, PicInfo = ""):
        ptr = self.PicLoad.getData()
        self["helperimage"].instance.setPixmap(ptr)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.ShowPicture()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.ShowPicture()

    def keyDown(self):
        self["config"].instance.moveSelection(self["config"].instance.moveDown)
        self.ShowPicture()

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)
        self.ShowPicture()

    def showInfo(self):
        self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

    def save(self):

        width = int(config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value)
        height = int(config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value)
        posx = int(config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value)
        posy = int(config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value)
        if (posx + width) > 1280:
            width = width - (posx + width - 1280)
            config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.setValue(width)
        if (posy + height) > 720:
            height = height - (posy + height - 720)
            config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.setValue(height)

        width = int(config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.value)
        height = int(config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.value)
        posx = int(config.plugins.MyMetrixLiteOther.SkinDesignOLVposx.value)
        posy = int(config.plugins.MyMetrixLiteOther.SkinDesignOLVposy.value)
        if (posx + width) > 1280:
            width = width - (posx + width - 1280)
            config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.setValue(width)
        if (posy + height) > 720:
            height = height - (posy + height - 720)
            config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.setValue(height)

        for x in self["config"].list:
            if len(x) > 1:
                x[1].save()
            else:
                pass

        configfile.save()
        self.exit()

    def exit(self):
        for x in self["config"].list:
            if len(x) > 1:
                    x[1].cancel()
            else:
                    pass
        self.close()

    def defaults(self):

        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDenabled)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDrounddown)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDfontsize)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDfontoffset)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDpiconzoom)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.FHDadditionalfiles)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.STBDistance)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showCPULoad)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showRAMfree)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showCPUTemp)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showSYSTemp)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showChannelNumber)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showChannelName)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showInfoBarResolution)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showExtendedinfo)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.ExtendedinfoStyle)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showSnr)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showRecordstate)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showOrbitalposition)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showInfoBarClock)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showSTBinfo)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showMovieTime)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showPVRState)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showTunerinfo)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.setTunerAuto)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.setTunerManual)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.channelSelectionStyle)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showMovieName)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showEMCSelectionCover)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesign)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosX)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosY)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosX)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosY)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignSpace)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignInfobarColorGradient)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLUC)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLLC)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRUC)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRLC)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLH)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLV)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLUCheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLUCposz)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLLCheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignLLCposz)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRUCheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRUCposz)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRLCheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignRLCposz) 
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLHheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLHposx)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLHposy)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLHposz)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLVheight)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLVposx)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLVposy)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignOLVposz)
        self.setInputToDefault(config.plugins.MyMetrixLiteOther.SkinDesignExamples)

        self.save()

    def setInputToDefault(self, configItem):
        configItem.setValue(configItem.default)
