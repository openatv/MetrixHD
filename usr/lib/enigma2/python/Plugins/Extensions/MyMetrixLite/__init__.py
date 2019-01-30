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

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigNumber, ConfigSelectionNumber, ConfigYesNo, ConfigText, ConfigInteger
from os import path
import gettext
from enigma import getBoxType
#############################################################

PLUGIN_PATH = resolveFilename(SCOPE_PLUGINS, "Extensions/MyMetrixLite")

#############################################################

# Gettext

PluginLanguageDomain = "MyMetrixLite"

def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, PLUGIN_PATH + "/locale")

def _(txt):
	if gettext.dgettext(PluginLanguageDomain, txt):
		return gettext.dgettext(PluginLanguageDomain, txt)
	else:
		return gettext.gettext(txt)

language.addCallback(localeInit())

#############################################################

SKIN_SOURCE = "/usr/share/enigma2/MetrixHD/skin.xml"
SKIN_TARGET = "/usr/share/enigma2/MetrixHD/skin.MySkin.xml"
SKIN_TARGET_TMP = SKIN_TARGET + ".tmp"

SKIN_TEMPLATES_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00_templates.xml"
SKIN_TEMPLATES_TARGET = "/usr/share/enigma2/MetrixHD/skin_00_templates.MySkin.xml"
SKIN_TEMPLATES_TARGET_TMP = SKIN_TEMPLATES_TARGET + ".tmp"

SKIN_INFOBAR_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00a_InfoBar.xml"
SKIN_INFOBAR_TARGET = "/usr/share/enigma2/MetrixHD/skin_00a_InfoBar.MySkin.xml"
SKIN_INFOBAR_TARGET_TMP = SKIN_INFOBAR_TARGET + ".tmp"

SKIN_SECOND_INFOBAR_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00b_SecondInfoBar.xml"
SKIN_SECOND_INFOBAR_TARGET = "/usr/share/enigma2/MetrixHD/skin_00b_SecondInfoBar.MySkin.xml"
SKIN_SECOND_INFOBAR_TARGET_TMP = SKIN_SECOND_INFOBAR_TARGET + ".tmp"

SKIN_SECOND_INFOBAR_ECM_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00c_SecondInfoBarECM.xml"
SKIN_SECOND_INFOBAR_ECM_TARGET = "/usr/share/enigma2/MetrixHD/skin_00c_SecondInfoBarECM.MySkin.xml"
SKIN_SECOND_INFOBAR_ECM_TARGET_TMP = SKIN_SECOND_INFOBAR_ECM_TARGET + ".tmp"

SKIN_INFOBAR_LITE_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00d_InfoBarLite.xml"
SKIN_INFOBAR_LITE_TARGET = "/usr/share/enigma2/MetrixHD/skin_00d_InfoBarLite.MySkin.xml"
SKIN_INFOBAR_LITE_TARGET_TMP = SKIN_INFOBAR_LITE_TARGET + ".tmp"

SKIN_CHANNEL_SELECTION_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00e_ChannelSelection.xml"
SKIN_CHANNEL_SELECTION_TARGET = "/usr/share/enigma2/MetrixHD/skin_00e_ChannelSelection.MySkin.xml"
SKIN_CHANNEL_SELECTION_TARGET_TMP = SKIN_CHANNEL_SELECTION_TARGET + ".tmp"

SKIN_MOVIEPLAYER_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00f_MoviePlayer.xml"
SKIN_MOVIEPLAYER_TARGET = "/usr/share/enigma2/MetrixHD/skin_00f_MoviePlayer.MySkin.xml"
SKIN_MOVIEPLAYER_TARGET_TMP = SKIN_MOVIEPLAYER_TARGET + ".tmp"

SKIN_EMC_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00g_EMC.xml"
SKIN_EMC_TARGET = "/usr/share/enigma2/MetrixHD/skin_00g_EMC.MySkin.xml"
SKIN_EMC_TARGET_TMP = SKIN_EMC_TARGET + ".tmp"

SKIN_OPENVISION_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00o_openvision.xml"
SKIN_OPENVISION_TARGET = "/usr/share/enigma2/MetrixHD/skin_00o_openvision.MySkin.xml"
SKIN_OPENVISION_TARGET_TMP = SKIN_OPENVISION_TARGET + ".tmp"

SKIN_PLUGINS_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00p_plugins.xml"
SKIN_PLUGINS_TARGET = "/usr/share/enigma2/MetrixHD/skin_00p_plugins.MySkin.xml"
SKIN_PLUGINS_TARGET_TMP = SKIN_PLUGINS_TARGET + ".tmp"

SKIN_UNCHECKED_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00u_unchecked.xml"
SKIN_UNCHECKED_TARGET = "/usr/share/enigma2/MetrixHD/skin_00u_unchecked.MySkin.xml"
SKIN_UNCHECKED_TARGET_TMP = SKIN_UNCHECKED_TARGET + ".tmp"

SKIN_DESIGN_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00z_design.xml"
SKIN_DESIGN_TARGET = "/usr/share/enigma2/MetrixHD/skin_00z_design.MySkin.xml"
SKIN_DESIGN_TARGET_TMP = SKIN_DESIGN_TARGET + ".tmp"
#############################################################

MAIN_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/%s.png"
COLOR_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/colors/%s.png"
FONT_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/fonts/%s.png"

OLD_BACKUP_FILE = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/MyMetrixLiteBackup.dat"
BACKUP_FILE = "/etc/enigma2/MyMetrixLiteBackup.dat"

from shutil import move
from os import path
if path.exists(OLD_BACKUP_FILE) and not path.exists(BACKUP_FILE):
	move(OLD_BACKUP_FILE, BACKUP_FILE)

#############################################################

ColorList = [
		("F0A30A", _("Amber")),
		("825A2C", _("Brown")),
		("5E0901", _("Burgund")),
		("0050EF", _("Cobalt")),
		("911D10", _("Crimson")),
		("1BA1E2", _("Cyan")),
		("00008B", _("Darkblue")),
		("2F1A09", _("Darkbrown")),
		("0F0F0F", _("Darkgrey")),
		("A61D4D", _("Magenta")),
		("A4C400", _("Lime")),
		("6A00FF", _("Indigo")),
		("5FA816", _("Brightgreen")),
		("70AD11", _("Green")),
		("009A93", _("Turquoise")),
		("008A00", _("Emerald")),
		("76608A", _("Mauve")),
		("FF5A00", _("Mandarin")),
		("0000CD", _("Mediumblue")),
		("0A173A", _("Midnight")),
		("000080", _("Navy")),
		("6D8764", _("Olive")),
		("C3461B", _("Orange")),
		("F472D0", _("Pink")),
		("E51400", _("Red")),
		("27408B", _("Royal Blue")),
		("7A3B3F", _("Sienna")),
		("647687", _("Steel")),
		("149BAF", _("Teal")),
		("6C0AAB", _("Violet")),
		("D8C100", _("Brightyellow")),
		("BF9217", _("Yellow")),
		("000000", _("Black")),
		("151515", _("Greyscale 1")),
		("1C1C1C", _("Greyscale 2")),
		("2E2E2E", _("Greyscale 3")),
		("424242", _("Greyscale 4")),
		("585858", _("Greyscale 5")),
		("6E6E6E", _("Greyscale 6")),
		("848484", _("Greyscale 7")),
		("A4A4A4", _("Greyscale 8")),
		("BDBDBD", _("Greyscale 9")),
		("D8D8D8", _("Greyscale 10")),
		("E6E6E6", _("Greyscale 11")),
		("F2F2F2", _("Greyscale 12")),
		("FAFAFA", _("Greyscale 13")),
		("FFFFFF", _("White"))
	]

TransparencyList=[
		("00", _("0%")),
		("0D", _("5%")),
		("1A", _("10%")),
		("27", _("15%")),
		("34", _("20%")),
		("40", _("25%")),
		("4D", _("30%")),
		("5A", _("35%")),
		("67", _("40%")),
		("74", _("45%")),
		("80", _("50%")),
		("8D", _("55%")),
		("9A", _("60%")),
		("A7", _("65%")),
		("B4", _("70%")),
		("C0", _("75%")),
		("CD", _("80%")),
		("DA", _("85%")),
		("E7", _("90%")),
		("F4", _("95%")),
		("FF", _("100%"))
	]

SysFontTypeList = [
	("/usr/share/fonts/ae_AlMateen.ttf", ("ae_AlMateen (ae_AlMateen.ttf)")),
	("/usr/share/fonts/andale.ttf", ("Andale Mono (andale.ttf)")),
	("/usr/share/fonts/lcd.ttf", ("LCD (lcd.ttf)")),
	#("/usr/share/fonts/md_khmurabi_10.ttf", ("MD King KhammuRabi (md_khmurabi_10.ttf)")),
	("/usr/share/fonts/nmsbd.ttf", ("Nemisis Flatline (nmsbd.ttf)")),
	#("/usr/share/fonts/Roboto-Black.ttf", ("Roboto Bk (Roboto-Black.ttf)")),
	#("/usr/share/fonts/Roboto-BlackItalic.ttf", ("Roboto Bk (Roboto-BlackItalic.ttf)")),
	#("/usr/share/fonts/Roboto-Bold.ttf", ("Roboto (Roboto-Bold.ttf)")),
	#("/usr/share/fonts/Roboto-BoldItalic.ttf", ("Roboto (Roboto-BoldItalic.ttf)")),
	("/usr/share/fonts/tuxtxt.ttf", ("Bitstream Vera Sans Mono (tuxtxt.ttf)"))
	#("/usr/share/fonts/valis_enigma.ttf", ("valis_enigma (valis_enigma.ttf)"))
]
SkinFontTypeList = [
	("/usr/share/enigma2/MetrixHD/fonts/analog.ttf", ("Analog (analog.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/DejaVuSans.ttf", ("DejaVu Sans (DejaVuSans.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/digi.ttf", ("LCD (digi.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/DroidSans.ttf", ("Droid Sans (DroidSans.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf", ("Droid Sans Bold (DroidSans-Bold.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/HandelGotD.ttf", ("HandelGotD (HandelGotD.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/HandelGotDBol.ttf", ("HandelGotD Bold (HandelGotDBol.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", ("OpenSans Regular (OpenSans-Regular.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/Raleway-Channel.ttf", ("Raleway Channel (Raleway-Channel.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf", ("Raleway Light(Raleway-Light.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf", ("Raleway Regular (Raleway-Regular.ttf)")),
	("/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", ("Segoe UI Light 8 (setrixHD.ttf)"))
]

SkinFontPresetList = [
	("preset_0", _("Standard Fonts")),
	("preset_1", _("Standard Fonts greater")),
	("preset_2", _("Bold and greater Fonts")),
	("preset_3", _("Raleway Fonts")),
	("preset_4", _("Digital Fonts")),
	("preset_5", _("Analog Fonts")),
	("preset_6", _("HandelGotD Fonts"))
	]

FontTypeList = []

for lines in SysFontTypeList:
	if path.exists(lines[0]):
		FontTypeList.append(lines)

for lines in SkinFontTypeList:
	if path.exists(lines[0]):
		FontTypeList.append(lines)

def initColorsConfig():

	BorderList = [
		("F0A30A", _("Amber")),
		("825A2C", _("Brown")),
		("0050EF", _("Cobalt")),
		("911D10", _("Crimson")),
		("1BA1E2", _("Cyan")),
		("00008B", _("Darkblue")),
		("0F0F0F", _("Darkgrey")),
		("A61D4D", _("Magenta")),
		("A4C400", _("Lime")),
		("6A00FF", _("Indigo")),
		("5FA816", _("Brightgreen")),
		("70AD11", _("Green")),
		("008A00", _("Emerald")),
		("76608A", _("Mauve")),
		("0000CD", _("Mediumblue")),
		("000080", _("Navy")),
		("6D8764", _("Olive")),
		("C3461B", _("Orange")),
		("F472D0", _("Pink")),
		("E51400", _("Red")),
		("27408B", _("Royal Blue")),
		("7A3B3F", _("Sienna")),
		("647687", _("Steel")),
		("149BAF", _("Teal")),
		("6C0AAB", _("Violet")),
		("D8C100", _("Brightyellow")),
		("BF9217", _("Yellow")),
		("000000", _("Black")),
		("151515", _("Greyscale 1")),
		("1C1C1C", _("Greyscale 2")),
		("2E2E2E", _("Greyscale 3")),
		("424242", _("Greyscale 4")),
		("585858", _("Greyscale 5")),
		("6E6E6E", _("Greyscale 6")),
		("848484", _("Greyscale 7")),
		("A4A4A4", _("Greyscale 8")),
		("BDBDBD", _("Greyscale 9")),
		("D8D8D8", _("Greyscale 10")),
		("E6E6E6", _("Greyscale 11")),
		("F2F2F2", _("Greyscale 12")),
		("FAFAFA", _("Greyscale 13")),
		("FFFFFF", _("White")),
		("trans", _("Transparent"))
	]

	BorderWidth = [
		("no", _("No")),
		("1px", _("1 px")),
		("2px", _("2 px")),
		("3px", _("3 px")),
		("4px", _("4 px")),
		("5px", _("5 px")),
		("6px", _("6 px")),
		("7px", _("7 px")),
		("8px", _("8 px")),
		("9px", _("9 px")),
		("10px", _("10 px"))
	]

	SkinColorPresetList = [
		("preset_0", _("Standard Colors")),
		("preset_1", _("Bright Colors")),
		("preset_2", _("Dark Colors")),
		("preset_3", _("Red Colors")),
		("preset_4", _("Yellow Colors")),
		("preset_5", _("Green Colors"))
		]

	config.plugins.MyMetrixLiteColors = ConfigSubsection()

	#preset
	config.plugins.MyMetrixLiteColors.SkinColorExamples = ConfigSelection(default = "preset_0", choices = SkinColorPresetList)
	#MetrixColors

	config.plugins.MyMetrixLiteColors.listboxborder_top = ConfigSelection(default="FFFFFF", choices = BorderList)
	config.plugins.MyMetrixLiteColors.listboxborder_topwidth = ConfigSelection(default="no", choices = BorderWidth)
	config.plugins.MyMetrixLiteColors.listboxborder_bottom = ConfigSelection(default="FFFFFF", choices = BorderList)
	config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth = ConfigSelection(default="no", choices = BorderWidth)
	config.plugins.MyMetrixLiteColors.listboxborder_right = ConfigSelection(default="FFFFFF", choices = BorderList)
	config.plugins.MyMetrixLiteColors.listboxborder_rightwidth = ConfigSelection(default="no", choices = BorderWidth)
	config.plugins.MyMetrixLiteColors.listboxborder_left = ConfigSelection(default="FFFFFF", choices = BorderList)
	config.plugins.MyMetrixLiteColors.listboxborder_leftwidth = ConfigSelection(default="no", choices = BorderWidth)

	config.plugins.MyMetrixLiteColors.windowborder_top = ConfigSelection(default="0F0F0F", choices = BorderList)
	config.plugins.MyMetrixLiteColors.windowborder_bottom = ConfigSelection(default="0F0F0F", choices = BorderList)
	config.plugins.MyMetrixLiteColors.windowborder_right = ConfigSelection(default="0F0F0F", choices = BorderList)
	config.plugins.MyMetrixLiteColors.windowborder_left = ConfigSelection(default="0F0F0F", choices = BorderList)

	config.plugins.MyMetrixLiteColors.menufont = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.menufontselected = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.menubackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.menubackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.menusymbolbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.infobarbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.infobarprogress = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.infobarprogresstransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.infobarfont1 = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.infobarfont2 = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.infobaraccent1 = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.infobaraccent2 = ConfigSelection(default="6E6E6E", choices = ColorList)

	config.plugins.MyMetrixLiteColors.channelselectionservice = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectionserviceselected = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectionservicedescription = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectionprogress = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectionprogressborder = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded = ConfigSelection(default="E51400", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded = ConfigSelection(default="0000CD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed = ConfigSelection(default="C3461B", choices = ColorList)

	config.plugins.MyMetrixLiteColors.emcWatchingColor = ConfigSelection(default="D8C100", choices = ColorList)
	config.plugins.MyMetrixLiteColors.emcFinishedColor = ConfigSelection(default="5FA816", choices = ColorList)
	config.plugins.MyMetrixLiteColors.emcRecordingColor = ConfigSelection(default="E51400", choices = ColorList)
	config.plugins.MyMetrixLiteColors.emcCoolHighlightColor = ConfigYesNo(default=True)

	config.plugins.MyMetrixLiteColors.windowtitletext = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.windowtitletexttransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.windowtitletextback = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.backgroundtext = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.backgroundtexttransparency = ConfigSelection(default="34", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.backgroundtextback = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency = ConfigSelection(default="67", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.backgroundtextborderwidth = ConfigSelectionNumber(0, 10, 1, default = 0)
	config.plugins.MyMetrixLiteColors.backgroundtextbordercolor = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.backgroundtextbordertransparency = ConfigSelection(default="1A", choices = TransparencyList)

	config.plugins.MyMetrixLiteColors.layerabackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerabackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layeraforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraselectionbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layeraselectionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraaccent1 = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraaccent2 = ConfigSelection(default="6E6E6E", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraprogress = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraprogresstransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layeraunderline = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraunderlinetransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layeraextendedinfo1 = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraextendedinfo2 = ConfigSelection(default="6E6E6E", choices = ColorList)

	config.plugins.MyMetrixLiteColors.layerbbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layerbforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbselectionbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.layerbselectionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbaccent1 = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbaccent2 = ConfigSelection(default="6E6E6E", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbprogress = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbprogresstransparency = ConfigSelection(default="1A", choices = TransparencyList)

	config.plugins.MyMetrixLiteColors.epgbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgborderlines = ConfigSelection(default="BDBDBD", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgborderlinestransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgeventforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgprimetimeforeground = ConfigSelection(default="008A00", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgprimetimebackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgprimetimebackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgeventnowforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventnowbackground = ConfigSelection(default="000000", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgeventselectedforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventselectedbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgserviceforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgservicebackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgservicenowforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgservicenowbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.epgtimelineforeground = ConfigSelection(default="F0A30A", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgtimelinebackground = ConfigSelection(default="000000", choices = ColorList)
	config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)

	config.plugins.MyMetrixLiteColors.buttonforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layeraclockforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.layerbclockforeground = ConfigSelection(default="FFFFFF", choices = ColorList)

	config.plugins.MyMetrixLiteColors.upperleftcornerbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.upperleftcornertransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.lowerleftcornerbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.lowerleftcornertransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.upperrightcornerbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.upperrightcornertransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.lowerrightcornerbackground = ConfigSelection(default="0F0F0F", choices = ColorList)
	config.plugins.MyMetrixLiteColors.lowerrightcornertransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency = ConfigSelection(default="1A", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.optionallayerverticalbackground = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency = ConfigSelection(default="1A", choices = TransparencyList)

	config.plugins.MyMetrixLiteColors.scrollbarSlidercolor = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteColors.scrollbarSlidertransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteColors.scrollbarSliderbordercolor = ConfigSelection(default="27408B", choices = ColorList)
	config.plugins.MyMetrixLiteColors.scrollbarSliderbordertransparency = ConfigSelection(default="00", choices = TransparencyList)

	gradientcolor = [('0', _('disabled')), ('1', _('same as background')), ('25', _('%s darker than background')%'25%') , ('50',  _('%s darker than background')%'50%'), ('75',  _('%s darker than background')%'75%')] + ColorList
	config.plugins.MyMetrixLiteColors.cologradient = ConfigSelection(default='0', choices = gradientcolor)

#############################################################

def initFontsConfig():

	config.plugins.MyMetrixLiteFonts = ConfigSubsection()
#preset
	config.plugins.MyMetrixLiteFonts.SkinFontExamples = ConfigSelection(default = "preset_0", choices = SkinFontPresetList)
#system fonts
	config.plugins.MyMetrixLiteFonts.Lcd_type = ConfigSelection(default="/usr/share/fonts/lcd.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Lcd_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.Replacement_type = ConfigSelection(default="/usr/share/fonts/ae_AlMateen.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Replacement_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.Console_type = ConfigSelection(default="/usr/share/fonts/tuxtxt.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Console_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.Fixed_type = ConfigSelection(default="/usr/share/fonts/andale.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Fixed_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.Arial_type = ConfigSelection(default="/usr/share/fonts/nmsbd.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Arial_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
#skin fonts
	config.plugins.MyMetrixLiteFonts.Regular_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.Regular_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.RegularLight_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.RegularLight_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.SetrixHD_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.SetrixHD_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.Meteo_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
#------------------------------#
#for individual skinned screens#
#------------------------------#
#global
	config.plugins.MyMetrixLiteFonts.globaltitle_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globaltitle_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.globalbutton_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globalbutton_scale = ConfigSelectionNumber(50, 150, 1, default = 90)
	config.plugins.MyMetrixLiteFonts.globalclock_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globalclock_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.globallarge_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globallarge_scale = ConfigSelectionNumber(50, 150, 1, default = 80)
	config.plugins.MyMetrixLiteFonts.globalsmall_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globalsmall_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.globalmenu_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.globalmenu_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
#screens, plugins
	config.plugins.MyMetrixLiteFonts.screenlabel_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.screenlabel_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.screentext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.screentext_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.screeninfo_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.screeninfo_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
#epg, channellist, movielist
	config.plugins.MyMetrixLiteFonts.epgevent_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.epgevent_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.epgtext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.epgtext_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
	config.plugins.MyMetrixLiteFonts.epginfo_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.epginfo_scale = ConfigSelectionNumber(50, 150, 1, default = 95)
#infobar, movieplayer
	config.plugins.MyMetrixLiteFonts.infobarevent_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.infobarevent_scale = ConfigSelectionNumber(50, 150, 1, default = 100)
	config.plugins.MyMetrixLiteFonts.infobartext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteFonts.infobartext_scale = ConfigSelectionNumber(50, 150, 1, default = 95)

#######################################################################

def initWeatherConfig():
	config.plugins.MetrixWeather = ConfigSubsection()

	#MetrixWeather

	config.plugins.MetrixWeather.enabled = ConfigYesNo(default=False)
	config.plugins.MetrixWeather.MoviePlayer = ConfigYesNo(default=True)
	config.plugins.MetrixWeather.verifyDate = ConfigYesNo(default=True)
	config.plugins.MetrixWeather.refreshInterval = ConfigSelectionNumber(0, 1440, 30, default = 120, wraparound = True)
	config.plugins.MetrixWeather.woeid = ConfigNumber(default=2911298)
	config.plugins.MetrixWeather.apikey = ConfigText(default="a4bd84726035d0ce2c6185740617d8c5")
	config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
		("Celsius", _("Celsius")),
		("Fahrenheit", _("Fahrenheit"))
	])


	## RENDERER CONFIG:

	config.plugins.MetrixWeather.currentWeatherDataValid = ConfigNumber(default=0)
	config.plugins.MetrixWeather.currentLocation = ConfigText(default="N/A")
	config.plugins.MetrixWeather.currentWeatherCode = ConfigText(default="(")
	config.plugins.MetrixWeather.currentWeatherText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.currentWeatherTemp = ConfigText(default="0")

	config.plugins.MetrixWeather.forecastTodayCode = ConfigText(default="(")
	config.plugins.MetrixWeather.forecastTodayText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.forecastTodayTempMin = ConfigText(default="0")
	config.plugins.MetrixWeather.forecastTodayTempMax = ConfigText(default="0")

	config.plugins.MetrixWeather.forecastTomorrowCode = ConfigText(default="(")
	config.plugins.MetrixWeather.forecastTomorrowText = ConfigText(default="N/A")
	config.plugins.MetrixWeather.forecastTomorrowTempMin = ConfigText(default="0")
	config.plugins.MetrixWeather.forecastTomorrowTempMax = ConfigText(default="0")

#######################################################################

def initOtherConfig():
	channelSelectionStyleList = [
		("CHANNELSELECTION-1", _("Focus left, no picon, 5 next Events")),
		("CHANNELSELECTION-2", _("Focus left, big picon, 1 next Events")),
		("CHANNELSELECTION-3", _("Focus right, big picon, 1 next Events")),
		("CHANNELSELECTION-4", _("Focus right, no picon, 5 next Events"))
		]

	movielistStyleList = [
		("left", _("Focus left, description right")),
		("right", _("Focus right, description left"))
		]

	infoBarChannelNameFontSizeList = [
		("INFOBARCHANNELNAME-5", _("40")),
		("INFOBARCHANNELNAME-4", _("50")),
		("INFOBARCHANNELNAME-3", _("60")),
		("INFOBARCHANNELNAME-2", _("70")),
		("INFOBARCHANNELNAME-1", _("80"))
		]

	skinDesignShowLayerList = [
		("no", _("No")),
		("screens", _("in Screens")),
		("menus", _("in Menus")),
		("both", _("in Menus and Screens"))
		]

	skinDesignPresetList = [
		("preset_0", _("No Design")),
		("preset_1", _("One Layer Design")),
		("preset_2", _("Contrast Layer Design")),
		("preset_3", _("Stripe Layer Design")),
		("preset_4", _("Blocks Layer Design")),
		("preset_5", _("Frame Layer Design"))
		]

	config.plugins.MyMetrixLiteOther = ConfigSubsection()

	#OtherSettings
	#EHD-Option -> Enhanced HD
	BoxType = getBoxType()
	config.plugins.MyMetrixLiteOther.EHDtested = ConfigText(default = "%s_|_0" %BoxType)

	skinmodes = [("0", _("Standard HD (1280x720)"))]
	mode1080p = mode2160p = risk = False
	try:
		if path.exists("/proc/stb/video/videomode_choices"):
			vmodes = open("/proc/stb/video/videomode_choices").read()
			if '1080p' in vmodes:
				mode1080p = True
			if '2160p' in vmodes:
				mode2160p = True
		else:
			risk = True
	except:
		print "[MyMetrixLite] - can't read video modes"
		risk = True

	tested = config.plugins.MyMetrixLiteOther.EHDtested.value.split('_|_')
	risktxt = _(" - box support unknown")
	if len(tested) == 2:
		if BoxType in tested[0] and '1' in tested[1]:
			skinmodes.append(("1", _("Full HD (1920x1080)")))
		elif mode1080p or risk:
			skinmodes.append(("1", _("Full HD (1920x1080) %s") %risktxt))
		if BoxType in tested[0] and '2' in tested[1]:
			skinmodes.append(("2", _("Ultra HD (3840x2160)")))
		elif mode2160p or risk:
			skinmodes.append(("2", _("Ultra HD (3840x2160) %s") %risktxt))
	else:
		if mode1080p or risk:
			skinmodes.append(("1", _("Full HD (1920x1080) %s") %risktxt))
		if mode2160p or risk:
			skinmodes.append(("2", _("Ultra HD (3840x2160) %s") %risktxt))
	###no box supports at time uhd skins ...###
	if '2' in skinmodes[-1]: del skinmodes[-1]#
	###########################################
	config.plugins.MyMetrixLiteOther.EHDenabled = ConfigSelection(default = "0", choices = skinmodes)
	config.plugins.MyMetrixLiteOther.EHDrounddown = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.EHDfontsize = ConfigSelection(default = "2", choices = [("1", _("scale")), ("2", _("size")), ("3", _("50/50"))])
	config.plugins.MyMetrixLiteOther.EHDfontoffset = ConfigSelectionNumber(-20, 20, 1, default = 0)
	config.plugins.MyMetrixLiteOther.EHDpiconzoom =  ConfigSelection(default = "1.0", choices = [("0", _("No")), ("0.2", _("20%")), ("0.4", _("40%")), ("0.6", _("60%")), ("0.8", _("80%")), ("1.0", _("100%"))])
	config.plugins.MyMetrixLiteOther.EHDadditionalfiles = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.piconresize_experimental = ConfigYesNo(default=False)
	sharpness = []
	for i in range(0,525,25):
		x = str(format(float(i)/100, '.2f'))
		sharpness.append((x,x))
	config.plugins.MyMetrixLiteOther.piconsharpness_experimental = ConfigSelection(default = '1.00', choices = sharpness)
	#STB-Info
	config.plugins.MyMetrixLiteOther.STBDistance = ConfigSelectionNumber(1, 50, 1, default = 10)
	config.plugins.MyMetrixLiteOther.showCPULoad = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showRAMfree = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showSYSTemp = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showCPUTemp = ConfigYesNo(default=False)
	#Infobar/Secondinfobar
	config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showChannelNumber = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showChannelName = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize = ConfigSelection(default="INFOBARCHANNELNAME-1", choices = infoBarChannelNameFontSizeList)
	config.plugins.MyMetrixLiteOther.showInfoBarResolution = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showInfoBarResolutionExtended = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showExtendedinfo = ConfigYesNo(default=False)

	config.plugins.MyMetrixLiteOther.showExtended_caid = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showExtended_prov = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showExtended_pid = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showExtended_source = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showExtended_reader = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showExtended_protocol = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showExtended_hops = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showExtended_ecmtime = ConfigYesNo(default=True)
	
	config.plugins.MyMetrixLiteOther.ExtendedinfoStyle = ConfigSelection(default = "1", choices = [("1", _("Top of the screen")), ("2", _("Between Clock and Weather enclosed")), ("3", _("Between Clock and Weather centered")), ("4", _("Bottom of the screen"))])
	config.plugins.MyMetrixLiteOther.showSnr = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showRecordstate = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showOrbitalposition = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showInfoBarClock = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showSTBinfo = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showTunerinfo = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.setTunerAuto = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.setTunerManual = ConfigSelection(default='2', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('10','10'),('12','12'),('16','16'),('18','18'),('19','19')])
	config.plugins.MyMetrixLiteOther.showInfoBarRunningtext = ConfigYesNo(default=False)
	#running text parameter
	config.plugins.MyMetrixLiteOther.runningTextStartdelay = ConfigSelectionNumber(600, 10000, 100, default = 1200, wraparound=True)
	config.plugins.MyMetrixLiteOther.runningTextSpeed = ConfigSelectionNumber(20, 1000, 10, default = 60, wraparound=True)
	#channel list
	config.plugins.MyMetrixLiteOther.channelSelectionStyle = ConfigSelection(default="CHANNELSELECTION-1", choices = channelSelectionStyleList)
	config.plugins.MyMetrixLiteOther.setItemDistance = ConfigSelectionNumber(1, 50, 1, default = 5, wraparound=True)
	config.plugins.MyMetrixLiteOther.setFieldMargin = ConfigSelectionNumber(1, 50, 1, default = 5, wraparound=True)
	config.plugins.MyMetrixLiteOther.channelSelectionShowPrimeTime = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.graphicalEpgStyle = ConfigSelection(default = "1", choices = [("1", _("Standard")), ("2", _("more Events or 'mini TV' greater"))])
	config.plugins.MyMetrixLiteOther.showChannelListScrollbar = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showChannelListRunningtext = ConfigYesNo(default=False)
	#EMC/MoviePlayer
	config.plugins.MyMetrixLiteOther.movielistStyle = ConfigSelection(default="left", choices = movielistStyleList)
	config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign = ConfigSelection(default = "2", choices = [("1", _("Large")), ("2", _("Standard")), ("3", _("Small"))])
	config.plugins.MyMetrixLiteOther.showMovieName = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showMoviePlayerResolutionExtended = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showMovieTime = ConfigSelection(default = "2", choices = [("1", _("No")), ("2", _("In Moviebar")), ("3", _("Side by PVR-Symbol"))])
	config.plugins.MyMetrixLiteOther.showPVRState = ConfigSelection(default = "1", choices = [("1", _("Standard")), ("2", _("Top of the screen")), ("3", _("Top of the screen with current time"))])
	config.plugins.MyMetrixLiteOther.showMovieListScrollbar = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.showMovieListRunningtext = ConfigYesNo(default=False)
	#EMC
	config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover = ConfigSelection(default = "no", choices = [("no", _("No")), ("small", _("Small")), ("large", _("Large"))])
	config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showEMCSelectionCover = ConfigSelection(default = "no", choices = [("no", _("No")), ("small", _("Small")), ("large", _("Large"))])
	config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.showEMCSelectionRows = ConfigSelection(default = "0", choices = [("-4", _("-4")), ("-2", _("-2")), ("0", _("No")), ("+2", _("+2")), ("+4", _("+4")), ("+6", _("+6")), ("+8", _("+8"))])
	config.plugins.MyMetrixLiteOther.showEMCSelectionPicon = ConfigSelection(default = "no", choices = [("no", _("No")), ("left", _("left")), ("right", _("right"))])
	choicelist = [("0", _("off"))]
	for x in range(50,202,2):
		choicelist.append(('%d' %x,'%d' %x))
	config.plugins.MyMetrixLiteOther.setEMCdatesize = ConfigSelection(default = "104", choices = choicelist)
	config.plugins.MyMetrixLiteOther.setEMCdirinfosize = ConfigSelection(default = "140", choices = choicelist)
	choicelist = [("0", _("off"))]
	for x in range(20,82,2):
		choicelist.append(('%d' %x,'%d' %x))
	config.plugins.MyMetrixLiteOther.setEMCbarsize = ConfigSelection(default = "50", choices = choicelist)
	#SkinDesign
	config.plugins.MyMetrixLiteOther.SkinDesignScrollbarSliderWidth = ConfigSelectionNumber(0, 15, 1, default = 10)
	config.plugins.MyMetrixLiteOther.SkinDesignScrollbarBorderWidth = ConfigSelectionNumber(0, 5, 1, default = 1)
	config.plugins.MyMetrixLiteOther.SkinDesignMenuButtons = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.SkinDesignMenuScrollInfo = ConfigYesNo(default=True)
	config.plugins.MyMetrixLiteOther.SkinDesign = ConfigSelection(default = "1", choices = [("1", _("Standard")), ("2", _("Layer A and B same height, Clock in Layer A")), ("3", _("Layer A and B same height, Clock in Layer B"))])
	config.plugins.MyMetrixLiteOther.SkinDesignSpace = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarColorGradient = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon = ConfigSelection(default = "1", choices = [("1", _("XPicons")), ("2", _("ZZZPicons"))])
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosX = ConfigSelectionNumber(-33, 33, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosY = ConfigSelectionNumber(-14, 14, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosX = ConfigSelectionNumber(0, 66, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosY = ConfigSelectionNumber(0, 28, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize = ConfigSelectionNumber(-28, 0, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText = ConfigSelection(default = "both", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignLUC = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignLLC = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignRUC = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignRLC = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignOLH = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignOLV = ConfigSelection(default = "no", choices = skinDesignShowLayerList)
	config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth = ConfigInteger(default=40, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignLUCheight = ConfigInteger(default=25, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignLUCposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth = ConfigInteger(default=40, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignLLCheight = ConfigInteger(default=45, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignLLCposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth = ConfigInteger(default=40, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignRUCheight = ConfigInteger(default=60, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignRUCposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth = ConfigInteger(default=40, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignRLCheight = ConfigInteger(default=80, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignRLCposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth = ConfigInteger(default=1127, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignOLHheight = ConfigInteger(default=30, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignOLHposx = ConfigInteger(default=0, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignOLHposy = ConfigInteger(default=655, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignOLHposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth = ConfigInteger(default=60, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignOLVheight = ConfigInteger(default=669, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignOLVposx = ConfigInteger(default=102, limits=(0, 1280))
	config.plugins.MyMetrixLiteOther.SkinDesignOLVposy = ConfigInteger(default=51, limits=(0, 720))
	config.plugins.MyMetrixLiteOther.SkinDesignOLVposz = ConfigInteger(default=0, limits=(0, 5))
	config.plugins.MyMetrixLiteOther.layeraunderlinesize = ConfigSelectionNumber(0, 10, 1, default = 1)
	config.plugins.MyMetrixLiteOther.layeraunderlineposy = ConfigSelectionNumber(-5, 5, 1, default = 0)
	config.plugins.MyMetrixLiteOther.layeraunderlineshowmainlayer = ConfigYesNo(default=False)
	#preset
	config.plugins.MyMetrixLiteOther.SkinDesignExamples = ConfigSelection(default = "preset_0", choices = skinDesignPresetList)
	#Buttons
	config.plugins.MyMetrixLiteOther.SkinDesignButtons = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColor = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColorTransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColor = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColorTransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColor = ConfigSelection(default="000000", choices = ColorList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColorTransparency = ConfigSelection(default="00", choices = TransparencyList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextFont = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextSize = ConfigSelectionNumber(10, 30, 1, default = 24)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameSize = ConfigSelectionNumber(0, 5, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextPosition = ConfigSelectionNumber(-10, 10, 1, default = 0)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect = ConfigSelection(default = "no", choices = [("no", _("None")), ("solidframe", _("Solid")), ("solid", _("Solid without Frame")), ("gradientframe", _("Flat Gradient")), ("gradient", _("Flat Gradient without Frame")), ("circleframe", _("Circle Gradient")), ("circle", _("Circle Gradient without Frame"))])
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectSize = ConfigSelection(default = "0.5", choices = [("0.1", _("10%")), ("0.2", _("20%")), ("0.3", _("30%")), ("0.4", _("40%")), ("0.5", _("50%")), ("0.6", _("60%")), ("0.7", _("70%")), ("0.8", _("80%")), ("0.9", _("90%")), ("1", _("100%"))])
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosX = ConfigSelection(default = "0.5", choices = [("0", _("0")), ("0.1", _("10")), ("0.2", _("20")), ("0.3", _("30")), ("0.4", _("40")), ("0.5", _("50")), ("0.6", _("60")), ("0.7", _("70")), ("0.8", _("80")), ("0.9", _("90")), ("1", _("100"))])
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosY = ConfigSelection(default = "0.5", choices = [("0", _("0")), ("0.1", _("10")), ("0.2", _("20")), ("0.3", _("30")), ("0.4", _("40")), ("0.5", _("50")), ("0.6", _("60")), ("0.7", _("70")), ("0.8", _("80")), ("0.9", _("90")), ("1", _("100"))])
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectColor = ConfigSelection(default="FFFFFF", choices = ColorList)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectOverText = ConfigYesNo(default=False)
	config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectIntensity = ConfigSelection(default="00", choices = TransparencyList)

#######################################################################

def getTunerPositionList():
	tunerPositionList = [
		("286,666", "286,693", "1", "0,0"),
		("306,666", "306,693", "2", "1,1"),
		("326,666", "326,693", "4", "2,2"),
		("346,666", "346,693", "8", "3,3"),
		("366,666", "366,693", "16", "4,4"),
		("386,666", "386,693", "32", "5,5")
	]

	return tunerPositionList

#######################################################################

def appendSkinFile(appendFileName, skinPartSearchAndReplace):
	"""
	add skin file to main skin content

	appendFileName:
	 xml skin-part to add

	skinPartSearchAndReplace:
	 (optional) a list of search and replace arrays. first element, search, second for replace
	"""
	rsSkinLines = []

	skFile = open(appendFileName, "r")
	file_lines = skFile.readlines()
	skFile.close()

	for skinLine in file_lines:
		for item in skinPartSearchAndReplace:
			skinLine = skinLine.replace(item[0], item[1])
		rsSkinLines.append(skinLine)

	return rsSkinLines
