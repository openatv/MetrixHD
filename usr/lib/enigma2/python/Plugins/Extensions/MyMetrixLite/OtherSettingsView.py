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

from . import _, initOtherConfig, COLOR_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from enigma import ePicLoad
from os import path

#############################################################

class OtherSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteOtherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
    <widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="saveBtn" position="257,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
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
            "cancel": self.exit
        }, -1)

        self.onLayoutFinish.append(self.UpdatePicture)

    def __selectionChanged(self):
        cur = self["config"].getCurrent()
        cur = cur and len(cur) > 2 and cur[2]

        if cur == "ENABLED":
            self["config"].setList(self.getMenuItemList())

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

        list.append(getConfigListEntry(_("STB-Info   ------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show CPU-Load"), config.plugins.MyMetrixLiteOther.showCPULoad))
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
        list.append(getConfigListEntry(_("EMC/MoviePlayer   ------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show Clock"), config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer))
        list.append(getConfigListEntry(_("Show MovieName"), config.plugins.MyMetrixLiteOther.showMovieName))
        list.append(getConfigListEntry(_("Show STB-Info"), config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer))
        list.append(getConfigListEntry(_("EMC   ------------------------------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Show Cover in Media Center"),config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover))
        list.append(getConfigListEntry(_("Show Cover in Movie Selection"),config.plugins.MyMetrixLiteOther.showEMCSelectionCover))
        list.append(getConfigListEntry(_("ChannelSelection   -----------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("Channel selection style"), config.plugins.MyMetrixLiteOther.channelSelectionStyle))

        return list

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(COLOR_IMAGE_PATH % "MyMetrixLiteOther")

    def DecodePicture(self, PicInfo = ""):
        ptr = self.PicLoad.getData()
        self["helperimage"].instance.setPixmap(ptr)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyDown(self):
        self["config"].instance.moveSelection(self["config"].instance.moveDown)

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)

    def showInfo(self):
        self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

    def save(self):
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
