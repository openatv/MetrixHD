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

from . import _, COLOR_IMAGE_PATH, MAIN_IMAGE_PATH, ColorList, TransparencyList
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from skin import parseColor
from Components.Pixmap import Pixmap
from enigma import ePicLoad, eTimer
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

		
		self.refreshTimer = eTimer()
		self.refreshTimer.callback.append(self.refreshList)

		self.initQuickColorSetup()

		ConfigListScreen.__init__(
			self,
			self.getMenuItemList(),
			session = session,
			on_change = self.selectionChanged
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

	def initQuickColorSetup(self):
		self.colorA = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layerabackground.value, choices = ColorList)
		self.colorAtransparency = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value, choices = TransparencyList)
		self.colorAfont = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layeraforeground.value, choices = ColorList)
		self.colorB = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layerbbackground.value, choices = ColorList)
		self.colorBtransparency = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value, choices = TransparencyList)
		self.colorBfont = ConfigSelection(default=config.plugins.MyMetrixLiteColors.layerbforeground.value, choices = ColorList)

	def getMenuItemList(self):
		char = 150
		tab = " "*10
		sep = "-"
		list = []
		list.append(getConfigListEntry(_("Color Examples"),config.plugins.MyMetrixLiteColors.SkinColorExamples, _("helptext"), "PRESET"))
		section = _("Quick Setup")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Left"), ))
		list.append(getConfigListEntry(tab*2 + _("Background"), self.colorA, _("helptext"), "QUICKCOLOR"))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), self.colorAtransparency, _("helptext"), "QUICKCOLOR"))
		list.append(getConfigListEntry(tab*2 + _("Font color"), self.colorAfont, _("helptext"), "QUICKCOLOR"))
		list.append(getConfigListEntry(tab + _("Right"), ))
		list.append(getConfigListEntry(tab*2 + _("Background"), self.colorB, _("helptext"), "QUICKCOLOR"))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), self.colorBtransparency, _("helptext"), "QUICKCOLOR"))
		list.append(getConfigListEntry(tab*2 + _("Font color"), self.colorBfont, _("helptext"), "QUICKCOLOR"))
		section = _("Scrollbar Slider")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Slider"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.scrollbarSlidercolor, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.scrollbarSlidertransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Border"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.scrollbarSliderbordercolor, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.scrollbarSliderbordertransparency, _("helptext")))
		section = _("Color Gradient")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Color"), config.plugins.MyMetrixLiteColors.cologradient, _("helptext")))
		list.append(getConfigListEntry(tab + _("Position"), config.plugins.MyMetrixLiteColors.cologradient_position, _("helptext")))
		list.append(getConfigListEntry(tab + _("Size"), config.plugins.MyMetrixLiteColors.cologradient_size, _("helptext")))
		list.append(getConfigListEntry(tab + 'A ' +_("Transparency"), config.plugins.MyMetrixLiteColors.cologradient_transparencyA, _("helptext"), "TRANSPARENCYA"))
		list.append(getConfigListEntry(tab + 'B ' +_("Transparency"), config.plugins.MyMetrixLiteColors.cologradient_transparencyB, _("helptext"), "TRANSPARENCYB"))
		list.append(getConfigListEntry(tab + _("Show Background"), config.plugins.MyMetrixLiteColors.cologradient_show_background, _("helptext")))
		section = _("Text Windowtitle")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Foreground"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.windowtitletext, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.windowtitletexttransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.windowtitletextback, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency, _("helptext")))
		section = _("Text in background")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Foreground"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.backgroundtext, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.backgroundtexttransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.backgroundtextback, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Border"), ))
		list.append(getConfigListEntry(tab*2 + _("Width"), config.plugins.MyMetrixLiteColors.backgroundtextborderwidth, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.backgroundtextbordercolor, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.backgroundtextbordertransparency, _("helptext")))
		section = _("Menu")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.menubackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.menubackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.menufont, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.menufontselected, _("helptext")))
		list.append(getConfigListEntry(tab + _("Menu Symbol"), ))
		list.append(getConfigListEntry(tab*2 + _("Background"), ))
		list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.menusymbolbackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency, _("helptext")))
		section = _("Infobar, Moviebar")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.infobarbackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Progress bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.infobarprogress, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.infobarprogresstransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Font color"), ))
		list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.infobarfont1, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.infobarfont2, _("helptext")))
		list.append(getConfigListEntry(tab + _("Accent colors"), ))
		list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.infobaraccent1, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.infobaraccent2, _("helptext")))
		list.append(getConfigListEntry(tab + _("Extended Info colors"), ))
		list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layeraextendedinfo1, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layeraextendedinfo2, _("helptext")))
		section = _("Clock, Weather and Buttons")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Clock in Layer A"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraclockforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Clock in Layer B"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbclockforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Buttons"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.buttonforeground, _("helptext")))
		section = _("Layer A (main layer)")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerabackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerabackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Screen title separating line"), ))
		list.append(getConfigListEntry(tab*2 + _("Show also in main layer?"), config.plugins.MyMetrixLiteOther.layeraunderlineshowmainlayer, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("height"), config.plugins.MyMetrixLiteOther.layeraunderlinesize, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("pos y"), config.plugins.MyMetrixLiteOther.layeraunderlineposy, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layeraunderline, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layeraunderlinetransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Selection bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layeraselectionbackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layeraselectionforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Progress bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layeraprogress, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layeraprogresstransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Accent colors"), ))
		list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layeraaccent1, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layeraaccent2, _("helptext")))
		section = _("Layer B (secondary layer)")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbbackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Selection bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbselectionbackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.layerbselectionforeground, _("helptext")))
		list.append(getConfigListEntry(tab + _("Progress bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.layerbprogress, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.layerbprogresstransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Accent colors"), ))
		list.append(getConfigListEntry(tab*2 + _("Color 1"), config.plugins.MyMetrixLiteColors.layerbaccent1, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Color 2"), config.plugins.MyMetrixLiteColors.layerbaccent2, _("helptext")))
		section = _("Graphical EPG") + " " +  _("and") + " " + _("Vertical EPG")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Background"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.epgbackground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Borderlines"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.epgborderlines, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgborderlinestransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Time Line"), ))
		list.append(getConfigListEntry(tab*3 + _("Font color"), config.plugins.MyMetrixLiteColors.epgtimelineforeground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Background") + " " + _("(Text-Mode)"), ))
		list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.epgtimelinebackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Primetime"), ))
		list.append(getConfigListEntry(tab*3 + _("Font color"), config.plugins.MyMetrixLiteColors.epgprimetimeforeground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Background") + " " + _("(Text-Mode)"), ))
		list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.epgprimetimebackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgprimetimebackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Service List"), ))
		list.append(getConfigListEntry(tab*3 + _("Font color"), config.plugins.MyMetrixLiteColors.epgserviceforeground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Font color") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgservicenowforeground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Background") + " " + _("(Text-Mode)"), ))
		list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.epgservicebackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Color") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgservicenowbackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Event List"), ))
		list.append(getConfigListEntry(tab*3 + _("Font color"), config.plugins.MyMetrixLiteColors.epgeventforeground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Font color") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgeventnowforeground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Font color selected"), config.plugins.MyMetrixLiteColors.epgeventselectedforeground, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Background") + " " + _("(Text-Mode)"), ))
		list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.epgeventbackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Color") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgeventnowbackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency") + " " + _("now"), config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Color") + " " + _("selected"), config.plugins.MyMetrixLiteColors.epgeventselectedbackground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Transparency") + " " + _("selected"), config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency, _("helptext")))
		list.append(getConfigListEntry(tab + _("Event Description"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Background"), ))
		list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground, _("helptext")))
		list.append(getConfigListEntry(tab*4 + _("Transparency"), config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency, _("helptext")))
		section = _("Channelselection")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Service"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.channelselectionservice, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.channelselectionserviceselected, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color recording"), config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color pseudo recording"), config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color streaming"), config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed, _("helptext")))
		list.append(getConfigListEntry(tab + _("Service Description"), ))
		list.append(getConfigListEntry(tab*2 + _("Font color"), config.plugins.MyMetrixLiteColors.channelselectionservicedescription, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font color selected"), config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected, _("helptext")))
		list.append(getConfigListEntry(tab + _("Progress bar"), ))
		list.append(getConfigListEntry(tab*2 + _("Color"), config.plugins.MyMetrixLiteColors.channelselectionprogress, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Border color"), config.plugins.MyMetrixLiteColors.channelselectionprogressborder, _("helptext")))
		section = _("EMC Movie List")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Watched color"), config.plugins.MyMetrixLiteColors.emcWatchingColor, _("helptext")))
		list.append(getConfigListEntry(tab + _("Finished color"), config.plugins.MyMetrixLiteColors.emcFinishedColor, _("helptext")))
		list.append(getConfigListEntry(tab + _("Recording color"), config.plugins.MyMetrixLiteColors.emcRecordingColor, _("helptext")))
		list.append(getConfigListEntry(tab + _("Show event colors if entry selected"), config.plugins.MyMetrixLiteColors.emcCoolHighlightColor, _("helptext")))
		section = _("Skin Design")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Border lines"), ))
		list.append(getConfigListEntry(tab*2 + _("Screens"), ))
		list.append(getConfigListEntry(tab*3 + _("Top"), config.plugins.MyMetrixLiteColors.windowborder_top, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Bottom"), config.plugins.MyMetrixLiteColors.windowborder_bottom, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Left"), config.plugins.MyMetrixLiteColors.windowborder_left, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Right"), config.plugins.MyMetrixLiteColors.windowborder_right, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Selection bar"), ))
		list.append(getConfigListEntry(tab*3 + _("Top"), config.plugins.MyMetrixLiteColors.listboxborder_topwidth, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteColors.listboxborder_topwidth.value != "no":
			list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_top, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Bottom"), config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth.value != "no":
			list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_bottom, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Left"), config.plugins.MyMetrixLiteColors.listboxborder_leftwidth, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteColors.listboxborder_leftwidth.value != "no":
			list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_left, _("helptext")))
		list.append(getConfigListEntry(tab*3 + _("Right"), config.plugins.MyMetrixLiteColors.listboxborder_rightwidth, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteColors.listboxborder_rightwidth.value != "no":
			list.append(getConfigListEntry(tab*4 + _("Color"), config.plugins.MyMetrixLiteColors.listboxborder_right, _("helptext")))
		list.append(getConfigListEntry(tab + _("Additional Layer"),))
		list.append(getConfigListEntry(tab*2 + _("Skin Design Examples"),config.plugins.MyMetrixLiteOther.SkinDesignExamples, _("helptext"), "PRESET2"))
		list.append(getConfigListEntry(tab*2 + _("Show upper left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLUC, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignLUC.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.upperleftcornerbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.upperleftcornertransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignLUCheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLUCposz, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Show lower left Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignLLC, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignLLC.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.lowerleftcornerbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.lowerleftcornertransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignLLCheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignLLCposz, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Show upper right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRUC, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignRUC.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.upperrightcornerbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.upperrightcornertransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignRUCheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRUCposz, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Show lower right Corner Layer"),config.plugins.MyMetrixLiteOther.SkinDesignRLC, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignRLC.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.lowerrightcornerbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.lowerrightcornertransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignRLCheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignRLCposz, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Show optional horizontal Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLH, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignOLH.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignOLHheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposx, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposy, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLHposz, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Show optional vertical Layer"),config.plugins.MyMetrixLiteOther.SkinDesignOLV, _("helptext"), "ENABLED"))
		if config.plugins.MyMetrixLiteOther.SkinDesignOLV.getValue() is not "no":
			list.append(getConfigListEntry(tab*3 + _("Color"), config.plugins.MyMetrixLiteColors.optionallayerverticalbackground, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("Transparency"), config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("width"), config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("height"), config.plugins.MyMetrixLiteOther.SkinDesignOLVheight, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos x"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposx, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos y"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposy, _("helptext")))
			list.append(getConfigListEntry(tab*3 + _("pos z"), config.plugins.MyMetrixLiteOther.SkinDesignOLVposz, _("helptext")))

		return list

	def selectionChanged(self):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == "PRESET":
			self.getPreset()
		elif cur == "PRESET2":
			self.getPreset2()
		elif cur == "QUICKCOLOR":
			self.setQuickColor()
		elif (cur == "TRANSPARENCYA" or cur == "TRANSPARENCYB") and int(config.plugins.MyMetrixLiteColors.cologradient_transparencyA.value, 16) > int(config.plugins.MyMetrixLiteColors.cologradient_transparencyB.value, 16):
			if cur == "TRANSPARENCYA":
				config.plugins.MyMetrixLiteColors.cologradient_transparencyA.value = config.plugins.MyMetrixLiteColors.cologradient_transparencyB.value
			else:
				config.plugins.MyMetrixLiteColors.cologradient_transparencyB.value = config.plugins.MyMetrixLiteColors.cologradient_transparencyA.value

		if cur == "ENABLED" or cur == "PRESET" or cur == "PRESET2" or cur == "QUICKCOLOR":
			self.refreshTimer.start(1000, True)
		self.ShowPicture()

	def refreshList(self):
		self["config"].setList(self.getMenuItemList())

	def setQuickColor(self):

		config.plugins.MyMetrixLiteColors.menufont.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.menufontselected.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.menubackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.menusymbolbackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.infobarbackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.infobarprogress.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value = self.colorAtransparency.value

		config.plugins.MyMetrixLiteColors.channelselectionservice.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value = self.colorAfont.value

		config.plugins.MyMetrixLiteColors.windowtitletext.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.windowtitletextback.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.backgroundtext.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.backgroundtextback.value = self.colorAfont.value

		config.plugins.MyMetrixLiteColors.layeraclockforeground.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.layerbclockforeground.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.buttonforeground.value = self.colorAfont.value

		config.plugins.MyMetrixLiteColors.layerabackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.layeraforeground.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.layeraselectionbackground.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.layeraselectionforeground.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.layeraprogress.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value = self.colorAtransparency.value

		config.plugins.MyMetrixLiteColors.layerbbackground.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value = self.colorBtransparency.value
		config.plugins.MyMetrixLiteColors.layerbforeground.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.layerbselectionbackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value = self.colorBtransparency.value
		config.plugins.MyMetrixLiteColors.layerbselectionforeground.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.layerbprogress.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value = self.colorBtransparency.value

		config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = self.colorBtransparency.value
		config.plugins.MyMetrixLiteColors.epgbackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.epgeventforeground.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.epgeventbackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = self.colorAtransparency.value
		config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = self.colorBfont.value
		config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = self.colorB.value
		config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = self.colorBtransparency.value
		config.plugins.MyMetrixLiteColors.epgserviceforeground.value = self.colorAfont.value
		config.plugins.MyMetrixLiteColors.epgservicebackground.value = self.colorA.value
		config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = self.colorAtransparency.value

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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "27408B"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "27408B"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "27408B"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#BDBDBD"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "1A"

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
			config.plugins.MyMetrixLiteColors.menufont.value = "1C1C1C"
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
			config.plugins.MyMetrixLiteColors.infobarfont2.value = "6E6E6E"
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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "1C1C1C"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "F2F2F2"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "6E6E6E"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "D8D8D8"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "1C1C1C"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "D8D8D8"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "1C1C1C"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "D8D8D8"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "F2F2F2"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "6E6E6E"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "1C1C1C"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "D8D8D8"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "F2F2F2"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "6E6E6E"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "F0A30A"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "6E6E6E"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#6E6E6E"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "1A"

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
			config.plugins.MyMetrixLiteColors.menusymbolbackground.value = "0F0F0F"
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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "27408B"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "27408B"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#6E6E6E"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "4D"

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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "911D10"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "911D10"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "911D10"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#6E6E6E"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "4D"

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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "BF9217"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "BF9217"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "BF9217"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "4D"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#6E6E6E"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "4D"

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
			config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value = "00"
			config.plugins.MyMetrixLiteColors.windowtitletextback.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value = "00"
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
			config.plugins.MyMetrixLiteColors.layeraunderline.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value = "00"

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

			config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value = "70AD11"
			config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventnowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventnowbackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value = "70AD11"
			config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgserviceforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicebackground.value = "000000"
			config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgservicenowforeground.value = "FFFFFF"
			config.plugins.MyMetrixLiteColors.epgservicenowbackground.value = "70AD11"
			config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgtimelineforeground.value = "BDBDBD"
			config.plugins.MyMetrixLiteColors.epgtimelinebackground.value = "0F0F0F"
			config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value = "1A"
			config.plugins.MyMetrixLiteColors.epgborderlines.value = "#6E6E6E"
			config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value = "1A"

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

		self.colorA.value = config.plugins.MyMetrixLiteColors.layerabackground.value
		self.colorAtransparency.value = config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value
		self.colorAfont.value = config.plugins.MyMetrixLiteColors.layeraforeground.value
		self.colorB.value = config.plugins.MyMetrixLiteColors.layerbbackground.value
		self.colorBtransparency.value = config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value
		self.colorBfont.value = config.plugins.MyMetrixLiteColors.layerbforeground.value

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

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def defaults(self, SAVE = False):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				if SAVE: x[1].save()
		if self.session:
			self.refreshList()
			self.ShowPicture()

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

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

		configfile.save()
		self.exit()

	def exit(self):
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
		self.close()

	def showHelperText(self):
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")
