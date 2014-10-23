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

SKIN_TARGET = "/usr/share/enigma2/MetrixHD/skin.MySkin.xml"
SKIN_TARGET_TMP = SKIN_TARGET + ".tmp"

SKIN_SOURCE = "/usr/share/enigma2/MetrixHD/skin.xml"

SKIN_INFOBAR_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00a_InfoBar.xml"
SKIN_INFOBAR_TARGET = "/usr/share/enigma2/MetrixHD/skin_00a_InfoBar.MySkin.xml"
SKIN_INFOBAR_TARGET_TMP = SKIN_INFOBAR_TARGET + ".tmp"

SKIN_SECOND_INFOBAR_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00b_SecondInfoBar.xml"
SKIN_SECOND_INFOBAR_TARGET = "/usr/share/enigma2/MetrixHD/skin_00b_SecondInfoBar.MySkin.xml"
SKIN_SECOND_INFOBAR_TARGET_TMP = SKIN_SECOND_INFOBAR_TARGET + ".tmp"

SKIN_CHANNEL_SELECTION_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00e_ChannelSelection.xml"
SKIN_CHANNEL_SELECTION_TARGET = "/usr/share/enigma2/MetrixHD/skin_00e_ChannelSelection.MySkin.xml"
SKIN_CHANNEL_SELECTION_TARGET_TMP = SKIN_CHANNEL_SELECTION_TARGET + ".tmp"

SKIN_MOVIEPLAYER_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00f_MoviePlayer.xml"
SKIN_MOVIEPLAYER_TARGET = "/usr/share/enigma2/MetrixHD/skin_00f_MoviePlayer.MySkin.xml"
SKIN_MOVIEPLAYER_TARGET_TMP = SKIN_MOVIEPLAYER_TARGET + ".tmp"

SKIN_EMC_SOURCE = "/usr/share/enigma2/MetrixHD/skin_00g_EMC.xml"
SKIN_EMC_TARGET = "/usr/share/enigma2/MetrixHD/skin_00g_EMC.MySkin.xml"
SKIN_EMC_TARGET_TMP = SKIN_EMC_TARGET + ".tmp"

#############################################################

MAIN_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/%s.png"
WEATHER_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/weather/%s.png"
COLOR_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/colors/%s.png"
FONT_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/fonts/%s.png"
OTHER_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/other/%s.png"

#############################################################

def initColorsConfig():
    ColorList = [
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

    config.plugins.MyMetrixLiteColors = ConfigSubsection()

    #MetrixColors

    config.plugins.MyMetrixLiteColors.channelselectionservice = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionserviceselected = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionservicedescription = ConfigSelection(default="BDBDBD", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected = ConfigSelection(default="FFFFFF", choices = ColorList)

    config.plugins.MyMetrixLiteColors.windowtitletext = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.windowtitletexttransparency = ConfigSelection(default="1A", choices = TransparencyList)
    config.plugins.MyMetrixLiteColors.windowtitletextback = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency = ConfigSelection(default="34", choices = TransparencyList)
    config.plugins.MyMetrixLiteColors.backgroundtext = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.backgroundtexttransparency = ConfigSelection(default="34", choices = TransparencyList)
    config.plugins.MyMetrixLiteColors.backgroundtextback = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency = ConfigSelection(default="67", choices = TransparencyList)

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

    config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground = ConfigSelection(default="27408B", choices = ColorList)
    config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
    config.plugins.MyMetrixLiteColors.epgeventforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.epgtimelineforeground = ConfigSelection(default="F0A30A", choices = ColorList)

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

#############################################################

def initFontsConfig():

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
        ("/usr/share/enigma2/MetrixHD/fonts/DroidSans-Bold.ttf", ("Droid Sans (DroidSans-Bold.ttf)")),
        ("/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", ("Open Sans (OpenSans-Regular.ttf)")),
        ("/usr/share/enigma2/MetrixHD/fonts/Raleway-Channel.ttf", ("Raleway (Raleway-Channel.ttf)")),
        ("/usr/share/enigma2/MetrixHD/fonts/Raleway-Light.ttf", ("Raleway (Raleway-Light.ttf)")),
        ("/usr/share/enigma2/MetrixHD/fonts/Raleway-Regular.ttf", ("Raleway (Raleway-Regular.ttf)")),
        ("/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", ("Segoe UI Light 8 (setrixHD.ttf)"))
    ]

    SkinFontPresetList = [
        ("preset_0", _("Standard Fonts")),
        ("preset_1", _("Standard Fonts greater")),
        ("preset_2", _("Bold and greater Fonts")),
        ("preset_3", _("Raleway Fonts")),
        ("preset_4", _("Digital Fonts"))
        ]

    FontTypeList = []

    for lines in SysFontTypeList:
        if path.exists(lines[0]):
            FontTypeList.append(lines)

    for lines in SkinFontTypeList:
        if path.exists(lines[0]):
            FontTypeList.append(lines)

    config.plugins.MyMetrixLiteFonts = ConfigSubsection()
#preset
    config.plugins.MyMetrixLiteFonts.SkinFontExamples = ConfigSelection(default = "preset_0", choices = SkinFontPresetList)
#system fonts
    config.plugins.MyMetrixLiteFonts.Lcd_type = ConfigSelection(default="/usr/share/fonts/lcd.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Lcd_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.Replacement_type = ConfigSelection(default="/usr/share/fonts/ae_AlMateen.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Replacement_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.Console_type = ConfigSelection(default="/usr/share/fonts/tuxtxt.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Console_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.Fixed_type = ConfigSelection(default="/usr/share/fonts/andale.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Fixed_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.Arial_type = ConfigSelection(default="/usr/share/fonts/nmsbd.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Arial_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
#skin fonts
    config.plugins.MyMetrixLiteFonts.Regular_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.Regular_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.RegularLight_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.RegularLight_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.SetrixHD_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.SetrixHD_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.Meteo_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
#------------------------------#
#for individual skinned screens#
#------------------------------#
#global
    config.plugins.MyMetrixLiteFonts.globaltitle_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globaltitle_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.globalbutton_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globalbutton_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.globalclock_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globalclock_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.globallarge_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globallarge_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.globalsmall_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globalsmall_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.globalmenu_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.globalmenu_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
#screens, plugins
    config.plugins.MyMetrixLiteFonts.screenlabel_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.screenlabel_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.screentext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.screentext_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.screeninfo_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.screeninfo_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
#epg, channellist, movielist
    config.plugins.MyMetrixLiteFonts.epgevent_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.epgevent_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.epgtext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.epgtext_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
    config.plugins.MyMetrixLiteFonts.epginfo_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.epginfo_scale = ConfigSelectionNumber(75, 125, 1, default = 95)
#infobar, movieplayer
    config.plugins.MyMetrixLiteFonts.infobarevent_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.infobarevent_scale = ConfigSelectionNumber(75, 125, 1, default = 100)
    config.plugins.MyMetrixLiteFonts.infobartext_type = ConfigSelection(default="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf", choices = FontTypeList)
    config.plugins.MyMetrixLiteFonts.infobartext_scale = ConfigSelectionNumber(75, 125, 1, default = 95)

#######################################################################

def initWeatherConfig():
    config.plugins.MetrixWeather = ConfigSubsection()

    #MetrixWeather

    config.plugins.MetrixWeather.enabled = ConfigYesNo(default=True)
    config.plugins.MetrixWeather.MoviePlayer = ConfigYesNo(default=True)
    config.plugins.MetrixWeather.refreshInterval = ConfigNumber(default=10)
    config.plugins.MetrixWeather.woeid = ConfigNumber(default=676757) #Location (visit metrixhd.info)
    config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
        ("Celsius", _("Celsius")),
        ("Fahrenheit", _("Fahrenheit"))
    ])


    ## RENDERER CONFIG:

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

    infoBarChannelNameFontSizeList = [
        ("INFOBARCHANNELNAME-1", _("80")),
        ("INFOBARCHANNELNAME-2", _("70")),
        ("INFOBARCHANNELNAME-3", _("60")),
        ("INFOBARCHANNELNAME-4", _("50")),
        ("INFOBARCHANNELNAME-5", _("40"))
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
        ("preset_4", _("Block Layer Design"))
        ]

    config.plugins.MyMetrixLiteOther = ConfigSubsection()

    #OtherSettings
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
    config.plugins.MyMetrixLiteOther.showExtendedinfo = ConfigYesNo(default=False)
    config.plugins.MyMetrixLiteOther.ExtendedinfoStyle = ConfigSelection(default = "1", choices = [("1", _("Top of the screen")), ("2", _("Between Clock and Weather enclosed")), ("3", _("Between Clock and Weather centered")), ("4", _("Bottom of the screen"))])
    config.plugins.MyMetrixLiteOther.showSnr = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showRecordstate = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showOrbitalposition = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showInfoBarClock = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showSTBinfo = ConfigYesNo(default=False)
    config.plugins.MyMetrixLiteOther.showTunerinfo = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.setTunerAuto = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.setTunerManual = ConfigSelectionNumber(1, 6, 1, default = 2)
    config.plugins.MyMetrixLiteOther.channelSelectionStyle = ConfigSelection(default="CHANNELSELECTION-1", choices = channelSelectionStyleList)
	#EMC/MoviePlayer
    config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign = ConfigSelection(default = "1", choices = [("1", _("Standard")), ("2", _("Infobar")), ("3", _("Small"))])
    config.plugins.MyMetrixLiteOther.showMovieName = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer = ConfigYesNo(default=False)
	#EMC
    config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover = ConfigSelection(default = "no", choices = [("no", _("No")), ("small", _("Small")), ("large", _("Large"))])
    config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showEMCSelectionCover = ConfigSelection(default = "no", choices = [("no", _("No")), ("small", _("Small")), ("large", _("Large"))])
    config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription = ConfigYesNo(default=True)
	#SkinDesign
    config.plugins.MyMetrixLiteOther.SkinDesign = ConfigSelection(default = "1", choices = [("1", _("Standard")), ("2", _("Layer A and B same height, Clock in Layer A")), ("3", _("Layer A and B same height, Clock in Layer B"))])
    config.plugins.MyMetrixLiteOther.SkinDesignSpace = ConfigYesNo(default=False)
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
#preset
    config.plugins.MyMetrixLiteOther.SkinDesignExamples = ConfigSelection(default = "preset_0", choices = skinDesignPresetList)

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
