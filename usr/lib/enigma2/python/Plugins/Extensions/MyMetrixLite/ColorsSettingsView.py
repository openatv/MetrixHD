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

from . import _, initColorsConfig, appendSkinFile, SKIN_TARGET_TMP, SKIN_SOURCE, COLOR_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from skin import parseColor
from Components.Pixmap import Pixmap
from enigma import ePicLoad


#######################################################################

class ColorsSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteColorsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <eLabel position="60,55" size="500,50" text="MyMetrixLite - MetrixColors" font="Regular; 40" valign="center" transparent="1" backgroundColor="#00000000" />
    <widget name="config" position="61,114" size="590,500" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="70,640" size="160,30" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="257,640" size="160,30" text="Save" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="445,640" size="160,30" text="Defaults" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.picPath = COLOR_IMAGE_PATH % "FFFFFF"
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

        initColorsConfig()

        list = []
        list.append(getConfigListEntry(_("Text in background  -----------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("    Font color"), config.plugins.MyMetrixLiteColors.backgroundtext))
        list.append(getConfigListEntry(_("    Font color transparency"), config.plugins.MyMetrixLiteColors.backgroundtexttransparency))
        list.append(getConfigListEntry(_("Layer A (main layer)  -----------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("    Background"), ))
        list.append(getConfigListEntry(_("        Color"), config.plugins.MyMetrixLiteColors.layerabackground))
        list.append(getConfigListEntry(_("        Transparency"), config.plugins.MyMetrixLiteColors.layerabackgroundtransparency))
        list.append(getConfigListEntry(_("    Font color"), config.plugins.MyMetrixLiteColors.layeraforeground))
        list.append(getConfigListEntry(_("    Selection bar"), ))
        list.append(getConfigListEntry(_("        Background"), ))
        list.append(getConfigListEntry(_("            Color"), config.plugins.MyMetrixLiteColors.layeraselectionbackground))
        list.append(getConfigListEntry(_("            Transparency"), config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency))
        list.append(getConfigListEntry(_("        Font color"), config.plugins.MyMetrixLiteColors.layeraselectionforeground))
        list.append(getConfigListEntry(_("    Progress bar"), ))
        list.append(getConfigListEntry(_("        Color"), config.plugins.MyMetrixLiteColors.layeraprogress))
        list.append(getConfigListEntry(_("        Transparency"), config.plugins.MyMetrixLiteColors.layeraprogresstransparency))
        list.append(getConfigListEntry(_("    Accent colors"), ))
        list.append(getConfigListEntry(_("        Color 1"), config.plugins.MyMetrixLiteColors.layeraaccent1))
        list.append(getConfigListEntry(_("        Color 2"), config.plugins.MyMetrixLiteColors.layeraaccent2))
        list.append(getConfigListEntry(_("Layer B (secondary layer)  -----------------------------------------------------------------------------------"), ))
        list.append(getConfigListEntry(_("    Background"), ))
        list.append(getConfigListEntry(_("        Color"), config.plugins.MyMetrixLiteColors.layerbbackground))
        list.append(getConfigListEntry(_("        Transparency"), config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency))
        list.append(getConfigListEntry(_("    Font color"), config.plugins.MyMetrixLiteColors.layerbforeground))
        list.append(getConfigListEntry(_("    Selection bar"), ))
        list.append(getConfigListEntry(_("        Background"), ))
        list.append(getConfigListEntry(_("            Color"), config.plugins.MyMetrixLiteColors.layerbselectionbackground))
        list.append(getConfigListEntry(_("            Transparency"), config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency))
        list.append(getConfigListEntry(_("        Font color"), config.plugins.MyMetrixLiteColors.layerbselectionforeground))
        list.append(getConfigListEntry(_("    Progress bar"), ))
        list.append(getConfigListEntry(_("        Color"), config.plugins.MyMetrixLiteColors.layerbprogress))
        list.append(getConfigListEntry(_("        Transparency"), config.plugins.MyMetrixLiteColors.layerbprogresstransparency))
        list.append(getConfigListEntry(_("    Accent colors"), ))
        list.append(getConfigListEntry(_("        Color 1"), config.plugins.MyMetrixLiteColors.layerbaccent1))
        list.append(getConfigListEntry(_("        Color 2"), config.plugins.MyMetrixLiteColors.layerbaccent2))

        ConfigListScreen.__init__(self, list)

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
            "yellow": self.defaults,
            "green": self.save,
            "cancel": self.exit
        }, -1)

        self.onLayoutFinish.append(self.UpdatePicture)

    def GetPicturePath(self):
        try:
            returnValue = self["config"].getCurrent()[1].value
            path = COLOR_IMAGE_PATH % returnValue
            return path
        except:
            pass

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(self.GetPicturePath())

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

    def defaults(self):
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.backgroundtext)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.backgroundtexttransparency)

        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerabackground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerabackgroundtransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraforeground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraselectionbackground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraselectionforeground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraprogress)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraprogresstransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraaccent1)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layeraaccent2)

        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbbackground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbforeground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbselectionbackground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbselectionforeground)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbprogress)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbprogresstransparency)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbaccent1)
        self.setInputToDefault(config.plugins.MyMetrixLiteColors.layerbaccent2)

        self.save()

    def setInputToDefault(self, configItem):
        configItem.setValue(configItem.default)

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
