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
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigNumber, ConfigSelectionNumber, ConfigYesNo, ConfigText
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

COLOR_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/%s.png"

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
        ("80", _("50%"))
    ]

    config.plugins.MyMetrixLiteColors = ConfigSubsection()

    #MetrixColors

    config.plugins.MyMetrixLiteColors.channelselectionservice = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionserviceselected = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionservicedescription = ConfigSelection(default="BDBDBD", choices = ColorList)
    config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected = ConfigSelection(default="FFFFFF", choices = ColorList)

    config.plugins.MyMetrixLiteColors.backgroundtext = ConfigSelection(default="FFFFFF", choices = ColorList)
    config.plugins.MyMetrixLiteColors.backgroundtexttransparency = ConfigSelection(default="80", choices = TransparencyList)

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

#############################################################

def initWeatherConfig():
    config.plugins.MetrixWeather = ConfigSubsection()

    #MetrixWeather

    config.plugins.MetrixWeather.enabled = ConfigYesNo(default=True)
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

    config.plugins.MyMetrixLiteOther = ConfigSubsection()

    #OtherSettings

    config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showChannelNumber = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showChannelName = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showMovieName = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize = ConfigSelection(default="INFOBARCHANNELNAME-1", choices = infoBarChannelNameFontSizeList)
    config.plugins.MyMetrixLiteOther.showInfoBarResolution = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showInfoBarClock = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.showCPULoad = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.setTunerAuto = ConfigYesNo(default=True)
    config.plugins.MyMetrixLiteOther.setTunerManual = ConfigSelectionNumber(1, 6, 1, default = 2)
    config.plugins.MyMetrixLiteOther.channelSelectionStyle = ConfigSelection(default="CHANNELSELECTION-1", choices = channelSelectionStyleList)

#######################################################################

def getTunerPositionList():
    tunerPositionList = [
        ("286,666", "286,693", "1", "0,0"),
        ("306,666", "306,693", "2", "1,1"),
        ("326,666", "326,693", "4", "2,2"),
        ("346,666", "346,693", "8", "3,3"),
        ("366,666", "346,693", "8", "3,3"),
        ("386,666", "346,693", "8", "3,3")
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
