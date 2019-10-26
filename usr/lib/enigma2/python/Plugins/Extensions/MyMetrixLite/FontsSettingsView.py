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

from . import _, FONT_IMAGE_PATH, MAIN_IMAGE_PATH
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
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists

#######################################################################

class FontsSettingsView(ConfigListScreen, Screen):
	skin = """
	<screen name="MyMetrixLiteFontsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
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
		self.picPath = FONT_IMAGE_PATH % "FFFFFF"
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["helpertext"] = Label()

		self["titleText"] = StaticText("")
		self["titleText"].setText(_("Font settings"))

		self["cancelBtn"] = StaticText("")
		self["cancelBtn"].setText(_("Cancel"))

		self["saveBtn"] = StaticText("")
		self["saveBtn"].setText(_("Save"))

		self["defaultsBtn"] = StaticText("")
		self["defaultsBtn"].setText(_("Defaults"))

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

	def getMenuItemList(self):
		char = 150
		tab = " "*10
		sep = "-"
		list = []
		list.append(getConfigListEntry(_("Font Examples"),config.plugins.MyMetrixLiteFonts.SkinFontExamples, _("helptext"),"PRESET"))
		section = _("in Image included Fonts")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("LCD"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Lcd_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Lcd_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Replacement"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Replacement_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Replacement_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Console"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Console_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Console_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Fixed"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Fixed_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Fixed_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Arial"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Arial_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Arial_scale, _("helptext")))
		section = _("in Skin included Fonts")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Regular"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.Regular_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Regular_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("RegularLight"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.RegularLight_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.RegularLight_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("SetrixHD"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.SetrixHD_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.SetrixHD_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Meteo"), ))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.Meteo_scale, _("helptext")))
		section = _("-")
		list.append(getConfigListEntry(section + sep*(char-len(section)), ))
		section = _("Individual Settings (only for some individual skinned screens)")
		list.append(getConfigListEntry(section, ))
		section = _("-")
		list.append(getConfigListEntry(section + sep*(char-len(section)), ))
		section = _("Generally")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Screen title text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globaltitle_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globaltitle_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Button text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globalbutton_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globalbutton_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Clock text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globalclock_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globalclock_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Large text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globallarge_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globallarge_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Small text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globalsmall_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globalsmall_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Menu entry text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.globalmenu_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.globalmenu_scale, _("helptext")))
		section = _("Screens, Plugins")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Label text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.screenlabel_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.screenlabel_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Output text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.screentext_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.screentext_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Description text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.screeninfo_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.screeninfo_scale, _("helptext")))
		section = _("EPG, Channellist, Movielist")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Event name text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.epgevent_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.epgevent_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Other text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.epgtext_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.epgtext_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Description text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.epginfo_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.epginfo_scale, _("helptext")))
		section = _("Infobar, Moviebar")
		list.append(getConfigListEntry(section + tab + sep*(char-len(section)-len(tab)), ))
		list.append(getConfigListEntry(tab + _("Event name text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.infobarevent_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.infobarevent_scale, _("helptext")))
		list.append(getConfigListEntry(tab + _("Other text"), ))
		list.append(getConfigListEntry(tab*2 + _("Font type"), config.plugins.MyMetrixLiteFonts.infobartext_type, _("helptext")))
		list.append(getConfigListEntry(tab*2 + _("Font scale [%]"), config.plugins.MyMetrixLiteFonts.infobartext_scale, _("helptext")))

		return list

	def selectionChanged(self):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == "PRESET":
			self.getPreset()

		if cur == "ENABLED" or cur == "PRESET":
			self["config"].setList(self.getMenuItemList())
		self.ShowPicture()

	def getPreset(self):
		if config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_0":
			#system fonts
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 95
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 95
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 100
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 90
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 95
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 100
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 95
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 95
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 100
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 95
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 95
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 95
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 100
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 95
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_1":
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 100
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 100
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 105
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 105
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 105
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 105
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 100
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 105
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 100
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_2":
			if not path.exists("/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf") or not path.exists("/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"):
				self.showPresetError()
				return
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 105
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 100
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 105
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 105
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 110
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 95
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 110
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 95
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 105
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 105
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 105
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 120
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 115
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 105
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_3":
			if not path.exists("/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf") or not path.exists("/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf") or not path.exists("/usr/share/enigma2/MetrixHD/fonts/Raleway-Channel.ttf"):
				self.showPresetError()
				return
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 100
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 100
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 105
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 100
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 115
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Channel.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 95
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 100
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 105
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Channel.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 105
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 105
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 115
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 115
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 105
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_4":
			if not path.exists("/usr/share/enigma2/MetrixHD/fonts/digi.ttf"):
				self.showPresetError()
				return
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 75
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 75
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 75
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 100
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 115
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 120
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 115
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 85
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 75
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 85
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 135
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 115
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/digi.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 100
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_5":
			if not path.exists("/usr/share/enigma2/MetrixHD/fonts/analog.ttf"):
				self.showPresetError()
				return
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 100
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 100
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 100
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 105
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 105
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 100
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 115
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 115
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/analog.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 100
		elif config.plugins.MyMetrixLiteFonts.SkinFontExamples.value == "preset_6":
			if not path.exists("/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf") or not path.exists("/usr/share/enigma2/MetrixHD/fonts/HandelGotDBol.ttf") or not path.exists("/usr/share/fonts/nmsbd.ttf"):
				self.showPresetError()
				return
			config.plugins.MyMetrixLiteFonts.Lcd_type.value = "/usr/share/fonts/lcd.ttf"
			config.plugins.MyMetrixLiteFonts.Lcd_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Replacement_type.value = "/usr/share/fonts/ae_AlMateen.ttf"
			config.plugins.MyMetrixLiteFonts.Replacement_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Console_type.value = "/usr/share/fonts/tuxtxt.ttf"
			config.plugins.MyMetrixLiteFonts.Console_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Fixed_type.value = "/usr/share/fonts/andale.ttf"
			config.plugins.MyMetrixLiteFonts.Fixed_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Arial_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.Arial_scale.value = 100
			#skin fonts
			config.plugins.MyMetrixLiteFonts.Regular_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.Regular_scale.value = 100
			config.plugins.MyMetrixLiteFonts.RegularLight_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.RegularLight_scale.value = 100
			config.plugins.MyMetrixLiteFonts.SetrixHD_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value = 100
			config.plugins.MyMetrixLiteFonts.Meteo_scale.value = 105
			#global
			config.plugins.MyMetrixLiteFonts.globaltitle_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.globaltitle_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalbutton_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.globalbutton_scale.value = 95
			config.plugins.MyMetrixLiteFonts.globalclock_type.value = "/usr/share/fonts/nmsbd.ttf"
			config.plugins.MyMetrixLiteFonts.globalclock_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globallarge_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.globallarge_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalsmall_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.globalsmall_scale.value = 100
			config.plugins.MyMetrixLiteFonts.globalmenu_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotDBol.ttf"
			config.plugins.MyMetrixLiteFonts.globalmenu_scale.value = 100
			#screens
			config.plugins.MyMetrixLiteFonts.screenlabel_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.screenlabel_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screentext_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.screentext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.screeninfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.screeninfo_scale.value = 115
			#channellist
			config.plugins.MyMetrixLiteFonts.epgevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.epgevent_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epgtext_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.epgtext_scale.value = 100
			config.plugins.MyMetrixLiteFonts.epginfo_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.epginfo_scale.value = 115
			#infobar
			config.plugins.MyMetrixLiteFonts.infobarevent_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.infobarevent_scale.value = 105
			config.plugins.MyMetrixLiteFonts.infobartext_type.value = "/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf"
			config.plugins.MyMetrixLiteFonts.infobartext_scale.value = 100

	def GetPicturePath(self):
		returnValue = str(self["config"].getCurrent()[1].value).split('/')[-1]
		if len(returnValue) <= 3:
			returnValue = "scale_75-100-125"
		picturepath = resolveFilename(SCOPE_CURRENT_SKIN, "mymetrixlite/fonts/%s.png" % returnValue)
		if not fileExists(picturepath):
			picturepath = FONT_IMAGE_PATH % returnValue
			if not fileExists(picturepath):
				picturepath = resolveFilename(SCOPE_CURRENT_SKIN, "mymetrixlite/MyMetrixLiteFont.png")
				if not fileExists(picturepath):
					picturepath = MAIN_IMAGE_PATH % "MyMetrixLiteFont"
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
			self["config"].setList(self.getMenuItemList())
			self.ShowPicture()

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

	def showPresetError(self):
		self.session.open(MessageBox, _("Error creating Preset! One or more Fonts are not available!"), MessageBox.TYPE_ERROR)

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
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")
