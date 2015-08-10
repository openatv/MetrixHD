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

from . import _, initColorsConfig, initOtherConfig, getHelperText, appendSkinFile, SKIN_TARGET_TMP, SKIN_SOURCE, COLOR_IMAGE_PATH, MAIN_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from skin import parseColor
from Components.Pixmap import Pixmap
from enigma import ePicLoad
from os import path

#######################################################################

class ColorsSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteColorsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
    <widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="saveBtn" position="257,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="defaultsBtn" position="445,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
    <widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.picPath = COLOR_IMAGE_PATH % "FFFFFF"
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()
        self["helpertext"] = Label()

        self["titleText"] = StaticText("")
        self["titleText"].setText(_("Color settings"))

        self["cancelBtn"] = StaticText("")
        self["cancelBtn"].setText(_("Cancel"))

        self["saveBtn"] = StaticText("")
        self["saveBtn"].setText(_("Save"))

        self["defaultsBtn"] = StaticText("")
        self["defaultsBtn"].setText(_("Defaults"))

        initColorsConfig()
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
            "yellow": self.defaults,
            "green": self.save,
            "cancel": self.exit
        }, -1)

        self.onLayoutFinish.append(self.UpdatePicture)

    def getMenuItemList(self):
        char = 150
        tab = " "*10
        sep = "-"
        list = []
        list.append(getConfigListEntry(_("Color Examples"),config.plugins.MyMetrixLiteColors.SkinColorExamples, "PRESET"))
        section = _("Text Windowtitle")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Foreground"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.windowtitletext))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.windowtitletexttransparency))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.windowtitletextback))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency))
        section = _("Text in background")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Foreground"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.backgroundtext))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.backgroundtexttransparency))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.backgroundtextback))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency))
        section = _("Menu")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.menubackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.menubackgroundtransparency))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.menufont))
        list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.menufontselected))
        list.append(getConfigListEntry(tab + _("Menu Symbol"), ))
        list.append(getConfigListEntry(tab*2 + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.menusymbolbackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency))
        section = _("Infobar, Moviebar")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.infobarbackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency))
        list.append(getConfigListEntry(tab + _("Progress bar"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.infobarprogress))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.infobarprogresstransparency))
        list.append(getConfigListEntry(tab + _("Font color"), ))
        list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.infobarfont1))
        list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.infobarfont2))
        list.append(getConfigListEntry(tab + _("Accent colors"), ))
        list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.infobaraccent1))
        list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.infobaraccent2))
        section = _("Clock, Weather and Buttons")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Clock in Layer A"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraclockforeground))
        list.append(getConfigListEntry(tab + _("Clock in Layer B"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbclockforeground))
        list.append(getConfigListEntry(tab + _("Buttons"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.buttonforeground))
        section = _("Layer A (main layer)")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerabackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerabackgroundtransparency))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraforeground))
        list.append(getConfigListEntry(tab + _("Selection bar"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layeraselectionbackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraselectionforeground))
        list.append(getConfigListEntry(tab + _("Progress bar"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layeraprogress))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layeraprogresstransparency))
        list.append(getConfigListEntry(tab + _("Accent colors"), ))
        list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layeraaccent1))
        list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layeraaccent2))
        list.append(getConfigListEntry(tab + _("Extended Info colors"), ))
        list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layeraextendedinfo1))
        list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layeraextendedinfo2))
        section = _("Layer B (secondary layer)")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Background"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbbackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbforeground))
        list.append(getConfigListEntry(tab + _("Selection bar"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbselectionbackground))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbselectionforeground))
        list.append(getConfigListEntry(tab + _("Progress bar"), ))
        list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbprogress))
        list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbprogresstransparency))
        list.append(getConfigListEntry(tab + _("Accent colors"), ))
        list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layerbaccent1))
        list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layerbaccent2))
        section = _("Graphical EPG")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Event Description"), ))
        list.append(getConfigListEntry(tab*2 + _("Background"), ))
        list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground))
        list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency))
        list.append(getConfigListEntry(tab*3 + _("Font color"), config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground))
        list.append(getConfigListEntry(tab + _("Event List"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.epgeventforeground))
        list.append(getConfigListEntry(tab + _("Time Line"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.epgtimelineforeground))
        section = _("Channelselection")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Service"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.channelselectionservice))
        list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.channelselectionserviceselected))
        list.append(getConfigListEntry(tab*2 + _("Font color recording"), config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded))
        list.append(getConfigListEntry(tab*2 + _("Font color pseudo recording"), config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded))
        list.append(getConfigListEntry(tab*2 + _("Font color streaming"), config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed))
        list.append(getConfigListEntry(tab + _("Service Description"), ))
        list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.channelselectionservicedescription))
        list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected))
        section = _("EMC Movie List")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Watched color"), config.plugins.MyMetrixLiteColors.emcWatchingColor))
        list.append(getConfigListEntry(tab + _("Finished color"), config.plugins.MyMetrixLiteColors.emcFinishedColor))
        list.append(getConfigListEntry(tab + _("Recording color"), config.plugins.MyMetrixLiteColors.emcRecordingColor))
        list.append(getConfigListEntry(tab + _("Show event colors if entry selected"), config.plugins.MyMetrixLiteColors.emcCoolHighlightColor))
        section = _("Skin Design")
        list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
        list.append(getConfigListEntry(tab + _("Border lines"), ))
        list.append(getConfigListEntry(tab*2 + _("Selection bar"), ))
        list.append(getConfigListEntry(tab*3 + _("Top"), config.plugins.MyMetrixLiteColors.listboxborder_topwidth, "ENABLED"))
        if config.plugins.MyMetrixLiteColors.listboxborder_topwidth.value != "no":
            list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_top))
        list.append(getConfigListEntry(tab*3 + _("Bottom"), config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth, "ENABLED"))
        if config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth.value != "no":
            list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_bottom))
        list.append(getConfigListEntry(tab*3 + _("Left"), config.plugins.MyMetrixLiteColors.listboxborder_leftwidth, "ENABLED"))
        if config.plugins.MyMetrixLiteColors.listboxborder_leftwidth.value != "no":
            list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_left))
        list.append(getConfigListEntry(tab*3 + _("Right"), config.plugins.MyMetrixLiteColors.listboxborder_rightwidth, "ENABLED"))
        if config.plugins.MyMetrixLiteColors.listboxborder_rightwidth.value != "no":
            list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_right))
        list.append(getConfigListEntry(tab + _("Additional Layer"),))
        list.append(getConfigListEntry(tab*2 + _("Skin Design Examples"),config.plugins.MyMetrixLiteOther.SkinDesignExamples, "PRESET2"))
        list.append(getConfigListEntry(tab*2 + _("Show upper left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLUC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignLUC.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.upperleftcornerbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.upperleftcornertransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignLUCheight))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLUCposz))
        list.append(getConfigListEntry(tab*2 + _("Show lower left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLLC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignLLC.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.lowerleftcornerbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.lowerleftcornertransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignLLCheight))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLLCposz))
        list.append(getConfigListEntry(tab*2 + _("Show upper right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRUC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignRUC.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.upperrightcornerbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.upperrightcornertransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignRUCheight))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRUCposz))
        list.append(getConfigListEntry(tab*2 + _("Show lower right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRLC, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignRLC.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.lowerrightcornerbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.lowerrightcornertransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignRLCheight))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRLCposz))
        list.append(getConfigListEntry(tab*2 + _("Show optional horizontal Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLH, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignOLH.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignOLHheight))
            list.append(getConfigListEntry(tab*3 + _("pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposx))
            list.append(getConfigListEntry(tab*3 + _("pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposy))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposz))
        list.append(getConfigListEntry(tab*2 + _("Show optional vertical Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLV, "ENABLED"))
        if config.plugins.MyMetrixLiteOther.SkinDesignOLV.getValue() is not "no":
            list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.optionallayerverticalbackground))
            list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency))
            list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth))
            list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignOLVheight))
            list.append(getConfigListEntry(tab*3 + _("pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposx))
            list.append(getConfigListEntry(tab*3 + _("pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposy))
            list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposz))

        return list

    def __selectionChanged(self):
        cur = self["config"].getCurrent()
        cur = cur and len(cur) > 2 and cur[2]

        if cur == "PRESET":
            self.getPreset()
        elif cur == "PRESET2":
            self.getPreset2()

        if cur == "ENABLED" or cur == "PRESET" or cur == "PRESET2":
            self["config"].setList(self.getMenuItemList())

    def getPreset(self):
        if config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_0":
        #standard colors
            config.plugins.MyMetrixLiteColors.menufont.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menubackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "D8C100"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "5FA816"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = True

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "34"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "67"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "FFFFFF"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "1A"
        elif config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_1":
        #bright colors
            config.plugins.MyMetrixLiteColors.menufont.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menubackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "424242"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "F0A30A"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "008A00"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = True

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "424242"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "424242"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "34"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "67"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "424242"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "F2F2F2"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "D8D8D8"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "1A"
        elif config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_2":
        #dark colors
            config.plugins.MyMetrixLiteColors.menufont.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menubackground.value = "000000"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "D8C100"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "5FA816"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = True

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "F0A30A"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "F0A30A"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "67"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "9A"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "CD"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "F0A30A"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "F0A30A"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "27408B"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "27408B"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "0F0F0F"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "4D"
        elif config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_3":
        #red colors
            config.plugins.MyMetrixLiteColors.menufont.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menubackground.value = "000000"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "911D10"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "D8C100"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "5FA816"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = False

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "67"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "9A"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "CD"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "BDBDBD"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "911D10"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "4D"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "911D10"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "4D"
        elif config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_4":
        #yellow colors
            config.plugins.MyMetrixLiteColors.menufont.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "000000"
            config.plugins.MyMetrixLiteColors.menubackground.value = "000000"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "BF9217"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "000000"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "1C1C1C"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "D8C100"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "5FA816"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = False

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "BF9217"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "BF9217"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "67"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "9A"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "CD"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "000000"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "BF9217"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "000000"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "BF9217"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "BF9217"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "BF9217"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "BF9217"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "1A"
        elif config.plugins.MyMetrixLiteColors.SkinColorExamples.value == "preset_5":
        #green colors
            config.plugins.MyMetrixLiteColors.menufont.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menufontselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.menubackground.value = "000000"
            config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "70AD11"
            config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarprogress.value = "70AD11"
            config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.infobarfont1.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.infobarfont2.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.infobaraccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.channelselectionservice.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value = "70AD11"
            config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value = "E51400"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value = "0000CD"
            config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value = "C3461B"

            config.plugins.MyMetrixLiteColors.emcWatchingColor.value = "D8C100"
            config.plugins.MyMetrixLiteColors.emcFinishedColor.value = "5FA816"
            config.plugins.MyMetrixLiteColors.emcRecordingColor.value = "E51400"
            config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.value = False

            config.plugins.MyMetrixLiteColors.windowtitletext.value = "70AD11"
            config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "34"
            config.plugins.MyMetrixLiteColors.windowtitletextback.value = "70AD11"
            config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "67"
            config.plugins.MyMetrixLiteColors.backgroundtext.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value = "9A"
            config.plugins.MyMetrixLiteColors.backgroundtextback.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value = "CD"

            config.plugins.MyMetrixLiteColors.layeraclockforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbclockforeground.value = "F2F2F2"
            config.plugins.MyMetrixLiteColors.buttonforeground.value = "70AD11"

            config.plugins.MyMetrixLiteColors.layerabackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = "70AD11"
            config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layeraprogress.value = "70AD11"
            config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layeraaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layeraaccent2.value = "6E6E6E"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value = "70AD11"
            config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.layerbbackground.value = "70AD11"
            config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogress.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.layerbaccent1.value = "BDBDBD"
            config.plugins.MyMetrixLiteColors.layerbaccent2.value = "6E6E6E"

            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
            config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "70AD11"

            config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value = "00008B"
            config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value = "00008B"
            config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value = "000000"
            config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value = "00008B"
            config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value = "1A"
            config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value = "00008B"
            config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value = "1A"

    def getPreset2(self):
        # skin design preset (additional layer)
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

    def GetPicturePath(self):
        try:
            returnValue = self["config"].getCurrent()[1].value
            picturepath = COLOR_IMAGE_PATH % returnValue
            if not path.exists(picturepath):
                picturepath = MAIN_IMAGE_PATH % "MyMetrixLiteColor"
        except:
            picturepath = MAIN_IMAGE_PATH % "MyMetrixLiteColor"
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
        for x in self["config"].list:
            if len(x) > 1:
                self.setInputToDefault(x[1])
        self["config"].setList(self.getMenuItemList())
        self.ShowPicture()
        #self.save()

    def setInputToDefault(self, configItem):
        configItem.setValue(configItem.default)

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
        self.close()
    
    def showHelperText(self):
		text = getHelperText(self["config"].getCurrent()[1])
		self["helpertext"].setText(text)