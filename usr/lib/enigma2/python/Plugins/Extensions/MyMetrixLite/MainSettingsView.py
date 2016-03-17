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

from . import _, initColorsConfig, initWeatherConfig, initOtherConfig, initFontsConfig, getTunerPositionList, appendSkinFile, MAIN_IMAGE_PATH, \
    SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP, \
    SKIN_TEMPLATES_SOURCE, SKIN_TEMPLATES_TARGET, SKIN_TEMPLATES_TARGET_TMP, \
    SKIN_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP, \
    SKIN_SECOND_INFOBAR_SOURCE, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP, \
    SKIN_SECOND_INFOBAR_ECM_SOURCE, SKIN_SECOND_INFOBAR_ECM_TARGET, SKIN_SECOND_INFOBAR_ECM_TARGET_TMP, \
    SKIN_INFOBAR_LITE_SOURCE, SKIN_INFOBAR_LITE_TARGET, SKIN_INFOBAR_LITE_TARGET_TMP, \
    SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP, \
    SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP, \
    SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP, \
    SKIN_OPENATV_SOURCE, SKIN_OPENATV_TARGET, SKIN_OPENATV_TARGET_TMP, \
    SKIN_PLUGINS_SOURCE, SKIN_PLUGINS_TARGET, SKIN_PLUGINS_TARGET_TMP, \
    SKIN_UNCHECKED_SOURCE, SKIN_UNCHECKED_TARGET, SKIN_UNCHECKED_TARGET_TMP, \
    SKIN_DESIGN_SOURCE, SKIN_DESIGN_TARGET, SKIN_DESIGN_TARGET_TMP

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.NimManager import nimmanager
from Components.Sources.StaticText import StaticText
from Components.Console import Console
from Components.Label import Label
from shutil import move, copy, rmtree, copytree
from enigma import ePicLoad, eListboxPythonMultiContent, gFont, getDesktop
from ColorsSettingsView import ColorsSettingsView
from WeatherSettingsView import WeatherSettingsView
from OtherSettingsView import OtherSettingsView
from FontsSettingsView import FontsSettingsView
from BackupSettingsView import BackupSettingsView
from SkinpartSettingsView import SkinpartSettingsView
from os import path, remove, statvfs, listdir, stat as statfile
from PIL import Image
from boxbranding import getBoxType
#############################################################

class MainMenuList(MenuList):
    def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 50, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth == 3840:
            self.l.setFont(0, gFont("Regular", int(font0*3)))
            self.l.setFont(1, gFont("Regular", int(font1*3)))
            self.l.setItemHeight(int(itemHeight*3))
        elif screenwidth and screenwidth == 1920:
            self.l.setFont(0, gFont("Regular", int(font0*1.5)))
            self.l.setFont(1, gFont("Regular", int(font1*1.5)))
            self.l.setItemHeight(int(itemHeight*1.5))
        else:
            self.l.setFont(0, gFont("Regular", font0))
            self.l.setFont(1, gFont("Regular", font1))
            self.l.setItemHeight(itemHeight)

#############################################################

def MenuEntryItem(itemDescription, key, helptext):
    res = [(itemDescription, key, helptext)]
    screenwidth = getDesktop(0).size().width()
    if screenwidth and screenwidth == 3840:
        res.append(MultiContentEntryText(pos=(30, 15), size=(1320, 135), font=0, text=itemDescription, ))
    elif screenwidth and screenwidth == 1920:
        res.append(MultiContentEntryText(pos=(15, 8), size=(660, 68), font=0, text=itemDescription, ))
    else:
        res.append(MultiContentEntryText(pos=(10, 5), size=(440, 45), font=0, text=itemDescription))
    return res

#############################################################

skinReady = False
skinReadyCode = 0

class MainSettingsView(Screen):
    skin = """
  <screen name="MyMetrixLiteMainSettingsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
    <widget name="menuList" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="applyBtn" position="257,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
    <widget name="logo" position="838,100" size="258,58" zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/MyMetrixLiteWeatherLogo.png" alphatest="blend" />
    <widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["logo"] = Pixmap()
        self["helperimage"] = Pixmap()
        self["helpertext"] = Label()

        self["titleText"] = StaticText("")
        self["titleText"].setText(_("MyMetrixLite"))

        self["cancelBtn"] = StaticText("")
        self["cancelBtn"].setText(_("Cancel"))

        self["applyBtn"] = StaticText("")
        self["applyBtn"].setText(_("Apply changes"))

        self.applyChangesFirst = args
        if self.applyChangesFirst:
            self.checkEHDinstalled()

        self["actions"] = ActionMap(
            [
                "OkCancelActions",
                "DirectionActions",
                "InputActions",
                "ColorActions"
            ],
            {
                "ok": self.ok,
                "red": self.exit,
                "green": self.checkEHDinstalled,
                "cancel": self.exit
            }, -1)

        list = []
        list.append(MenuEntryItem(_("Font settings"), "FONT", _("helptext")))
        list.append(MenuEntryItem(_("Color settings"), "COLOR", _("helptext")))
        list.append(MenuEntryItem(_("Weather settings"), "WEATHER", _("helptext")))
        list.append(MenuEntryItem(_("Other settings"), "OTHER", _("helptext")))
        if path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/DesignSettings.py"):
            from DesignSettingsView import DesignSettingsView
            list.append(MenuEntryItem(_("Design settings"), "DESIGN", _("helptext")))
        list.append(MenuEntryItem(_("Skinpart settings"), "SKINPART", _("helptext")))
        list.append("")
        list.append(MenuEntryItem(_("Backup & Restore my settings"), "BACKUP", _("helptext")))

        self["menuList"] = MainMenuList([], font0=24, font1=16, itemHeight=50)
        self["menuList"].l.setList(list)

        if not self.__selectionChanged in self["menuList"].onSelectionChanged:
            self["menuList"].onSelectionChanged.append(self.__selectionChanged)

        self.onChangedEntry = []
        self.onLayoutFinish.append(self.UpdatePicture)

    def checkEHDinstalled(self):
        initColorsConfig()
        initWeatherConfig()
        initOtherConfig()
        initFontsConfig()
        #first check is ehd tested, ehd-settings and available ehd-icons
        tested = config.plugins.MyMetrixLiteOther.EHDtested.value.split('_|_')
        EHDtested = len(tested) == 2 and getBoxType() in tested[0] and config.plugins.MyMetrixLiteOther.EHDenabled.value in tested[1]
        if config.plugins.MyMetrixLiteOther.EHDenabled.value == '0':
            self.EHDenabled = False
            self.EHDfactor = 1
            self.EHDres = 'HD'
            self.EHDtxt = 'Standard HD'
        elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '1' and EHDtested:
            self.EHDenabled = True
            self.EHDfactor = 1.5
            self.EHDres = 'FHD'
            self.EHDtxt = 'Full HD'
        elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '2' and EHDtested:
            self.EHDenabled = True
            self.EHDfactor = 3
            self.EHDres = 'UHD'
            self.EHDtxt = 'Ultra HD'
        else:
            self.resetEHD()
            return

        if self.EHDenabled:
            self.Console = Console()
            self.service_name = 'enigma2-plugin-skins-metrix-atv-%s-icons' % self.EHDres.lower()
            self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkEHDicons)
        else:
            self.applyChanges()

    def checkEHDicons(self, str, retval, extra_args):
        if 'Collected errors' in str or not str:
            stat = statvfs("/usr/share/enigma2/MetrixHD/")
            freeflash = stat.f_bavail * stat.f_bsize / 1024 / 1024
            filesize = 10
            if self.EHDres == 'UHD':
                filesize = 25
            if freeflash < filesize:
                global skinReadyCode
                skinReadyCode = 3
                self.installEHDcomplete("flash")
            else:
                self.Console.ePopen('/usr/bin/opkg install ' + self.service_name, self.installEHDcomplete)
        else:
            self.applyChanges()

    def checkEHDsettingsCallback(self, ret = None):
        self.session.open(OtherSettingsView)

    def installEHDcomplete(self, result, retval = None, extra_args = None):
        if 'Unknown package' in result or "Collected errors" in result or "flash" in result:
            if not "flash" in result:
                global skinReadyCode
                skinReadyCode = 4
            self.resetEHD()
        else:
            self.applyChanges()

    def resetEHD(self):
        if self.applyChangesFirst:
            self.EHDenabled = False
            self.EHDfactor = 1
            self.EHDres = 'HD'
            self.EHDtxt = 'Standard HD'
            self.applyChanges()
        else:
            self.session.openWithCallback(self.checkEHDsettingsCallback, MessageBox,_("Your enhanced hd settings are inconsistent. Please check this."), MessageBox.TYPE_INFO, timeout=10)

    def __del__(self):
        self["menuList"].onSelectionChanged.remove(self.__selectionChanged)

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        if self["helperimage"] is None or self["helperimage"].instance is None:
            return

        cur = self["menuList"].getCurrent()

        imageUrl = MAIN_IMAGE_PATH % "FFFFFF"

        self["logo"].hide()

        if cur:
            selectedKey = cur[0][1]

            if selectedKey == "COLOR":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteColor"
            elif selectedKey == "WEATHER":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteWeather"
                self["logo"].show()
            elif selectedKey == "OTHER":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteOther"
            elif selectedKey == "FONT":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteFont"
            elif selectedKey == "BACKUP":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteBackup"
            elif selectedKey == "SKINPART":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteSkinpart"
            elif selectedKey == "DESIGN":
                imageUrl = MAIN_IMAGE_PATH % "MyMetrixLiteSkinpart"

        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(imageUrl)
        self.showHelperText()

    def DecodePicture(self, PicInfo = ""):
        ptr = self.PicLoad.getData()
        self["helperimage"].instance.setPixmap(ptr)

    def ok(self):
        cur = self["menuList"].getCurrent()

        if cur:
            selectedKey = cur[0][1]

            if selectedKey == "COLOR":
                self.session.open(ColorsSettingsView)
            elif selectedKey == "WEATHER":
                self.session.open(WeatherSettingsView)
            elif selectedKey == "OTHER":
                self.session.open(OtherSettingsView)
            elif selectedKey == "FONT":
                self.session.open(FontsSettingsView)
            elif selectedKey == "BACKUP":
                self.session.open(BackupSettingsView)
            elif selectedKey == "SKINPART":
                self.session.open(SkinpartSettingsView)
            elif selectedKey == "DESIGN":
                self.session.open(DesignSettingsView)

    def reboot(self, message = None):
        if message is None:
            message = _("Do you really want to reboot now?")

        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, message, MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Restart GUI"))

    def applyChanges(self):
        print"MyMetrixLite apply Changes"
        global skinReady, skinReadyCode

        try:
            # make backup of skin.xml
            bname = "_original_file_.xml"
            f = open(SKIN_SOURCE, 'r')
            firstline = f.readline()
            f.close()
            if '<!-- original file -->' in firstline:
                copy(SKIN_SOURCE,SKIN_SOURCE + bname)
            else:
                copy(SKIN_SOURCE + bname, SKIN_SOURCE)

            skinfiles_HD = [(SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP),
                        #(SKIN_TEMPLATES_SOURCE, SKIN_TEMPLATES_TARGET, SKIN_TEMPLATES_TARGET_TMP),
                        (SKIN_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP),
                        (SKIN_SECOND_INFOBAR_SOURCE, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP),
                        #(SKIN_SECOND_INFOBAR_ECM_SOURCE, SKIN_SECOND_INFOBAR_ECM_TARGET, SKIN_SECOND_INFOBAR_ECM_TARGET_TMP),
                        #(SKIN_INFOBAR_LITE_SOURCE, SKIN_INFOBAR_LITE_TARGET, SKIN_INFOBAR_LITE_TARGET_TMP),
                        (SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP),
                        (SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP),
                        (SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP),
                        #(SKIN_OPENATV_SOURCE, SKIN_OPENATV_TARGET, SKIN_OPENATV_TARGET_TMP),
                        #(SKIN_PLUGINS_SOURCE, SKIN_PLUGINS_TARGET, SKIN_PLUGINS_TARGET_TMP),
                        #(SKIN_UNCHECKED_SOURCE, SKIN_UNCHECKED_TARGET, SKIN_UNCHECKED_TARGET_TMP),
                        (SKIN_DESIGN_SOURCE, SKIN_DESIGN_TARGET, SKIN_DESIGN_TARGET_TMP)]

            skinfiles_EHD = [(SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP),
                        (SKIN_TEMPLATES_SOURCE, SKIN_TEMPLATES_TARGET, SKIN_TEMPLATES_TARGET_TMP),
                        (SKIN_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP),
                        (SKIN_SECOND_INFOBAR_SOURCE, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP),
                        (SKIN_SECOND_INFOBAR_ECM_SOURCE, SKIN_SECOND_INFOBAR_ECM_TARGET, SKIN_SECOND_INFOBAR_ECM_TARGET_TMP),
                        (SKIN_INFOBAR_LITE_SOURCE, SKIN_INFOBAR_LITE_TARGET, SKIN_INFOBAR_LITE_TARGET_TMP),
                        (SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP),
                        (SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP),
                        (SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP),
                        (SKIN_OPENATV_SOURCE, SKIN_OPENATV_TARGET, SKIN_OPENATV_TARGET_TMP),
                        (SKIN_PLUGINS_SOURCE, SKIN_PLUGINS_TARGET, SKIN_PLUGINS_TARGET_TMP),
                        (SKIN_UNCHECKED_SOURCE, SKIN_UNCHECKED_TARGET, SKIN_UNCHECKED_TARGET_TMP),
                        (SKIN_DESIGN_SOURCE, SKIN_DESIGN_TARGET, SKIN_DESIGN_TARGET_TMP)]

            ################
            # check free flash for _TARGET and _TMP files 
            ################

            stat = statvfs("/usr/share/enigma2/MetrixHD/")
            freeflash = stat.f_bavail * stat.f_bsize / 1024

            filesize = 0
            if self.EHDenabled:
                for file in skinfiles_EHD:
                    if path.exists(file[1]):
                        filesize += path.getsize(file[1])
                    else:
                        if path.exists(file[0]):
                            filesize += path.getsize(file[0]) * 2
            else:
                for file in skinfiles_HD:
                    if path.exists(file[1]):
                        filesize += path.getsize(file[1])
                    else:
                        filesize += path.getsize(file[0]) * 2
            reserve = 256
            filesize = filesize/1024 + reserve 

            if freeflash < filesize:
                skinReady = True
                skinReadyCode = 2
                if not self.applyChangesFirst:
                    self.session.open(MessageBox, _("Not enough free flash memory to create the new %s skin files. ( %d kb is required )") % (self.EHDtxt, filesize), MessageBox.TYPE_ERROR)
                return

            ################
            # InfoBar
            ################

            infobarSkinSearchAndReplace = []

            '''
            i = 0
            tunerXml = ""
            for nimSlot in nimmanager.nim_slots:
                tunerData = getTunerPositionList()[i]

                tunerXml += self.getTunerXMLItem(nimSlot.getSlotID(), tunerData[0], tunerData[1], tunerData[2], tunerData[3], tunerData[4], tunerData[5], nimmanager.somethingConnected(nimSlot.slot))
                i += 1

            infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', tunerXml])
            '''

            if config.plugins.MyMetrixLiteOther.showTunerinfo.getValue() is True:
                if config.plugins.MyMetrixLiteOther.setTunerAuto.getValue() is False:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', '<panel name="INFOBARTUNERINFO-%d" />' % config.plugins.MyMetrixLiteOther.setTunerManual.getValue()])
                else:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', '<panel name="INFOBARTUNERINFO-%d" />' % self.getTunerCount()])
            else:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', '']) 

            if config.plugins.MyMetrixLiteOther.showInfoBarClock.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            if config.plugins.MetrixWeather.enabled.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARWEATHERWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons.getValue() is False: 
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARSERVICEINFO" />', '']) 

            if config.plugins.MyMetrixLiteOther.showRecordstate.getValue() is False: 
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARRECORDSTATE" />', '']) 

            if config.plugins.MyMetrixLiteOther.showSnr.getValue() is False: 
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARSNR" />', '']) 
            else:
                if (config.plugins.MyMetrixLiteOther.showOrbitalposition.getValue() and config.plugins.MyMetrixLiteOther.showInfoBarResolution.getValue() and config.plugins.MyMetrixLiteOther.showInfoBarResolutionExtended.getValue()) is True:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARSNR" />', '<panel name="INFOBARSNR-2" />' ])

            if config.plugins.MyMetrixLiteOther.showOrbitalposition.getValue() is False: 
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARORBITALPOSITION" />', '']) 
            else:
                if (config.plugins.MyMetrixLiteOther.showInfoBarResolution.getValue() and config.plugins.MyMetrixLiteOther.showInfoBarResolutionExtended.getValue()) is True:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARORBITALPOSITION" />', '<panel name="INFOBARORBITALPOSITION-2" />' ])

            if config.plugins.MyMetrixLiteOther.showInfoBarResolution.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARRESOLUTION" />', ''])
            else:
                if config.plugins.MyMetrixLiteOther.showInfoBarResolutionExtended.getValue() is True:
                    infobarSkinSearchAndReplace.append(['<panel name="INFOBARRESOLUTION" />', '<panel name="INFOBARRESOLUTION-2" />' ])

            if config.plugins.MyMetrixLiteOther.showSTBinfo.getValue() is True:
                infobarSkinSearchAndReplace.append(['<!--panel name="STBINFO" /-->', '<panel name="STBINFO" />'])

            channelNameXML = self.getChannelNameXML(
                "30,455",
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                config.plugins.MyMetrixLiteOther.showChannelName.getValue()
            )
            infobarSkinSearchAndReplace.append(['<panel name="CHANNELNAME" />', channelNameXML])


            # SecondInfoBar
            skin_lines = appendSkinFile(SKIN_SECOND_INFOBAR_SOURCE, infobarSkinSearchAndReplace)

            xFile = open(SKIN_SECOND_INFOBAR_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            # InfoBar
            if config.plugins.MyMetrixLiteOther.showExtendedinfo.getValue() is True:
                infobarSkinSearchAndReplace.append(['<!--panel name="INFOBAREXTENDEDINFO" /-->', '<panel name="INFOBAREXTENDEDINFO" />']) 

            skin_lines = appendSkinFile(SKIN_INFOBAR_SOURCE, infobarSkinSearchAndReplace)

            xFile = open(SKIN_INFOBAR_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            ################
            # ChannelSelection
            ################

            channelSelectionSkinSearchAndReplace = []

            primetime = ""
            if int(config.plugins.MyMetrixLiteOther.SkinDesign.value) > 1 and (config.plugins.MyMetrixLiteOther.channelSelectionStyle.value == "CHANNELSELECTION-1" or config.plugins.MyMetrixLiteOther.channelSelectionStyle.value == "CHANNELSELECTION-2") and config.plugins.MyMetrixLiteOther.channelSelectionShowPrimeTime.value:
                primetime = "P"
            channelSelectionSkinSearchAndReplace.append(['<panel name="CHANNELSELECTION-1" />', '<panel name="%s%s" />' % (config.plugins.MyMetrixLiteOther.channelSelectionStyle.getValue(),primetime)])

            skin_lines = appendSkinFile(SKIN_CHANNEL_SELECTION_SOURCE, channelSelectionSkinSearchAndReplace)

            xFile = open(SKIN_CHANNEL_SELECTION_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            ################
            # MoviePlayer
            ################

            moviePlayerSkinSearchAndReplace = []

            if config.plugins.MetrixWeather.MoviePlayer.getValue() is False or config.plugins.MetrixWeather.enabled.getValue() is False:
                moviePlayerSkinSearchAndReplace.append(['<panel name="INFOBARWEATHERWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer.getValue() is True:
                if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "1":
                    moviePlayerSkinSearchAndReplace.append(['<!--panel name="STBINFOMOVIEPLAYER" /-->', '<panel name="STBINFOMOVIEPLAYER" />'])
                else:
                    moviePlayerSkinSearchAndReplace.append(['<!--panel name="STBINFO" /-->', '<panel name="STBINFO" />'])

            if config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer.getValue() is False:
                moviePlayerSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            namepos = "30,465"
            if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
                if config.plugins.MyMetrixLiteOther.showMoviePlayerResolutionExtended.getValue() is True:
                    moviePlayerSkinSearchAndReplace.append(['<panel name="RESOLUTIONMOVIEPLAYER" />', '<panel name="RESOLUTIONMOVIEPLAYER-2" />' ])
                moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_1" />', '<panel name="MoviePlayer_2" />' ])
            elif config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "3":
                moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_1" />', '<panel name="MoviePlayer_3" />' ])
                namepos = "30,535"

            channelNameXML = self.getChannelNameXML(
                namepos,
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                #config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                False,
                config.plugins.MyMetrixLiteOther.showMovieName.getValue()
            )
            moviePlayerSkinSearchAndReplace.append(['<panel name="MOVIENAME" />', channelNameXML])

            if config.plugins.MyMetrixLiteOther.showMovieTime.getValue() == "2":
                moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_1_time" />', '<panel name="MoviePlayer_' + config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() + '_time" />' ])
            else:
                moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_1_time" />', '' ])

            skin_lines = appendSkinFile(SKIN_MOVIEPLAYER_SOURCE, moviePlayerSkinSearchAndReplace)

            xFile = open(SKIN_MOVIEPLAYER_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            ################
            # EMC
            ################

            EMCSkinSearchAndReplace = []

            if config.plugins.MetrixWeather.MoviePlayer.getValue() is False or config.plugins.MetrixWeather.enabled.getValue() is False:
                EMCSkinSearchAndReplace.append(['<panel name="INFOBARWEATHERWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showSTBinfoMoviePlayer.getValue() is True:
                if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "1":
                    EMCSkinSearchAndReplace.append(['<!--panel name="STBINFOMOVIEPLAYER" /-->', '<panel name="STBINFOMOVIEPLAYER" />'])
                else:
                    EMCSkinSearchAndReplace.append(['<!--panel name="STBINFO" /-->', '<panel name="STBINFO" />'])

            if config.plugins.MyMetrixLiteOther.showInfoBarClockMoviePlayer.getValue() is False:
                EMCSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover.getValue() == "small":
                if config.plugins.MyMetrixLiteOther.showEMCMediaCenterCoverInfobar.getValue() is True and config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
                    EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenterCover_no" />', '<panel name="EMCMediaCenterCover_small_infobar" />'])
                else:
                    EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenterCover_no" />', '<panel name="EMCMediaCenterCover_small" />'])
            elif config.plugins.MyMetrixLiteOther.showEMCMediaCenterCover.getValue() == "large":
                EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenterCover_no" />', '<panel name="EMCMediaCenterCover_large" />'])

            if config.plugins.MyMetrixLiteOther.showEMCSelectionCover.getValue() == "small":
                EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionCover_no" />', '<panel name="EMCSelectionCover_small" />'])
            elif config.plugins.MyMetrixLiteOther.showEMCSelectionCover.getValue() == "large":
                EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionCover_no" />', '<panel name="EMCSelectionCover_large" />'])
                if config.plugins.MyMetrixLiteOther.showEMCSelectionCoverLargeDescription.getValue() is False:
                    EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionCover_large_description_on" />', '<panel name="EMCSelectionCover_large_description_off" />'])

            if config.plugins.MyMetrixLiteOther.showEMCSelectionRows.getValue() == "2":
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="90" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="140" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="20" CoolFont="epg_text;13" CoolSelectFont="epg_text;13" CoolDateFont="epg_text;13" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="8" CoolBarSize="50,7" CoolBarSizeSa="50,7" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="531" CoolFolderSize="546" CoolDatePos="625" CoolDateHPos="1" CoolDateWidth="80" CoolPiconPos="90" CoolPiconHPos="1" CoolPiconWidth="30" CoolPiconHeight="17" CoolMoviePiconPos="125" CoolMoviePiconSize="498" CoolCSWidth="80" CoolDirInfoWidth="80"'])
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="542" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="88" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="20" CoolFont="epg_text;13" CoolSelectFont="epg_text;13" CoolDateFont="epg_text;13" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="8" CoolBarSize="50,7" CoolBarSizeSa="50,7" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="532" CoolFolderSize="546" CoolDatePos="625" CoolDateHPos="1" CoolDateWidth="80" CoolPiconPos="592" CoolPiconHPos="1" CoolPiconWidth="30" CoolPiconHeight="17" CoolMoviePiconPos="88" CoolMoviePiconSize="498" CoolCSWidth="80" CoolDirInfoWidth="80"'])
            elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.getValue() == "1":
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="90" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="140" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="24" CoolFont="epg_text;17" CoolSelectFont="epg_text;17" CoolDateFont="epg_text;15" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="2" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="10" CoolBarSize="50,8" CoolBarSizeSa="50,8" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="516" CoolFolderSize="566" CoolDatePos="610" CoolDateHPos="1" CoolDateWidth="90" CoolPiconPos="90" CoolPiconHPos="2" CoolPiconWidth="35" CoolPiconHeight="20" CoolMoviePiconPos="130" CoolMoviePiconSize="470" CoolCSWidth="90" CoolDirInfoWidth="90"'])
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="542" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="88" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="24" CoolFont="epg_text;17" CoolSelectFont="epg_text;17" CoolDateFont="epg_text;15" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="2" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="10" CoolBarSize="50,8" CoolBarSizeSa="50,8" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="516" CoolFolderSize="566" CoolDatePos="610" CoolDateHPos="1" CoolDateWidth="90" CoolPiconPos="570" CoolPiconHPos="2" CoolPiconWidth="35" CoolPiconHeight="20" CoolMoviePiconPos="88" CoolMoviePiconSize="470" CoolCSWidth="90" CoolDirInfoWidth="90"'])
            elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.getValue() == "-1":
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="90" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="140" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="40" CoolFont="epg_text;24" CoolSelectFont="epg_text;20" CoolDateFont="epg_text;24" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="3" CoolIconPos="5" CoolIconHPos="7" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="16" CoolBarSize="50,12" CoolBarSizeSa="50,12" CoolMoviePos="88" CoolMovieHPos="3" CoolMovieSize="471" CoolFolderSize="524" CoolDatePos="565" CoolDateHPos="3" CoolDateWidth="135" CoolPiconPos="90" CoolPiconHPos="6" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="140" CoolMoviePiconSize="423" CoolCSWidth="135" CoolDirInfoWidth="135"'])
                EMCSkinSearchAndReplace.append(['itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;18" CoolDateFont="epg_text;20" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="1" CoolIconPos="5" CoolIconHPos="3" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="88" CoolMovieHPos="1" CoolMovieSize="496" CoolFolderSize="546" CoolDatePos="585" CoolDateHPos="1" CoolDateWidth="115" CoolPiconPos="542" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="88" CoolMoviePiconSize="448" CoolCSWidth="115" CoolDirInfoWidth="115"'\
                                               ,'itemHeight="40" CoolFont="epg_text;24" CoolSelectFont="epg_text;20" CoolDateFont="epg_text;24" CoolSelNumTxtWidth="26" CoolProgressPos="35" CoolProgressHPos="3" CoolIconPos="5" CoolIconHPos="7" CoolIconSize="24,24" CoolBarPos="32" CoolBarHPos="16" CoolBarSize="50,12" CoolBarSizeSa="50,12" CoolMoviePos="88" CoolMovieHPos="3" CoolMovieSize="471" CoolFolderSize="524" CoolDatePos="565" CoolDateHPos="3" CoolDateWidth="135" CoolPiconPos="522" CoolPiconHPos="6" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="88" CoolMoviePiconSize="423" CoolCSWidth="135" CoolDirInfoWidth="135"'])

            posNR = False
            if not self.applyChangesFirst:
                try:
                    posNR = config.EMC.movie_picons_pos.getValue() == "nr"
                except:
                    print "Error: find emc config - it's not installed ?"
            else:
                f=open("/etc/enigma2/settings", "r")
                s=f.read()
                f.close()
                posNR = "config.EMC.movie_picons_pos=nr" in s

            if posNR:
                EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionList_picon_left" />', '<panel name="EMCSelectionList_picon_right" />'])
                EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionList_large_description_picon_left" />', '<panel name="EMCSelectionList_large_description_picon_right" />'])

            namepos = "30,465"
            if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
                if config.plugins.MyMetrixLiteOther.showMoviePlayerResolutionExtended.getValue() is True:
                    EMCSkinSearchAndReplace.append(['<panel name="RESOLUTIONMOVIEPLAYER" />', '<panel name="RESOLUTIONMOVIEPLAYER-2" />' ])
                EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_1" />', '<panel name="EMCMediaCenter_2" />' ])
            elif config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "3":
                EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_1" />', '<panel name="EMCMediaCenter_3" />' ])
                namepos = "30,535"

            channelNameXML = self.getChannelNameXML(
                namepos,
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                #config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                False,
                config.plugins.MyMetrixLiteOther.showMovieName.getValue()
            )
            EMCSkinSearchAndReplace.append(['<panel name="MOVIENAME" />', channelNameXML])

            if config.plugins.MyMetrixLiteOther.showMovieTime.getValue() == "2":
                EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_1_time" />', '<panel name="EMCMediaCenter_' + config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() + '_time" />' ])
            else:
                EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_1_time" />', '' ])

            EMCSkinSearchAndReplace.append(['WatchingColor="#D8C100"', 'WatchingColor="#' + config.plugins.MyMetrixLiteColors.emcWatchingColor.value + '"' ])
            EMCSkinSearchAndReplace.append(['FinishedColor="#5FA816"', 'FinishedColor="#' + config.plugins.MyMetrixLiteColors.emcFinishedColor.value + '"' ])
            EMCSkinSearchAndReplace.append(['RecordingColor="#E51400"', 'RecordingColor="#' + config.plugins.MyMetrixLiteColors.emcRecordingColor.value + '"' ])

            if config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.getValue() is False:
                EMCSkinSearchAndReplace.append(['CoolHighlightColor="1"', 'CoolHighlightColor="0"' ])

            skin_lines = appendSkinFile(SKIN_EMC_SOURCE, EMCSkinSearchAndReplace)

            xFile = open(SKIN_EMC_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            ################
            # Design
            ################

            DESIGNSkinSearchAndReplace = []

            #SkinDesign
            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignLUC.getValue()
            if confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.upperleftcornertransparency.value + config.plugins.MyMetrixLiteColors.upperleftcornerbackground.value)
                width = config.plugins.MyMetrixLiteOther.SkinDesignLUCwidth.value
                height = config.plugins.MyMetrixLiteOther.SkinDesignLUCheight.value
                posx = 0
                posy = 0
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignLUCposz.value)
                newlines = (('<eLabel name="upperleftcorner-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="upperleftcorner-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperleftcorner-s" position="0,0" zPosition="-105" size="40,25" backgroundColor="#1A27408B" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperleftcorner-m" position="0,0" zPosition="-105" size="40,25" backgroundColor="#1A27408B" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperleftcorner-s" position="0,0" zPosition="-105" size="40,25" backgroundColor="#1A27408B" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperleftcorner-m" position="0,0" zPosition="-105" size="40,25" backgroundColor="#1A27408B" /-->', newlinem ])

            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignLLC.getValue()
            if  confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.lowerleftcornertransparency.value + config.plugins.MyMetrixLiteColors.lowerleftcornerbackground.value)
                width = config.plugins.MyMetrixLiteOther.SkinDesignLLCwidth.value
                height = int(config.plugins.MyMetrixLiteOther.SkinDesignLLCheight.value)
                posx = 0
                posy = 720 - height
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignLLCposz.value)
                newlines = (('<eLabel name="lowerleftcorner-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="lowerleftcorner-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerleftcorner-s" position="0,675" zPosition="-105" size="40,45" backgroundColor="#1A27408B" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerleftcorner-m" position="0,675" zPosition="-105" size="40,45" backgroundColor="#1A27408B" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerleftcorner-s" position="0,675" zPosition="-105" size="40,45" backgroundColor="#1A27408B" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerleftcorner-m" position="0,675" zPosition="-105" size="40,45" backgroundColor="#1A27408B" /-->', newlinem ])

            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignRUC.getValue()
            if  confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.upperrightcornertransparency.value + config.plugins.MyMetrixLiteColors.upperrightcornerbackground.value)
                width = int(config.plugins.MyMetrixLiteOther.SkinDesignRUCwidth.value)
                height = config.plugins.MyMetrixLiteOther.SkinDesignRUCheight.value
                posx = 1280 - width
                posy = 0
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignRUCposz.value)
                newlines = (('<eLabel name="upperrightcorner-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="upperrightcorner-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperrightcorner-s" position="1240,0" zPosition="-105" size="40,60" backgroundColor="#1A0F0F0F" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperrightcorner-m" position="1240,0" zPosition="-105" size="40,60" backgroundColor="#1A0F0F0F" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperrightcorner-s" position="1240,0" zPosition="-105" size="40,60" backgroundColor="#1A0F0F0F" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="upperrightcorner-m" position="1240,0" zPosition="-105" size="40,60" backgroundColor="#1A0F0F0F" /-->', newlinem ])

            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignRLC.getValue()
            if  confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.lowerrightcornertransparency.value + config.plugins.MyMetrixLiteColors.lowerrightcornerbackground.value)
                width = int(config.plugins.MyMetrixLiteOther.SkinDesignRLCwidth.value)
                height = int(config.plugins.MyMetrixLiteOther.SkinDesignRLCheight.value)
                posx = 1280 - width
                posy = 720 - height
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignRLCposz.value)
                newlines = (('<eLabel name="lowerrightcorner-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="lowerrightcorner-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerrightcorner-s" position="1240,640" zPosition="-105" size="40,80" backgroundColor="#1A0F0F0F" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerrightcorner-m" position="1240,640" zPosition="-105" size="40,80" backgroundColor="#1A0F0F0F" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerrightcorner-s" position="1240,640" zPosition="-105" size="40,80" backgroundColor="#1A0F0F0F" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="lowerrightcorner-m" position="1240,640" zPosition="-105" size="40,80" backgroundColor="#1A0F0F0F" /-->', newlinem ])

            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignOLH.getValue()
            if  confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.optionallayerhorizontaltransparency.value + config.plugins.MyMetrixLiteColors.optionallayerhorizontalbackground.value)
                width = config.plugins.MyMetrixLiteOther.SkinDesignOLHwidth.value
                height = config.plugins.MyMetrixLiteOther.SkinDesignOLHheight.value
                posx = config.plugins.MyMetrixLiteOther.SkinDesignOLHposx.value
                posy = config.plugins.MyMetrixLiteOther.SkinDesignOLHposy.value
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignOLHposz.value)
                newlines = (('<eLabel name="optionallayerhorizontal-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="optionallayerhorizontal-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayerhorizontal-s" position="0,655" zPosition="-105" size="1127,30" backgroundColor="#1A27408B" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayerhorizontal-m" position="0,655" zPosition="-105" size="1127,30" backgroundColor="#1A27408B" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayerhorizontal-s" position="0,655" zPosition="-105" size="1127,30" backgroundColor="#1A27408B" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayerhorizontal-m" position="0,655" zPosition="-105" size="1127,30" backgroundColor="#1A27408B" /-->', newlinem ])

            confvalue = config.plugins.MyMetrixLiteOther.SkinDesignOLV.getValue()
            if  confvalue != "no": 
                color = (config.plugins.MyMetrixLiteColors.optionallayerverticaltransparency.value + config.plugins.MyMetrixLiteColors.optionallayerverticalbackground.value)
                width = config.plugins.MyMetrixLiteOther.SkinDesignOLVwidth.value
                height = config.plugins.MyMetrixLiteOther.SkinDesignOLVheight.value
                posx = config.plugins.MyMetrixLiteOther.SkinDesignOLVposx.value
                posy = config.plugins.MyMetrixLiteOther.SkinDesignOLVposy.value
                posz = -105 + int(config.plugins.MyMetrixLiteOther.SkinDesignOLVposz.value)
                newlines = (('<eLabel name="optionallayervertical-s" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                newlinem = (('<eLabel name="optionallayervertical-m" position="%s,%s" zPosition="%s" size="%s,%s" backgroundColor="#%s" />') % (posx, posy, posz, width, height, color))
                if confvalue == "both": 
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayervertical-s" position="102,51" zPosition="-105" size="60,669" backgroundColor="#1A27408B" /-->', newlines ])
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayervertical-m" position="102,51" zPosition="-105" size="60,669" backgroundColor="#1A27408B" /-->', newlinem ])
                elif confvalue == "screens":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayervertical-s" position="102,51" zPosition="-105" size="60,669" backgroundColor="#1A27408B" /-->', newlines ])
                elif confvalue == "menus":
                    DESIGNSkinSearchAndReplace.append(['<!--eLabel name="optionallayervertical-m" position="102,51" zPosition="-105" size="60,669" backgroundColor="#1A27408B" /-->', newlinem ])

            if config.plugins.MyMetrixLiteOther.layeraunderlineshowmainlayer.value:
               DESIGNSkinSearchAndReplace.append(['<!--eLabel name="underline" position="40,88" size="1200,1" backgroundColor="layer-a-underline" zPosition="-1" /-->', '<eLabel name="underline" position="40,88" size="1200,1" backgroundColor="layer-a-underline" zPosition="-1" />' ])
               DESIGNSkinSearchAndReplace.append(['<!--eLabel name="underline" position="40,88" size="755,1" backgroundColor="layer-a-underline" zPosition="-1" /-->', '<eLabel name="underline" position="40,88" size="755,1" backgroundColor="layer-a-underline" zPosition="-1" />' ])

            if config.plugins.MyMetrixLiteOther.SkinDesignSpace.getValue() is True:
                newline1 = ('<panel name="template1_2layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + 's" />')
                newline2 = ('<panel name="INFOBAREPGWIDGET_Layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + 's" />')
                newline3 = ('<panel name="QuickMenu_Layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + 's" />')
                DESIGNSkinSearchAndReplace.append(['eLabel name="underline" position="40,88" size="755,1"', 'eLabel name="underline" position="40,88" size="750,1"' ])
            else:
                newline1 = ('<panel name="template1_2layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + '" />')
                newline2 = ('<panel name="INFOBAREPGWIDGET_Layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + '" />')
                newline3 = ('<panel name="QuickMenu_Layer-' + config.plugins.MyMetrixLiteOther.SkinDesign.value + '" />')
            DESIGNSkinSearchAndReplace.append(['<panel name="template1_2layer-1" />', newline1 ])
            DESIGNSkinSearchAndReplace.append(['<panel name="INFOBAREPGWIDGET_Layer-1" />', newline2 ])
            DESIGNSkinSearchAndReplace.append(['<panel name="QuickMenu_Layer-1" />', newline3 ])

            if int(config.plugins.MyMetrixLiteOther.SkinDesign.value) > 1:
                DESIGNSkinSearchAndReplace.append(['<ePixmap position="950,600" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/', '<ePixmap position="950,635" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/' ])
                DESIGNSkinSearchAndReplace.append(['<ePixmap position="1045,600" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/', '<ePixmap position="1045,635" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/' ])
                DESIGNSkinSearchAndReplace.append(['<ePixmap position="1140,600" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/', '<ePixmap position="1140,635" size="81,40" zPosition="10" pixmap="MetrixHD/buttons/' ])

            DESIGNSkinSearchAndReplace.append(['<panel name="INFOBAREXTENDEDINFO-1" />', '<panel name="INFOBAREXTENDEDINFO-' + config.plugins.MyMetrixLiteOther.ExtendedinfoStyle.value + '" />' ])

            # color gradient for ib,sib,mb,ibepg and quickemenu
            if config.plugins.MyMetrixLiteColors.cologradient.value != '0': # config.plugins.MyMetrixLiteOther.SkinDesignInfobarColorGradient.value:
                old = '<!--ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_bottom_ib.png" position="0,640" size="1280,80" zPosition="-1" /-->'
                new = '<ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_bottom_ib.png" position="0,640" size="1280,80" zPosition="-1" />'
                DESIGNSkinSearchAndReplace.append([old, new ])
                old = '<!--ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_bottom_epg.png" position="0,150" size="1280,80" zPosition="-1" /-->'
                new = '<ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_bottom_epg.png" position="0,150" size="1280,80" zPosition="-1" />'
                DESIGNSkinSearchAndReplace.append([old, new ])
                old = '<!--ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_top_ib.png" position="0,0" size="1280,30" zPosition="-1" /-->'
                new = '<ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_top_ib.png" position="0,0" size="1280,30" zPosition="-1" />'
                DESIGNSkinSearchAndReplace.append([old, new ])
                old = '<!--ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_top_qm.png" position="0,0" size="1280,30" zPosition="-1" /-->'
                new = '<ePixmap alphatest="blend" pixmap="MetrixHD/colorgradient_top_qm.png" position="0,0" size="1280,30" zPosition="-1" />'
                DESIGNSkinSearchAndReplace.append([old, new ])

            #picon
            if config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon.value == "1":
                posx = 33 + config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosX.value
                posy = 574 + config.plugins.MyMetrixLiteOther.SkinDesignInfobarXPiconPosY.value
                old = '<widget alphatest="blend" position="33,574" size="220,132" render="MetrixHDXPicon" source="session.CurrentService" transparent="1" zPosition="4">'
                new = '<widget alphatest="blend" position="' + str(posx) + ',' + str(posy) + '" size="220,132" render="MetrixHDXPicon" source="session.CurrentService" transparent="1" zPosition="4">'
            else:
                sizex = 267 + int(config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize.value * 1.66)
                sizey = 160 + int(config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconSize.value)
                posx = 0 + config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosX.value
                posy = 560 + config.plugins.MyMetrixLiteOther.SkinDesignInfobarZZZPiconPosY.value
                old = '<widget alphatest="blend" position="0,560" size="267,160" render="MetrixHDXPicon" source="session.CurrentService" transparent="1" zPosition="4">'
                new = '<widget alphatest="blend" position="' + str(posx) + ',' + str(posy) + '" size="' + str(sizex) + ',' + str(sizey) + '" render="MetrixHDXPicon" source="session.CurrentService" transparent="1" zPosition="4">'
                DESIGNSkinSearchAndReplace.append(['<panel name="IB_XPicon" />', '<panel name="IB_ZZZPicon" />' ])
            DESIGNSkinSearchAndReplace.append([old, new ])

            #pvr state
            if config.plugins.MyMetrixLiteOther.showPVRState.getValue() > "1":
                DESIGNSkinSearchAndReplace.append(['<screen name="PVRState" position="230,238"', '<screen name="PVRState_Standard" position="230,238"' ])
                DESIGNSkinSearchAndReplace.append(['<screen name="PVRState_Top" position="0,0"', '<screen name="PVRState" position="0,0"' ])
                if config.plugins.MyMetrixLiteOther.showPVRState.getValue() == "3":
                    DESIGNSkinSearchAndReplace.append(['<!--panel name="PVRState_3_ct" /-->', '<panel name="PVRState_3_ct" />' ])
                if config.plugins.MyMetrixLiteOther.showMovieTime.getValue() == "3":
                    DESIGNSkinSearchAndReplace.append(['<!--panel name="PVRState_3_mt" /-->', '<panel name="PVRState_3_mt" />' ])
            else:
                if config.plugins.MyMetrixLiteOther.showMovieTime.getValue() == "3":
                    DESIGNSkinSearchAndReplace.append(['<panel name="PVRState_1" />', '<panel name="PVRState_2" />' ])

            #graphical epg style
            if config.plugins.MyMetrixLiteOther.graphicalEpgStyle.getValue() == "2":
                DESIGNSkinSearchAndReplace.append(['<panel name="GraphicalEPG_1" />', '<panel name="GraphicalEPG_2" />' ])
                DESIGNSkinSearchAndReplace.append(['<panel name="GraphicalEPGPIG_1" />', '<panel name="GraphicalEPGPIG_2" />' ])

            skin_lines = appendSkinFile(SKIN_DESIGN_SOURCE, DESIGNSkinSearchAndReplace)

            ulsize = config.plugins.MyMetrixLiteOther.layeraunderlinesize.value
            ulposy = config.plugins.MyMetrixLiteOther.layeraunderlineposy.value
            xFile = open(SKIN_DESIGN_TARGET_TMP, "w")
            for xx in skin_lines:
                if '<eLabel name="underline"' in xx:
                    n1 = xx.find(' position=', 0)
                    n2 = xx.find(',', n1) 
                    n3 = xx.find('"', n2) 
                    n4 = xx.find(' size=', 0)
                    n5 = xx.find(',', n4) 
                    n6 = xx.find('"', n5) 
                    pos = int(xx[(n2+1):n3])-int(ulsize/2) + ulposy
                    xx = xx[:n2+1] + str(pos) + xx[n3:n5+1] + str(ulsize) + xx[n6:]

                xFile.writelines(xx)
            xFile.close()

            ################
            # Skin
            ################

            channelselectionservice = ('name="layer-a-channelselection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservice.value + '"')
            channelselectionserviceselected = ('name="layer-a-channelselection-foregroundColorSelected" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value + '"')
            channelselectionservicedescription = ('name="layer-a-channelselection-foreground-ServiceDescription" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value + '"')
            channelselectionservicedescriptionselected = ('name="layer-a-channelselection-foreground-ServiceDescriptionSelected" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value + '"')
            channelselectioncolorServiceRecorded = ('name="layer-a-channelselection-foreground-colorServiceRecorded" value="#00' + config.plugins.MyMetrixLiteColors.channelselectioncolorServiceRecorded.value + '"')
            channelselectioncolorServicePseudoRecorded = ('name="layer-a-channelselection-foreground-colorServicePseudoRecorded" value="#00' + config.plugins.MyMetrixLiteColors.channelselectioncolorServicePseudoRecorded.value + '"')
            channelselectioncolorServiceStreamed = ('name="layer-a-channelselection-foreground-colorServiceStreamed" value="#00' + config.plugins.MyMetrixLiteColors.channelselectioncolorServiceStreamed.value + '"')

            windowtitletext = ('name="title-foreground" value="#' + config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value + config.plugins.MyMetrixLiteColors.windowtitletext.value + '"')
            windowtitletextback = ('name="title-background" value="#' + config.plugins.MyMetrixLiteColors.windowtitletextbacktransparency.value + config.plugins.MyMetrixLiteColors.windowtitletextback.value + '"')
            backgroundtext = ('name="background-text" value="#' + config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value + config.plugins.MyMetrixLiteColors.backgroundtext.value + '"')
            backgroundtextback = ('name="text-background" value="#' + config.plugins.MyMetrixLiteColors.backgroundtextbacktransparency.value + config.plugins.MyMetrixLiteColors.backgroundtextback.value + '"')

            layerabackground = ('name="layer-a-background" value="#' + config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerabackground.value + '"')
            layeraforeground = ('name="layer-a-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraforeground.value + '"')
            layeraselectionbackground = ('name="layer-a-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layeraselectionbackground.value + '"')
            layeraselectionforeground = ('name="layer-a-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraselectionforeground.value + '"')
            layeraaccent1 = ('name="layer-a-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent1.value + '"')
            layeraaccent2 = ('name="layer-a-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent2.value + '"')
            layeraextendedinfo1 = ('name="layer-a-extendedinfo1" value="#00' + config.plugins.MyMetrixLiteColors.layeraextendedinfo1.value + '"')
            layeraextendedinfo2 = ('name="layer-a-extendedinfo2" value="#00' + config.plugins.MyMetrixLiteColors.layeraextendedinfo2.value + '"')
            layeraprogress = ('name="layer-a-progress" value="#' + config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value + config.plugins.MyMetrixLiteColors.layeraprogress.value + '"')
            layeraunderline = ('name="layer-a-underline" value="#' + config.plugins.MyMetrixLiteColors.layeraunderlinetransparency.value + config.plugins.MyMetrixLiteColors.layeraunderline.value + '"')

            layerbbackground = ('name="layer-b-background" value="#' + config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbbackground.value + '"')
            layerbforeground = ('name="layer-b-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbforeground.value + '"')
            layerbselectionbackground = ('name="layer-b-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbselectionbackground.value + '"')
            layerbselectionforeground = ('name="layer-b-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbselectionforeground.value + '"')
            layerbaccent1 = ('name="layer-b-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent1.value + '"')
            layerbaccent2 = ('name="layer-b-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent2.value + '"')
            layerbprogress = ('name="layer-b-progress" value="#' + config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value + config.plugins.MyMetrixLiteColors.layerbprogress.value + '"')

            epgeventdescriptionbackground = ('name="epg-eventdescription-background" value="#' + config.plugins.MyMetrixLiteColors.epgeventdescriptionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgeventdescriptionbackground.value + '"')
            epgeventdescriptionforeground = ('name="epg-eventdescription-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgeventdescriptionforeground.value + '"')
            epgbackground = ('name="epg-background" value="#' + config.plugins.MyMetrixLiteColors.epgbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgbackground.value + '"')
            epgborderlines = ('name="epg-borderlines" value="#' + config.plugins.MyMetrixLiteColors.epgborderlinestransparency.value + config.plugins.MyMetrixLiteColors.epgborderlines.value + '"')
            epgeventforeground = ('name="epg-event-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgeventforeground.value + '"')
            epgeventbackground = ('name="epg-event-background" value="#' + config.plugins.MyMetrixLiteColors.epgeventbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgeventbackground.value + '"')
            epgeventnowforeground = ('name="epg-event-now-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgeventnowforeground.value + '"')
            epgeventnowbackground = ('name="epg-event-now-background" value="#' + config.plugins.MyMetrixLiteColors.epgeventnowbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgeventnowbackground.value + '"')
            epgeventselectedforeground = ('name="epg-event-selected-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgeventselectedforeground.value + '"')
            epgeventselectedbackground = ('name="epg-event-selected-background" value="#' + config.plugins.MyMetrixLiteColors.epgeventselectedbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgeventselectedbackground.value + '"')
            epgserviceforeground = ('name="epg-service-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgserviceforeground.value + '"')
            epgservicebackground = ('name="epg-service-background" value="#' + config.plugins.MyMetrixLiteColors.epgservicebackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgservicebackground.value + '"')
            epgservicenowforeground = ('name="epg-service-now-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgservicenowforeground.value + '"')
            epgservicenowbackground = ('name="epg-service-now-background" value="#' + config.plugins.MyMetrixLiteColors.epgservicenowbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgservicenowbackground.value + '"')
            epgtimelineforeground = ('name="epg-timeline-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgtimelineforeground.value + '"')
            epgtimelinebackground = ('name="epg-timeline-background" value="#' + config.plugins.MyMetrixLiteColors.epgtimelinebackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgtimelinebackground.value + '"')

            layeratitleforeground = ('name="layer-a-title-foreground" value="#00' + config.plugins.MyMetrixLiteColors.windowtitletext.value + '"')
            layerabuttonforeground = ('name="layer-a-button-foreground" value="#00' + config.plugins.MyMetrixLiteColors.buttonforeground.value + '"')
            layeraclockforeground = ('name="layer-a-clock-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraclockforeground.value + '"')
            layerbclockforeground = ('name="layer-b-clock-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbclockforeground.value + '"')

            menufont = ('name="menufont" value="#00' + config.plugins.MyMetrixLiteColors.menufont.value + '"')
            menufontselected = ('name="menufontselected" value="#00' + config.plugins.MyMetrixLiteColors.menufontselected.value + '"')
            menubackground = ('name="menubackground" value="#' + config.plugins.MyMetrixLiteColors.menubackgroundtransparency.value + config.plugins.MyMetrixLiteColors.menubackground.value  + '"')
            menusymbolbackground = ('name="menusymbolbackground" value="#' + config.plugins.MyMetrixLiteColors.menusymbolbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.menusymbolbackground.value  + '"')
            infobarbackground = ('name="infobarbackground" value="#' + config.plugins.MyMetrixLiteColors.infobarbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.infobarbackground.value + '"')
            infobarprogress = ('name="infobarprogress" value="#' + config.plugins.MyMetrixLiteColors.infobarprogresstransparency.value + config.plugins.MyMetrixLiteColors.infobarprogress.value + '"')
            infobarfont1 = ('name="infobarfont1" value="#00' + config.plugins.MyMetrixLiteColors.infobarfont1.value + '"')
            infobarfont2 = ('name="infobarfont2" value="#00' + config.plugins.MyMetrixLiteColors.infobarfont2.value + '"')
            infobaraccent1 = ('name="infobaraccent1" value="#00' + config.plugins.MyMetrixLiteColors.infobaraccent1.value + '"')
            infobaraccent2 = ('name="infobaraccent2" value="#00' + config.plugins.MyMetrixLiteColors.infobaraccent2.value + '"')

            skinSearchAndReplace = []
            orgskinSearchAndReplace = [] # for some attributes (e.g. borderset)
            skinSearchAndReplace.append(['<!-- original file -->',''])
            orgskinSearchAndReplace.append(['<!-- original file -->','<!-- !!!copied and changed file!!! -->'])

            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground" value="#00FFFFFF"', channelselectionservice ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foregroundColorSelected" value="#00FFFFFF"', channelselectionserviceselected ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-ServiceDescription" value="#00BDBDBD"', channelselectionservicedescription ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-ServiceDescriptionSelected" value="#00FFFFFF"', channelselectionservicedescriptionselected ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-colorServiceRecorded" value="#00E51400"', channelselectioncolorServiceRecorded ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-colorServicePseudoRecorded" value="#000000CD"', channelselectioncolorServicePseudoRecorded ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-colorServiceStreamed" value="#00E51400"', channelselectioncolorServiceStreamed ])

            skinSearchAndReplace.append(['name="layer-a-background" value="#1A0F0F0F"', layerabackground ])
            skinSearchAndReplace.append(['name="layer-a-foreground" value="#00FFFFFF"', layeraforeground ])
            skinSearchAndReplace.append(['name="layer-a-selection-background" value="#1A27408B"', layeraselectionbackground ])
            skinSearchAndReplace.append(['name="layer-a-selection-foreground" value="#00FFFFFF"', layeraselectionforeground ])
            skinSearchAndReplace.append(['name="layer-a-accent1" value="#00BDBDBD"', layeraaccent1 ])
            skinSearchAndReplace.append(['name="layer-a-accent2" value="#006E6E6E"', layeraaccent2 ])
            skinSearchAndReplace.append(['name="layer-a-extendedinfo1" value="#00BDBDBD"', layeraextendedinfo1 ])
            skinSearchAndReplace.append(['name="layer-a-extendedinfo2" value="#006E6E6E"', layeraextendedinfo2 ])
            skinSearchAndReplace.append(['name="layer-a-progress" value="#1A27408B"', layeraprogress ])
            skinSearchAndReplace.append(['name="layer-a-underline" value="#00BDBDBD"', layeraunderline ])

            skinSearchAndReplace.append(['name="layer-b-background" value="#1A27408B"', layerbbackground ])
            skinSearchAndReplace.append(['name="layer-b-foreground" value="#00FFFFFF"', layerbforeground ])
            skinSearchAndReplace.append(['name="layer-b-selection-background" value="#1A0F0F0F"', layerbselectionbackground ])
            skinSearchAndReplace.append(['name="layer-b-selection-foreground" value="#00FFFFFF"', layerbselectionforeground ])
            skinSearchAndReplace.append(['name="layer-b-accent1" value="#00BDBDBD"', layerbaccent1 ])
            skinSearchAndReplace.append(['name="layer-b-accent2" value="#006E6E6E"', layerbaccent2 ])
            skinSearchAndReplace.append(['name="layer-b-progress" value="#1AFFFFFF"', layerbprogress ])

            skinSearchAndReplace.append(['name="title-foreground" value="#00FFFFFF"', windowtitletext ])
            skinSearchAndReplace.append(['name="title-background" value="#000F0F0F"', windowtitletextback ])
            skinSearchAndReplace.append(['name="background-text" value="#34FFFFFF"', backgroundtext ])
            skinSearchAndReplace.append(['name="text-background" value="#67FFFFFF"', backgroundtextback ])

            skinSearchAndReplace.append(['name="epg-eventdescription-background" value="#1A27408B"', epgeventdescriptionbackground ])
            skinSearchAndReplace.append(['name="epg-eventdescription-foreground" value="#00FFFFFF"', epgeventdescriptionforeground ])
            skinSearchAndReplace.append(['name="epg-background" value="#1A0F0F0F"', epgbackground ])
            skinSearchAndReplace.append(['name="epg-borderlines" value="#1ABDBDBD"', epgborderlines ])
            skinSearchAndReplace.append(['name="epg-event-foreground" value="#00FFFFFF"', epgeventforeground ])
            skinSearchAndReplace.append(['name="epg-event-background" value="#1A0F0F0F"', epgeventbackground ])
            skinSearchAndReplace.append(['name="epg-event-now-foreground" value="#00FFFFFF"', epgeventnowforeground ])
            skinSearchAndReplace.append(['name="epg-event-now-background" value="#1A000000"', epgeventnowbackground ])
            skinSearchAndReplace.append(['name="epg-event-selected-foreground" value="#00FFFFFF"', epgeventselectedforeground ])
            skinSearchAndReplace.append(['name="epg-event-selected-background" value="#1A27408B"', epgeventselectedbackground ])
            skinSearchAndReplace.append(['name="epg-service-foreground" value="#00FFFFFF"', epgserviceforeground ])
            skinSearchAndReplace.append(['name="epg-service-background" value="#1A0F0F0F"', epgservicebackground ])
            skinSearchAndReplace.append(['name="epg-service-now-foreground" value="#00FFFFFF"', epgservicenowforeground ])
            skinSearchAndReplace.append(['name="epg-service-now-background" value="#1A27408B"', epgservicenowbackground ])
            skinSearchAndReplace.append(['name="epg-timeline-foreground" value="#00F0A30A"', epgtimelineforeground ])
            skinSearchAndReplace.append(['name="epg-timeline-background" value="#1A000000"', epgtimelinebackground ])

            skinSearchAndReplace.append(['name="layer-a-title-foreground" value="#00FFFFFF"', layeratitleforeground ])
            skinSearchAndReplace.append(['name="layer-a-button-foreground" value="#00FFFFFF"', layerabuttonforeground ])
            skinSearchAndReplace.append(['name="layer-a-clock-foreground" value="#00FFFFFF"', layeraclockforeground ])
            skinSearchAndReplace.append(['name="layer-b-clock-foreground" value="#00FFFFFF"', layerbclockforeground ])

            skinSearchAndReplace.append(['name="menufont" value="#00FFFFFF"', menufont ])
            skinSearchAndReplace.append(['name="menufontselected" value="#00FFFFFF"', menufontselected ])
            skinSearchAndReplace.append(['name="menubackground" value="#1A0F0F0F"', menubackground ])
            skinSearchAndReplace.append(['name="menusymbolbackground" value="#1A0F0F0F"', menusymbolbackground ])
            skinSearchAndReplace.append(['name="infobarbackground" value="#1A0F0F0F"', infobarbackground ])
            skinSearchAndReplace.append(['name="infobarprogress" value="#1A27408B"', infobarprogress ])
            skinSearchAndReplace.append(['name="infobarfont1" value="#00FFFFFF"', infobarfont1 ])
            skinSearchAndReplace.append(['name="infobarfont2" value="#00BDBDBD"', infobarfont2 ])
            skinSearchAndReplace.append(['name="infobaraccent1" value="#00BDBDBD"', infobaraccent1 ])
            skinSearchAndReplace.append(['name="infobaraccent2" value="#006E6E6E"', infobaraccent2 ])

            #Borderset screens
            w = 5
            wt = 50
            if self.EHDenabled:
                w *= self.EHDfactor
                wt *= self.EHDfactor
            width = "%dpx" %w
            width_top = "%dpx" %wt

            color = config.plugins.MyMetrixLiteColors.windowborder_top.value
            if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width_top, color)):
                newline = (('<pixmap pos="bpTop" filename="MetrixHD/border/%s/%s.png" />') % (width_top, color))
                skinSearchAndReplace.append(['<pixmap pos="bpTop" filename="MetrixHD/border/50px/0F0F0F.png" />', newline ])
                orgskinSearchAndReplace.append(['<pixmap pos="bpTop" filename="MetrixHD/border/50px/0F0F0F.png" />', newline ])
            color = config.plugins.MyMetrixLiteColors.windowborder_bottom.value
            if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                newline = (('<pixmap pos="bpBottom" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                skinSearchAndReplace.append(['<pixmap pos="bpBottom" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])
                orgskinSearchAndReplace.append(['<pixmap pos="bpBottom" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])
            color = config.plugins.MyMetrixLiteColors.windowborder_left.value
            if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                newline = (('<pixmap pos="bpLeft" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                skinSearchAndReplace.append(['<pixmap pos="bpLeft" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])
                orgskinSearchAndReplace.append(['<pixmap pos="bpLeft" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])
            color = config.plugins.MyMetrixLiteColors.windowborder_right.value
            if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                newline = (('<pixmap pos="bpRight" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                skinSearchAndReplace.append(['<pixmap pos="bpRight" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])
                orgskinSearchAndReplace.append(['<pixmap pos="bpRight" filename="MetrixHD/border/5px/0F0F0F.png" />', newline ])

            #Border listbox
            width = config.plugins.MyMetrixLiteColors.listboxborder_topwidth.value
            if width != "no":
                color = config.plugins.MyMetrixLiteColors.listboxborder_top.value
                if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                    newline = (('<pixmap pos="bpTop" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                    skinSearchAndReplace.append(['<!--lb pixmap pos="bpTop" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
                    orgskinSearchAndReplace.append(['<!--lb pixmap pos="bpTop" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
            width = config.plugins.MyMetrixLiteColors.listboxborder_bottomwidth.value
            if width != "no":
                color = config.plugins.MyMetrixLiteColors.listboxborder_bottom.value
                if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                    newline = (('<pixmap pos="bpBottom" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                    skinSearchAndReplace.append(['<!--lb pixmap pos="bpBottom" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
                    orgskinSearchAndReplace.append(['<!--lb pixmap pos="bpBottom" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
            width = config.plugins.MyMetrixLiteColors.listboxborder_leftwidth.value
            if width != "no":
                color = config.plugins.MyMetrixLiteColors.listboxborder_left.value
                if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                    newline = (('<pixmap pos="bpLeft" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                    skinSearchAndReplace.append(['<!--lb pixmap pos="bpLeft" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
                    orgskinSearchAndReplace.append(['<!--lb pixmap pos="bpLeft" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
            width = config.plugins.MyMetrixLiteColors.listboxborder_rightwidth.value
            if width != "no":
                color = config.plugins.MyMetrixLiteColors.listboxborder_right.value
                if path.exists(("/usr/share/enigma2/MetrixHD/border/%s/%s.png") % (width, color)):
                    newline = (('<pixmap pos="bpRight" filename="MetrixHD/border/%s/%s.png" />') % (width, color))
                    skinSearchAndReplace.append(['<!--lb pixmap pos="bpRight" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])
                    orgskinSearchAndReplace.append(['<!--lb pixmap pos="bpRight" filename="MetrixHD/border/1px/FFFFFF.png" /-->', newline ])

            #fonts system
            type = config.plugins.MyMetrixLiteFonts.Lcd_type.value
            scale = config.plugins.MyMetrixLiteFonts.Lcd_scale.value
            old = '<font filename="/usr/share/fonts/lcd.ttf" name="LCD" scale="100" />'
            new = '<font filename="' + type + '" name="LCD" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.Replacement_type.value
            scale = config.plugins.MyMetrixLiteFonts.Replacement_scale.value
            old = '<font filename="/usr/share/fonts/ae_AlMateen.ttf" name="Replacement" scale="100" replacement="1" />'
            new = '<font filename="' + type + '" name="Replacement" scale="' + str(scale) + '" replacement="1" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.Console_type.value
            scale = config.plugins.MyMetrixLiteFonts.Console_scale.value
            old = '<font filename="/usr/share/fonts/tuxtxt.ttf" name="Console" scale="100" />'
            new = '<font filename="' + type + '" name="Console" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.Fixed_type.value
            scale = config.plugins.MyMetrixLiteFonts.Fixed_scale.value
            old = '<font filename="/usr/share/fonts/andale.ttf" name="Fixed" scale="100" />'
            new = '<font filename="' + type + '" name="Fixed" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.Arial_type.value
            scale = config.plugins.MyMetrixLiteFonts.Arial_scale.value
            old = '<font filename="/usr/share/fonts/nmsbd.ttf" name="Arial" scale="100" />'
            new = '<font filename="' + type + '" name="Arial" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            #fonts skin
            type = config.plugins.MyMetrixLiteFonts.Regular_type.value
            scale = config.plugins.MyMetrixLiteFonts.Regular_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="Regular" scale="95" />'
            new = '<font filename="' + type + '" name="Regular" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.RegularLight_type.value
            scale = config.plugins.MyMetrixLiteFonts.RegularLight_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="RegularLight" scale="95" />'
            new = '<font filename="' + type + '" name="RegularLight" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.SetrixHD_type.value
            scale = config.plugins.MyMetrixLiteFonts.SetrixHD_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="SetrixHD" scale="100" />'
            new = '<font filename="' + type + '" name="SetrixHD" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            scale = config.plugins.MyMetrixLiteFonts.Meteo_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/meteocons.ttf" name="Meteo" scale="100" />'
            new = '<font filename="/usr/share/enigma2/MetrixHD/fonts/meteocons.ttf" name="Meteo" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            #global
            type = config.plugins.MyMetrixLiteFonts.globaltitle_type.value
            scale = config.plugins.MyMetrixLiteFonts.globaltitle_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_title" scale="100" />'
            new = '<font filename="' + type + '" name="global_title" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.globalbutton_type.value
            scale = config.plugins.MyMetrixLiteFonts.globalbutton_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_button" scale="100" />'
            new = '<font filename="' + type + '" name="global_button" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.globalclock_type.value
            scale = config.plugins.MyMetrixLiteFonts.globalclock_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_clock" scale="100" />'
            new = '<font filename="' + type + '" name="global_clock" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.globallarge_type.value
            scale = config.plugins.MyMetrixLiteFonts.globallarge_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large" scale="100" />'
            new = '<font filename="' + type + '" name="global_large" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])
            else:
                type = "/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf"

            if config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText.value == "both":
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_menu" scale="' + str(scale) + '" />'
                skinSearchAndReplace.append([old, new ])
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_screen" scale="' + str(scale) + '" />'
                skinSearchAndReplace.append([old, new ])
            elif config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText.value == "menus":
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_menu" scale="' + str(scale) + '" />'
                skinSearchAndReplace.append([old, new ])
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_screen" scale="-1" />'
                skinSearchAndReplace.append([old, new ])
            elif config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText.value == "screens":
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_menu" scale="-1" />'
                skinSearchAndReplace.append([old, new ])
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_screen" scale="' + str(scale) + '" />'
                skinSearchAndReplace.append([old, new ])
            else:
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_menu" scale="-1" />'
                skinSearchAndReplace.append([old, new ])
                old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
                new = '<font filename="' + type + '" name="global_large_screen" scale="-1" />'
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.globalsmall_type.value
            scale = config.plugins.MyMetrixLiteFonts.globalsmall_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="global_small" scale="95" />'
            new = '<font filename="' + type + '" name="global_small" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.globalmenu_type.value
            scale = config.plugins.MyMetrixLiteFonts.globalmenu_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_menu" scale="100" />'
            new = '<font filename="' + type + '" name="global_menu" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            #screens
            type = config.plugins.MyMetrixLiteFonts.screenlabel_type.value
            scale = config.plugins.MyMetrixLiteFonts.screenlabel_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="screen_label" scale="95" />'
            new = '<font filename="' + type + '" name="screen_label" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.screentext_type.value
            scale = config.plugins.MyMetrixLiteFonts.screentext_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="screen_text" scale="95" />'
            new = '<font filename="' + type + '" name="screen_text" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.screeninfo_type.value
            scale = config.plugins.MyMetrixLiteFonts.screeninfo_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="screen_info" scale="100" />'
            new = '<font filename="' + type + '" name="screen_info" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            #channellist
            type = config.plugins.MyMetrixLiteFonts.epgevent_type.value
            scale = config.plugins.MyMetrixLiteFonts.epgevent_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="epg_event" scale="100" />'
            new = '<font filename="' + type + '" name="epg_event" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.epgtext_type.value
            scale = config.plugins.MyMetrixLiteFonts.epgtext_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="epg_text" scale="95" />'
            new = '<font filename="' + type + '" name="epg_text" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.epginfo_type.value
            scale = config.plugins.MyMetrixLiteFonts.epginfo_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="epg_info" scale="95" />'
            new = '<font filename="' + type + '" name="epg_info" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            #infobar
            type = config.plugins.MyMetrixLiteFonts.infobarevent_type.value
            scale = config.plugins.MyMetrixLiteFonts.infobarevent_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="infobar_event" scale="100" />'
            new = '<font filename="' + type + '" name="infobar_event" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            type = config.plugins.MyMetrixLiteFonts.infobartext_type.value
            scale = config.plugins.MyMetrixLiteFonts.infobartext_scale.value
            old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="infobar_text" scale="95" />'
            new = '<font filename="' + type + '" name="infobar_text" scale="' + str(scale) + '" />'
            if path.exists(type):
                skinSearchAndReplace.append([old, new ])

            if self.EHDenabled:
                skinSearchAndReplace.append(['skin_00_templates.xml', 'skin_00_templates.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00a_InfoBar.xml', 'skin_00a_InfoBar.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00b_SecondInfoBar.xml', 'skin_00b_SecondInfoBar.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00c_SecondInfoBarECM.xml', 'skin_00c_SecondInfoBarECM.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00d_InfoBarLite.xml', 'skin_00d_InfoBarLite.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00e_ChannelSelection.xml', 'skin_00e_ChannelSelection.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00f_MoviePlayer.xml', 'skin_00f_MoviePlayer.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00g_EMC.xml', 'skin_00g_EMC.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00o_openatv.xml', 'skin_00o_openatv.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00p_plugins.xml', 'skin_00p_plugins.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00u_unchecked.xml', 'skin_00u_unchecked.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00z_design.xml', 'skin_00z_design.MySkin.xml'])
            else:
                #skinSearchAndReplace.append(['skin_00_templates.xml', 'skin_00_templates.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00a_InfoBar.xml', 'skin_00a_InfoBar.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00b_SecondInfoBar.xml', 'skin_00b_SecondInfoBar.MySkin.xml'])
                #skinSearchAndReplace.append(['skin_00c_SecondInfoBarECM.xml', 'skin_00c_SecondInfoBarECM.MySkin.xml'])
                #skinSearchAndReplace.append(['skin_00d_InfoBarLite.xml', 'skin_00d_InfoBarLite.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00e_ChannelSelection.xml', 'skin_00e_ChannelSelection.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00f_MoviePlayer.xml', 'skin_00f_MoviePlayer.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00g_EMC.xml', 'skin_00g_EMC.MySkin.xml'])
                #skinSearchAndReplace.append(['skin_00o_openatv.xml', 'skin_00o_openatv.MySkin.xml'])
                #skinSearchAndReplace.append(['skin_00p_plugins.xml', 'skin_00p_plugins.MySkin.xml'])
                #skinSearchAndReplace.append(['skin_00u_screens_unchecked.xml', 'skin_00u_screens_unchecked.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00z_design.xml', 'skin_00z_design.MySkin.xml'])

            #skinparts
            skinpartdir='/usr/share/enigma2/MetrixHD/skinparts/'
            skinparts = ''
            for skinpart in listdir(skinpartdir):
                if path.isfile(skinpartdir + skinpart):
                    continue
                enabled = False
                partname = partpath = ''
                for file in listdir(skinpartdir + skinpart):
                    filepath = path.join(skinpartdir + skinpart, file)
                    if not path.isfile(filepath):
                        continue
                    if file == skinpart + '.xml':
                        partname = skinpart
                        partpath = filepath
                        EHDpath = skinpartdir + skinpart + '/' + skinpart + '.MySkin.xml'
                        TMPpath = skinpartdir + skinpart + '/' + skinpart + '.MySkin.xml.tmp'
                        #remove old MySkin files
                        if path.isfile(EHDpath):
                            remove(EHDpath)
                    if file == 'enabled':
                        enabled = True
                if partname and enabled:
                    if self.EHDenabled:
                        if skinparts:
                            skinparts += '\n\t<include filename="%s" />' %EHDpath
                        else:
                            skinparts = '<include filename="%s" />' %EHDpath
                        skinfiles_EHD.append((partpath, EHDpath, TMPpath))
                    else:
                        if skinparts:
                            skinparts += '\n\t<include filename="%s" />' %partpath
                        else:
                            skinparts = '<include filename="%s" />' %partpath

            if skinparts:
                skinSearchAndReplace.append(['<!-- placeholder_skinparts /-->', skinparts])

            #make skin file
            skin_lines = appendSkinFile(SKIN_SOURCE, skinSearchAndReplace)
            orgskin_lines = appendSkinFile(SKIN_SOURCE + bname, orgskinSearchAndReplace)

            xFile = open(SKIN_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            # write changed skin.xml
            xFile = open(SKIN_SOURCE, "w")
            for xx in orgskin_lines:
                xFile.writelines(xx)
            xFile.close()

            ################
            # EHD-skin
            ################

            #function "optionEHD" variables
            self.skinline_error = False
            self.pixmap_error = False
            self.round_par = int(config.plugins.MyMetrixLiteOther.EHDrounddown.value)
            self.font_size = int(config.plugins.MyMetrixLiteOther.EHDfontsize.value)
            self.font_offset = config.plugins.MyMetrixLiteOther.EHDfontoffset.value
            if config.plugins.MyMetrixLiteOther.SkinDesignInfobarPicon.value == "1":
                self.picon_zoom = 1 + ((self.EHDfactor - 1) * float(config.plugins.MyMetrixLiteOther.EHDpiconzoom.value))
                if not self.picon_zoom: self.picon_zoom = 1
            else:
                self.picon_zoom = self.EHDfactor
            self.EHD_addfiles = config.plugins.MyMetrixLiteOther.EHDadditionalfiles.value
            #variables end

            plustext = ""

            #EHD-option
            if self.EHDenabled:
                if not self.skinline_error:
                    print "--------   option%s   --------" % self.EHDres
                    for file in skinfiles_EHD:
                        if self.skinline_error:
                            break
                        if path.exists(file[2]):
                            self.optionEHD(file[2],file[1])
                        else:
                            self.optionEHD(file[0],file[1])
                    #additional files
                    if self.EHD_addfiles:
                        plustext = _("--- additional files start ---\n")
                        #antilogo.xml
                        file_a = "/etc/enigma2/antilogo.xml"
                        file_b = "/etc/enigma2/antilogo_HD.xml"
                        file_c = "/etc/enigma2/antilogo_%s.xml" % self.EHDres
                        if path.exists(file_a) and not path.exists(file_b) and not path.exists(file_c) and not self.skinline_error:
                            copy(file_a, file_b)
                            self.optionEHD(file_a,file_c)
                            plustext = plustext + _("Backup ") + file_a + " ---> " + file_b + _("\nNew calculated file is ") + file_c
                        elif path.exists(file_a) and path.exists(file_b) and not path.exists(file_c) and not self.skinline_error:
                            self.optionEHD(file_b,file_c)
                            plustext = plustext + _("Backup ") + file_b + ", " + _("\nNew calculated file is ") + file_c

                        if len(plustext) < 100:
                            plustext = plustext + _("No files found or files already exist.")
                        plustext = plustext + _("\n--- additional files end ---\n\n")

            #last step to ehd-mode - copy icon files for fixed paths in py-files
            if self.EHDenabled and not self.skinline_error:
                #set standard icons before copy new ehd icons (for saving new icons and clean start)
                self.iconFileCopy("HD")
                self.iconFolderCopy("HD")
                #----
                self.iconFileCopy(self.EHDres)
                self.iconFolderCopy(self.EHDres)
                self.makeGraphics(self.EHDfactor)
            else:
                self.iconFileCopy("HD")
                self.iconFolderCopy("HD")
                self.makeGraphics(1)

            #HD-standard
            if not self.EHDenabled or self.skinline_error:
                if self.skinline_error:
                    for file in skinfiles_EHD:
                        if path.exists(file[2]):
                            move(file[2],file[1])
                        else:
                            copy(file[0],file[1])
                else:
                    #remove old MySkin files from EHD-option
                    for file in skinfiles_EHD:
                        if path.exists(file[1]):
                            remove(file[1])
                    for file in skinfiles_HD:
                        if path.exists(file[2]):
                            move(file[2],file[1])

            #remove old _TMP files
            for file in skinfiles_EHD:
                if path.exists(file[2]):
                    remove(file[2])

            config.skin.primary_skin.setValue("MetrixHD/skin.MySkin.xml")
            config.skin.primary_skin.save()
            configfile.save()

            if self.skinline_error:
                skinReadyCode = 5
                plustext = plustext + _("Error creating %s skin. HD skin is used!\n\n") % self.EHDres
            elif not self.skinline_error and self.pixmap_error:
                skinReadyCode = 6
                plustext = plustext + _("One or more %s icons are missing. Using HD icons for this.\n\n") % self.EHDres

            text = plustext + _("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?")

            if not self.applyChangesFirst:
                self.reboot(text)

        except Exception as error:
            print error
            skinReadyCode = 1
            if not self.applyChangesFirst:
                self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

        skinReady = True

    def makeGraphics(self, factor):
		# epg
		color = self.makeNewColor(config.plugins.MyMetrixLiteColors.epgbackground.value, config.plugins.MyMetrixLiteColors.cologradient.value)
		cgfile = "/usr/share/enigma2/MetrixHD/colorgradient_bottom_epg.png"
		if color:
			self.makeColorGradient(cgfile, int(1280*factor), int(80*factor), color, int(8*factor), False)
		else:
			if path.isfile(cgfile): remove(cgfile)
		# ib
		color = self.makeNewColor(config.plugins.MyMetrixLiteColors.infobarbackground.value, config.plugins.MyMetrixLiteColors.cologradient.value)
		cgfile = "/usr/share/enigma2/MetrixHD/colorgradient_bottom_ib.png"
		if color:
			self.makeColorGradient(cgfile, int(1280*factor), int(80*factor), color, int(8*factor), False)
		else:
			if path.isfile(cgfile): remove(cgfile)
		cgfile = "/usr/share/enigma2/MetrixHD/colorgradient_top_ib.png"
		if color:
			self.makeColorGradient(cgfile, int(1280*factor), int(30*factor), color, int(3*factor), True)
		else:
			if path.isfile(cgfile): remove(cgfile)
		# layer a
		color = self.makeNewColor(config.plugins.MyMetrixLiteColors.layerabackground.value, config.plugins.MyMetrixLiteColors.cologradient.value)
		cgfile = "/usr/share/enigma2/MetrixHD/colorgradient_top_qm.png"
		if color:
			self.makeColorGradient(cgfile, int(1280*factor), int(30*factor), color, int(3*factor), True)
		else:
			if path.isfile(cgfile): remove(cgfile)

    def makeNewColor(self, color, coloroption):
		if coloroption == '0':
			return None
		elif coloroption == '1':
			return color
		elif len(coloroption) < 6: #modify current color
			coloroption = int(coloroption)
			r = int(color[-6:][:2],16)
			r -= r * 0.01 * int(coloroption)
			g = int(color[-4:][:2],16)
			g -= g * 0.01 * int(coloroption)
			b = int(color[-2:][:2],16)
			b -= b * 0.01 * int(coloroption)
			if r < 0: r = 0
			if g < 0: g = 0
			if b < 0: b = 0
			return "%.2x%.2x%.2x" %(int(r), int(g), int(b))
		elif len(coloroption) == 6:
			return coloroption
		else:
			return color

    def makeColorGradient(self, name, sizex, sizey, color, begin, reverse):
		alpha = 255 #set start alpha 0...255
		rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), 255)
		imga = Image.new("RGBA",(sizex, sizey-begin), rgba)
		rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), alpha)
		imgb = Image.new("RGBA",(sizex, sizey), rgba)
		gradient = Image.new('L', (1,alpha+1))
		for y in range(0,alpha+1):
			gradient.putpixel((0,y),y)
		w,h = imga.size
		gradient = gradient.resize((w,h))
		imga.putalpha(gradient)
		imgb.paste(imga,(0,0,w,h))
		if reverse:
			imgb = imgb.transpose(Image.ROTATE_180)
		imgb.save(name)

    def getFHDiconRefresh(self,restore=False):
        # call from SystemPlugins/SoftwareManager/plugin.py after software update and Screens/SkinSelector.py after changing skin - not rename to EHD !!!
        if config.plugins.MyMetrixLiteOther.EHDenabled.value == '0':
            self.EHDres = 'HD'
        elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '1':
            self.EHDres = 'FHD'
        elif config.plugins.MyMetrixLiteOther.EHDenabled.value == '2':
            self.EHDres = 'UHD'
        else:
            restore = True
        screenwidth = getDesktop(0).size().width()
        if screenwidth and screenwidth != 1280 or restore:
            if restore:
                self.EHDres = 'HD'
                print "[MetrixHD] restoring original %s icons after changing skin..." % self.EHDres
            else:
                print "[MetrixHD] refreshing %s icons after software update..." % self.EHDres
            self.iconFileCopy(self.EHDres)
            self.iconFolderCopy(self.EHDres)
            print "[MetrixHD] ...done."

    def iconFileCopy(self, target):

        #skin root
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/"
        self.FileCopy(target, spath, dpath)

        #skin icons
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/icons/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/icons/"
        self.FileCopy(target, spath, dpath)
        
        #skin buttons
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/buttons/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/buttons/"
        self.FileCopy(target, spath, dpath)
        
        #skin extensions
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/extensions/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/extensions/"
        self.FileCopy(target, spath, dpath)

        #plugin SoftwareManager
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/Plugins/SystemPlugins/SoftwareManager/" % self.EHDres
        dpath = "/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager/"
        self.FileCopy(target, spath, dpath)

        #plugin AutoBouquetsMaker
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/Plugins/SystemPlugins/AutoBouquetsMaker/images/" % self.EHDres
        dpath = "/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoBouquetsMaker/images/"
        self.FileCopy(target, spath, dpath)

        #plugin NetworkBrowser
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/Plugins/SystemPlugins/NetworkBrowser/icons/" % self.EHDres
        dpath = "/usr/lib/enigma2/python/Plugins/SystemPlugins/NetworkBrowser/icons/"
        self.FileCopy(target, spath, dpath)

        #plugin Infopanel
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/Plugins/Extensions/Infopanel/icons/" % self.EHDres
        dpath = "/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/icons/"
        self.FileCopy(target, spath, dpath)

    def FileCopy(self, target, spath, dpath):
        if target != "HD" and path.exists(spath) and path.exists(dpath):
            for file in listdir(spath):
                if not path.isfile(spath + file):
                    continue
                if path.exists(dpath + file):
                    if not path.exists(dpath + file + ".hd") and not path.exists(dpath + file + ".del"):
                        move(dpath + file,dpath + file + ".hd")
                    copy(spath + file,dpath + file)
                else:
                    if not path.exists(dpath + file + ".hd") and not path.exists(dpath + file + ".del"):
                        f = open(dpath + file + ".del", "w")
                        f.close()
                    copy(spath + file,dpath + file)

        if target == "HD" and path.exists(dpath):
            for file in listdir(dpath):
                if file.endswith('.png.hd'):
                    move(dpath + file,dpath + file[:-3])
                if file.endswith('.png.del'):
                    remove(dpath + file)
                    if path.exists(dpath + file[:-4]):
                        remove(dpath + file[:-4])

    def iconFolderCopy(self, target):

        #plugin MyMetrixLite
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/Plugins/Extensions/MyMetrixLite/images/" % self.EHDres
        dpath = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/"
        npath = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images_hd/"
        self.FolderCopy(target,spath,dpath,npath)

        #plugin EnhancedMovieCenter
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/emc/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/emc/"
        npath = ""
        if config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "2":
            if self.EHDres == "FHD":
                self.FolderCopy('HD',spath,dpath,npath,True)
            elif self.EHDres == "UHD" and path.exists("/usr/share/enigma2/MetrixHD/FHD/copy/emc/"):
                self.FolderCopy('FHD',"/usr/share/enigma2/MetrixHD/FHD/copy/emc/",dpath,npath,True)
        else:
            self.FolderCopy(target,spath,dpath,npath,True)

        #plugin Infobar Tunerstate
        spath = "/usr/share/enigma2/MetrixHD/%s/copy/ibts/" % self.EHDres
        dpath = "/usr/share/enigma2/MetrixHD/ibts/"
        npath = ""
        self.FolderCopy(target,spath,dpath,npath,True)

    def FolderCopy(self, target, spath, dpath, npath, del_dpath = False):
        if target != "HD" and path.exists(spath) and path.exists(dpath) and not del_dpath:
            if not path.exists(npath):
                move(dpath,npath)
            if path.exists(dpath):
                #save new files in backup folder(*_hd) before remove image folder
                subdirlist = []
                self.compFolder(dpath,npath,subdirlist)
                for subdir in subdirlist:
                    self.compFolder(subdir[0] + subdir[2] + "/", subdir[1] + subdir[2] + "/", subdirlist)
                #---
                rmtree(dpath)
            copytree(spath,dpath)
        elif target != "HD" and path.exists(spath) and del_dpath:
            if path.exists(dpath):
                rmtree(dpath)
            copytree(spath,dpath)

        if target == "HD" and path.exists(dpath) and path.exists(npath):
            #save new files in backup folder(*_hd) before remove image folder
            subdirlist = []
            self.compFolder(dpath,npath,subdirlist)
            for subdir in subdirlist:
                self.compFolder(subdir[0] + subdir[2] + "/", subdir[1] + subdir[2] + "/", subdirlist)
            #---
            rmtree(dpath)
            move(npath,dpath)
        elif target == "HD" and path.exists(dpath) and del_dpath:
            rmtree(dpath)

    def compFolder(self, dpath, npath, subdirlist):
        for file in listdir(dpath):
            if path.isfile(dpath + file):
                if not path.exists(npath + file):
                    if not path.exists(npath):
                        copytree(dpath,npath)
                    else:
                        copy(dpath + file, npath + file)
            else:
                subdirlist.append((dpath,npath,file))

    @staticmethod
    def getTunerCount():
        '''
        get tuner count
        :return:
        '''
        tunerCount = nimmanager.getSlotCount()

        tunerCount = max(1, tunerCount)
        tunerCount = min(6, tunerCount)

        return tunerCount

    @staticmethod
    def getChannelNameXML(widgetPosition, fontSizeType, showChannelNumber, showChannelName):
        fontSize = "80"

        if fontSizeType == "INFOBARCHANNELNAME-2":
            fontSize = "70"
        elif fontSizeType == "INFOBARCHANNELNAME-3":
            fontSize = "60"
        elif fontSizeType == "INFOBARCHANNELNAME-4":
            fontSize = "50"
        elif fontSizeType == "INFOBARCHANNELNAME-5":
            fontSize = "40"

        if showChannelNumber and showChannelName:
            channelRenderer = "ServiceNumberAndName"
        elif showChannelNumber:
            channelRenderer = "ServiceNumber"
        elif showChannelName:
            channelRenderer = "ServiceName"
        else:
            channelRenderer = None

        if channelRenderer is not None:
            return '''<widget font="global_large;''' + fontSize + '''" backgroundColor="text-background" foregroundColor="background-text" noWrap="1" position="''' \
                + widgetPosition \
                + '''" render="Label" size="1252,105" source="session.CurrentService" transparent="1" valign="bottom" zPosition="-30">
                <convert type="MetrixHDExtServiceInfo">''' + channelRenderer + '''</convert>
            </widget>'''

        return ""

    # def getTunerXMLItem(self, slotID, position1, position2, valueBitTest, valueRange, isTunerEnabled):
    #     xml = '''<eLabel position="''' + position1 + '''" text="''' + slotID + '''" zPosition="1" size="20,26" font="RegularLight; 24" halign="center" transparent="1" valign="center" backgroundColor="layer-a-background" foregroundColor="layer-a-accent2" />
    #     <widget position="''' + position1 + '''" text="''' + slotID + '''" source="session.TunerInfo" render="FixedLabel" zPosition="2" size="20,26" font="RegularLight; 24" halign="center" transparent="1" valign="center" backgroundColor="layer-a-background" foregroundColor="layer-a-accent1">
    #         <convert type="TunerInfo">TunerUseMask</convert>
    #         <convert type="ValueBitTest">''' + valueBitTest + '''</convert>
    #         <convert type="ConditionalShowHide" />
    #     </widget>
    #     <widget position="''' + position2 + '''" source="session.FrontendInfo" render="FixedLabel" zPosition="5" size="20,3" font="RegularLight; 24" halign="center" backgroundColor="layer-a-selection-background" transparent="0" valign="top">
    #         <convert type="FrontendInfo">NUMBER</convert>
    #         <convert type="ValueRange">''' + valueRange + '''</convert>
    #         <convert type="ConditionalShowHide" />
    #     </widget>'''
    #
    #     return xml

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def exit(self):
        self["menuList"].onSelectionChanged.remove(self.__selectionChanged)
        self.close()

    def __selectionChanged(self):
        self.ShowPicture()

    def optionEHD(self, sourceFile, targetFile):

		run_mod = False
		next_rename = False
		next_picon_zoom = False
		next_pixmap_ignore = False
		FACT = self.EHDfactor
		FFACT = FACT
		PFACT = FACT

		print "starting   " + sourceFile + "   --->   " + targetFile

		fontsize = self.font_size
		if fontsize > 2:
			FFACT = 1.25

		r_par = self.round_par
		f_offset = self.font_offset

		f = open(sourceFile, "r")
		f1 = open(targetFile, "w")

		i = 0
		i_save = i
		for line in f.readlines(): 
			i += 1
			try: 
#start additional files
				if self.EHD_addfiles:
#file 'antilogo.xml'
					if sourceFile == "/etc/enigma2/antilogo.xml":
#height="88"
						if 'height="' in line and not 'alias name="' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('height="')):
								n1 = line.find('height=', n2)
								n2 = line.find('"', n1)
								n3 = line.find('"', n2+1)
								y = line[(n2+1):n3]
								ynew = str(int(round(float(int(y)*FACT),r_par)))
								strnew = line[n1:n2+1] + ynew
								line = line[:n1] + strnew + line[n3:]
#y="586"
						if 'y="' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('y="')):
								n1 = line.find('y=', n2)
								n2 = line.find('"', n1)
								n3 = line.find('"', n2+1)
								y = line[(n2+1):n3]
								ynew = str(int(round(float(int(y)*FACT),r_par)))
								strnew = line[n1:n2+1] + ynew
								line = line[:n1] + strnew + line[n3:]
#width="95"
						if 'width="' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('width="')):
								n1 = line.find('width=', n2)
								n2 = line.find('"', n1)
								n3 = line.find('"', n2+1)
								x = line[(n2+1):n3]
								ynew = str(int(round(float(int(x)*FACT),r_par)))
								strnew = line[n1:n2+1] + ynew
								line = line[:n1] + strnew + line[n3:]
#x="1088" 
						if 'x="' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('x="')):
								n1 = line.find('x=', n2)
								n2 = line.find('"', n1)
								n3 = line.find('"', n2+1)
								x = line[(n2+1):n3]
								ynew = str(int(round(float(int(x)*FACT),r_par)))
								strnew = line[n1:n2+1] + ynew
								line = line[:n1] + strnew + line[n3:]
#additional files end
#start skin files
#rename flag
				if '<!-- cf#_#rename -->' in line:
					next_rename = True
					run_mod = False
				else:
					if next_rename:
						if '#_' + self.EHDres + 'screen' in line:
							line = line.replace('#_%sscreen' % self.EHDres, "") 
						else:
							if 'name="' in line and not '#_' in line and not 'HDscreen' in line:
								n1 = line.find('name=', 0)
								n2 = line.find('"', n1)
								n3 = line.find('"', n2+1)
								line = line[:(n3)] + '#_HDscreen' + line[(n3):]
						next_rename = False
#control flags
					if '<!-- cf#_#begin -->' in line:
						run_mod = True
					if '<!-- cf#_#stop -->' in line:
						run_mod = False
#picon zoom, pixmap ignore flags
					if '<!-- cf#_#picon -->' in line:
						#only for next line!
						i_save = i+1
						next_picon_zoom = True
						PFACT = self.picon_zoom
					elif '<!-- cf#_#pixnore -->' in line:
						#only for next line!
						i_save = i+1
						next_pixmap_ignore = True
					else:
						if i > i_save:
							i_save = i+10000 
							next_picon_zoom = False
							next_pixmap_ignore = False
							PFACT = FACT
				if run_mod:
#<resolution xres="1280" yres="720"
					if '<resolution ' in line:
						n1 = line.find('xres', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', (n2+1))
						line = line[:(n2+1)] + "1920" + line[(n3):]

						n1 = line.find('yres', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', (n2+1))
						line = line[:(n2+1)] + "1080" + line[(n3):]
#<parameter name="AutotimerEnabledIcon" value="6,2,24,25"
					if '<parameter name="' in line and 'value="' in line:
						n1 = line.find('value="', 0)
						n2 = line.find('"', n1) 
						n12 = line.find('"', n2+1) 
						parcount = len(line[n2:n12+1].split(','))
						strnew = ""
						if parcount == 1:
							p1 = int(round(float(int(line[(n2+1):n12])*FACT),r_par))
							strnew = 'value="%d"' %(p1)
						elif parcount == 2:
							n3 = line.find(',', n2) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d"' %(p1,p2)
						elif parcount == 3:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d"' %(p1,p2,p3)
						elif parcount == 4:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							n5 = line.find(',', n4+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n5])*FACT),r_par))
							p4 = int(round(float(int(line[(n5+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d,%d"' %(p1,p2,p3,p4)
						elif parcount == 5:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							n5 = line.find(',', n4+1) 
							n6 = line.find(',', n5+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n5])*FACT),r_par))
							p4 = int(round(float(int(line[(n5+1):n6])*FACT),r_par))
							p5 = int(round(float(int(line[(n6+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d,%d,%d"' %(p1,p2,p3,p4,p5)
						elif parcount == 6:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							n5 = line.find(',', n4+1) 
							n6 = line.find(',', n5+1) 
							n7 = line.find(',', n6+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n5])*FACT),r_par))
							p4 = int(round(float(int(line[(n5+1):n6])*FACT),r_par))
							p5 = int(round(float(int(line[(n6+1):n7])*FACT),r_par))
							p6 = int(round(float(int(line[(n7+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d,%d,%d,%d"' %(p1,p2,p3,p4,p5,p6)
						elif parcount == 7:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							n5 = line.find(',', n4+1) 
							n6 = line.find(',', n5+1) 
							n7 = line.find(',', n6+1) 
							n8 = line.find(',', n7+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n5])*FACT),r_par))
							p4 = int(round(float(int(line[(n5+1):n6])*FACT),r_par))
							p5 = int(round(float(int(line[(n6+1):n7])*FACT),r_par))
							p6 = int(round(float(int(line[(n7+1):n8])*FACT),r_par))
							p7 = int(round(float(int(line[(n8+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d,%d,%d,%d,%d"' %(p1,p2,p3,p4,p5,p6,p7)
						elif parcount == 8:
							n3 = line.find(',', n2) 
							n4 = line.find(',', n3+1) 
							n5 = line.find(',', n4+1) 
							n6 = line.find(',', n5+1) 
							n7 = line.find(',', n6+1) 
							n8 = line.find(',', n7+1) 
							n9 = line.find(',', n8+1) 
							p1 = int(round(float(int(line[(n2+1):n3])*FACT),r_par))
							p2 = int(round(float(int(line[(n3+1):n4])*FACT),r_par))
							p3 = int(round(float(int(line[(n4+1):n5])*FACT),r_par))
							p4 = int(round(float(int(line[(n5+1):n6])*FACT),r_par))
							p5 = int(round(float(int(line[(n6+1):n7])*FACT),r_par))
							p6 = int(round(float(int(line[(n7+1):n8])*FACT),r_par))
							p7 = int(round(float(int(line[(n8+1):n9])*FACT),r_par))
							p8 = int(round(float(int(line[(n9+1):n12])*FACT),r_par))
							strnew = 'value="%d,%d,%d,%d,%d,%d,%d,%d"' %(p1,p2,p3,p4,p5,p6,p7,p8)

						if strnew:
							line = line[:n1] + strnew + line[(n12+1):]
#rowSplit="25"
					if 'rowSplit' in line:
						s = 0
						n3 = 0
						for s in range(0,line.count('rowSplit')):
							n1 = line.find('rowSplit', n3)
							n2 = line.find('="', n1)
							n3 = line.find('"', n2+2) 
							y = line[(n2+2):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+2] + ynew
							line = line[:n1] + strnew + line[n3:]
#rowHeight="25"
					if 'rowHeight="' in line:
						n1 = line.find('rowHeight="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#satPosLeft="160" 
					if 'satPosLeft="' in line:
						n1 = line.find('satPosLeft="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]

#iconMargin="5"
					if 'iconMargin="' in line:
						n1 = line.find('iconMargin="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#size="200,100"
					xpos = 0
					ypos = 0
					if 'size="' in line and not 'alias name="' in line:
						n1 = line.find('size="', 0)
						n2 = line.find('"', n1) 
						n3 = line.find(',', n2) 
						n4 = line.find('"', n3) 
						x = line[(n2+1):n3]
						y = line[(n3+1):n4]
						if "c+" in x:
							x1 = x.replace("c+", "")
							xpos = int(round(float((int(x1)*FACT - int(x1)*PFACT)/2),r_par))
							x1new = str(int(round(float(int(x1)*PFACT),r_par)))
							xnew = "c+" + x1new
						elif "c-" in x:
							x1 = x.replace("c-", "")
							xpos = int(round(float((int(x1)*FACT - int(x1)*PFACT)/2),r_par))
							x1new = str(int(round(float(int(x1)*PFACT),r_par)))
							xnew = "c-" + x1new
						elif "e-" in x:
							x1 = x.replace("e-", "")
							xpos = int(round(float((int(x1)*FACT - int(x1)*PFACT)/2),r_par))
							x1new = str(int(round(float(int(x1)*PFACT),r_par)))
							xnew = "e-" + x1new
						else:
							xpos = int(round(float((int(x)*FACT - int(x)*PFACT)/2),r_par))
							xnew = str(int(round(float(int(x)*PFACT),r_par)))

						if "c+" in y:
							y1 = y.replace("c+", "")
							ypos = int(round(float((int(y1)*FACT - int(y1)*PFACT)/2),r_par))
							y1new = str(int(round(float(int(y1)*PFACT),r_par)))
							ynew = "c+" + y1new
						elif "c-" in y:
							y1 = y.replace("c-", "")
							ypos = int(round(float((int(y1)*FACT - int(y1)*PFACT)/2),r_par))
							y1new = str(int(round(float(int(y1)*PFACT),r_par)))
							ynew = "c-" + y1new
						elif "e-" in y:
							y1 = y.replace("e-", "")
							ypos = int(round(float((int(y1)*FACT - int(y1)*PFACT)/2),r_par))
							y1new = str(int(round(float(int(y1)*PFACT),r_par)))
							ynew = "e-" + y1new
						else:
							ypos = int(round(float((int(y)*FACT - int(y)*PFACT)/2),r_par))
							ynew = str(int(round(float(int(y)*PFACT),r_par)))

						#if '<eLabel name="underline"' in line: #no new height for screen title separating line
						#	ynew = str(y)

						strnew = 'size="' + xnew + ',' + ynew + '"'
						line = line[:n1] + strnew + line[(n4+1):]
#position="423,460"
					if not next_picon_zoom:
						xpos = 0
						ypos = 0

					if 'position="' in line:
						n1 = line.find('position="', 0)
						n2 = line.find('"', n1) 
						n3 = line.find(',', n2) 
						n4 = line.find('"', n3) 
						x = line[(n2+1):n3]
						y = line[(n3+1):n4]
						if "c+" in x:
							x1 = x.replace("c+", "")
							x1new = str(int(round(float(int(x1)*FACT+xpos),r_par)))
							xnew = "c+" + x1new
						elif "c-" in x:
							x1 = x.replace("c-", "")
							x1new = str(int(round(float(int(x1)*FACT+xpos),r_par)))
							xnew = "c-" + x1new
						elif "e-" in x:
							x1 = x.replace("e-", "")
							x1new = str(int(round(float(int(x1)*FACT+xpos),r_par)))
							xnew = "e-" + x1new
						elif 'ente' in x:
							xnew = 'center'
						else:
							xnew = str(int(round(float(int(x)*FACT+xpos),r_par)))

						if "c+" in y:
							y1 = y.replace("c+", "")
							y1new = str(int(round(float(int(y1)*FACT+ypos),r_par)))
							ynew = "c+" + y1new
						elif "c-" in y:
							y1 = y.replace("c-", "")
							y1new = str(int(round(float(int(y1)*FACT+ypos),r_par)))
							ynew = "c-" + y1new
						elif "e-" in y:
							y1 = y.replace("e-", "")
							y1new = str(int(round(float(int(y1)*FACT+ypos),r_par)))
							ynew = "e-" + y1new
						elif 'ente' in y:
							ynew = 'center'
						else:
							ynew = str(int(round(float(int(y)*FACT+ypos),r_par)))

						strnew = 'position="' + xnew + ',' + ynew + '"'
						line = line[:n1] + strnew + line[(n4+1):]
#font="Regular;20"
					if 'font="' in line and not 'alias name="' in line and fontsize >= 2:
						n1 = line.find('font="', 0)
						n2 = line.find(';', n1) 
						n3 = line.find('"', n2) 
						y = line[(n2+1):n3]
						ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
						strnew = line[n1:(n2+1)] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#Font="Regular;20"
					if 'Font="' in line and not ' Cool' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('Font="')):
							n1 = line.find('Font="', n3)
							n2 = line.find(';', n1)
							n3 = line.find('"', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + ynew
							line = line[:n1] + strnew + line[n3:]
#ServiceFontGraphical="epg_text;20" EntryFontGraphical="epg_text;20"
					if 'FontGraphical="' in line and not ' Cool' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('FontGraphical="')):
							n1 = line.find('FontGraphical="', n3)
							n2 = line.find(';', n1)
							n3 = line.find('"', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + ynew
							line = line[:n1] + strnew + line[n3:]
#ServiceFontInfobar="epg_text;20" EntryFontInfobar="epg_text;20"
					if 'FontInfobar=' in line and not ' Cool' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('FontInfobar="')):
							n1 = line.find('FontInfobar="', n3)
							n2 = line.find(';', n1)
							n3 = line.find('"', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + ynew
							line = line[:n1] + strnew + line[n3:]
#EventFontSingle="epg_event;22"
					if 'FontSingle=' in line and not ' Cool' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('FontSingle="')):
							n1 = line.find('FontSingle="', n3)
							n2 = line.find(';', n1)
							n3 = line.find('"', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + ynew
							line = line[:n1] + strnew + line[n3:]
#EventFontMulti="epg_event;22"
					if 'FontMulti=' in line and not ' Cool' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('FontMulti="')):
							n1 = line.find('FontMulti="', n3)
							n2 = line.find(';', n1)
							n3 = line.find('"', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + ynew
							line = line[:n1] + strnew + line[n3:]
#<alias name="Body" font="screen_text" size="20" height="25" />
					if 'font="' in line and 'alias name="' in line and 'size="' in line and fontsize >= 2:
						n1 = line.find('size="', 0)
						n2 = line.find('"', n1) 
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]
						ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
						strnew = line[n1:(n2+1)] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#<alias name="Body" font="screen_text" size="20" height="25" />
					if 'font="' in line and 'alias name="' in line and 'height="' in line:
						n1 = line.find('height="', 0)
						n2 = line.find('"', n1) 
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]
						ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
						strnew = line[n1:(n2+1)] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#"fonts": [gFont("Regular",18),gFont("Regular",14),gFont("Regular",24),gFont("Regular",20)]
					if '"fonts":' in line and 'gFont' in line and fontsize >= 2:
						s = 0
						n3 = 0
						for s in range(0,line.count('gFont(')):
							n1 = line.find('gFont(', n3)
							n2 = line.find(',', n1)
							n3 = line.find(')', n2) 
							y = line[(n2+1):n3]
							ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
							strnew = line[n1:n2+1] + " " + ynew
							line = line[:n1] + strnew + line[n3:]
#scale="100"
					if 'scale="' in line and not 'scale="-1"' in line and fontsize != 2:
						n1 = line.find('scale="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]
						ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#(pos = (40, 5)
					if '(pos' in line and ')' in line:
						n1 = line.find('(pos', 0)
						n2 = line.find('(', n1+1) 
						n3 = line.find(',', n2) 
						n4 = line.find(')', n3) 
						x = line[(n2+1):n3]
						y = line[(n3+1):n4]
						if "c+" in x:
							x1 = x.replace("c+", "")
							x1new = str(int(round(float(int(x1)*FACT),r_par)))
							xnew = "c+" + x1new
						elif "c-" in x:
							x1 = x.replace("c-", "")
							x1new = str(int(round(float(int(x1)*FACT),r_par)))
							xnew = "c-" + x1new
						elif "e-" in x:
							x1 = x.replace("e-", "")
							x1new = str(int(round(float(int(x1)*FACT),r_par)))
							xnew = "e-" + x1new      
						elif 'ente' in x:
							xnew = 'center'
						else:
							xnew = str(int(round(float(int(x)*FACT),r_par)))

						if "c+" in y:
							y1 = y.replace("c+", "")
							y1new = str(int(round(float(int(y1)*FACT),r_par)))
							ynew = "c+" + y1new
						elif "c-" in y:
							y1 = y.replace("c-", "")
							y1new = str(int(round(float(int(y1)*FACT),r_par)))
							ynew = "c-" + y1new
						elif "e-" in y:
							y1 = y.replace("e-", "")
							y1new = str(int(round(float(int(y1)*FACT),r_par)))
							ynew = "e-" + y1new
						elif 'ente' in y:
							ynew = 'center'
						else:
							ynew = str(int(round(float(int(y)*FACT),r_par)))

						strnew = '(pos = (' + xnew + ', ' + ynew + ')'
						line = line[:n1] + strnew + line[(n4+1):]
#size = (500, 45)
						if 'size' in line and '(' in line and ')' in line:
							n1 = line.find('size', 0)
							n2 = line.find('(', n1) 
							n3 = line.find(',', n2) 
							n4 = line.find(')', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							if "c+" in x:
								x1 = x.replace("c+", "")
								x1new = str(int(round(float(int(x1)*FACT),r_par)))
								xnew = "c+" + x1new
							elif "c-" in x:
								x1 = x.replace("c-", "")
								x1new = str(int(round(float(int(x1)*FACT),r_par)))
								xnew = "c-" + x1new
							elif "e-" in x:
								x1 = x.replace("e-", "")
								x1new = str(int(round(float(int(x1)*FACT),r_par)))
								xnew = "e-" + x1new
							elif 'ente' in x:
								xnew = 'center'
							else:
								xnew = str(int(round(float(int(x)*FACT),r_par)))

							if "c+" in y:
								y1 = y.replace("c+", "")
								y1new = str(int(round(float(int(y1)*FACT),r_par)))
								ynew = "c+" + y1new
							elif "c-" in y:
								y1 = y.replace("c-", "")
								y1new = str(int(round(float(int(y1)*FACT),r_par)))
								ynew = "c-" + y1new
							elif "e-" in y:
								y1 = y.replace("e-", "")
								y1new = str(int(round(float(int(y1)*FACT),r_par)))
								ynew = "e-" + y1new
							elif 'ente' in y:
								ynew = 'center'
							else:
								ynew = str(int(round(float(int(y)*FACT),r_par)))

							strnew = 'size = (' + xnew + ', ' + ynew + ')'
							line = line[:n1] + strnew + line[(n4+1):]
#offset="5,0"
					if ' offset="' in line:
						n1 = line.find(' offset', 0)
						n2 = line.find('"', n1) 
						n3 = line.find(',', n2) 
						n4 = line.find('"', n3) 
						x = line[(n2+1):n3]
						y = line[(n3+1):n4]
						xnew = str(int(round(float(int(x)*FACT),r_par)))
						ynew = str(int(round(float(int(y)*FACT),r_par)))

						strnew = ' offset="' + xnew + ',' + ynew + '"'
						line = line[:n1] + strnew + line[(n4+1):]
#fieldMargins="10"
					if 'fieldMargins="' in line:
						n1 = line.find('fieldMargins="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#itemsDistances="10"
					if 'itemsDistances="' in line:
						n1 = line.find('itemsDistances="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#progressbarHeight="10"
					if 'progressbarHeight="' in line:
						n1 = line.find('progressbarHeight="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#progressBarWidth="50" 
					if 'progressBarWidth="' in line:
						n1 = line.find('progressBarWidth="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#progressbarBorderWidth="1" 
					if 'progressbarBorderWidth="' in line:
						n1 = line.find('progressbarBorderWidth="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#itemHeight="25"
					if 'itemHeight="' in line:
						n1 = line.find('itemHeight="', 0)
						n2 = line.find('"', n1)
						n3 = line.find('"', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew + '"'
						line = line[:n1] + strnew + line[(n3+1):]
#"itemHeight": 45
					if '"itemHeight":' in line:
						n1 = line.find('"itemHeight":', 0)
						n2 = line.find(':', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + ynew
						line = line[:n1] + strnew + line[n3:]
#": (90,[
					if '": (' in line and '[' in line:
						n1 = line.find('":', 0)
						n2 = line.find('(', n1)
						n3 = line.find(',', n2+1) 
						y = line[(n2+1):n3]

						ynew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + ynew
						line = line[:n1] + strnew + line[n3:]

#messagebox <applet type="onLayoutFinish">
#offset_listposx = 10
#offset_listposy = 10
#offset_listwidth = 10
#offset_listheight = 30
#offset_textwidth = 20
#offset_textheight = 90
#min_width = 400
#min_height = 50
#offset = 21
					if 'offset_listposx =' in line:
						n1 = line.find('offset_listposx', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						x = line[(n2+1):n3]
						xnew = str(int(round(float(int(x)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset_listposy =' in line:
						n1 = line.find('offset_listposy', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]
						xnew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset_listwidth =' in line:
						n1 = line.find('offset_listwidth', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						x = line[(n2+1):n3]
						xnew = str(int(round(float(int(x)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset_listheight =' in line:
						n1 = line.find('offset_listheight', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]
						xnew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset_textwidth =' in line:
						n1 = line.find('offset_textwidth', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						x = line[(n2+1):n3]
						xnew = str(int(round(float(int(x)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset_textheight =' in line:
						n1 = line.find('offset_textheight', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]
						xnew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'min_width =' in line:
						n1 = line.find('min_width', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						x = line[(n2+1):n3]
						xnew = str(int(round(float(int(x)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'min_height =' in line:
						n1 = line.find('min_height', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]
						xnew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
					elif 'offset =' in line:
						n1 = line.find('offset', 0)
						n2 = line.find('=', n1)
						n3 = line.find(',', n2) 
						if n3 == -1:
							n3 = line.find(')', n2)
							if n3 == -1:
								n3 = line.find('}', n2)
						y = line[(n2+1):n3]
						xnew = str(int(round(float(int(y)*FACT),r_par)))
						strnew = line[n1:n2+1] + " " + xnew
						line = line[:n1] + strnew + line[n3:]
#change pixmap path
					if not next_pixmap_ignore and ('pixmap="' in line or "pixmaps=" in line or '<pixmap pos="bp' in line or 'render="EMCPositionGauge"' in line):
						if 'MetrixHD/' in line and '.png' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('MetrixHD/')):
								n1 = line.find('MetrixHD/', n2)
								n2 = line.find('.png', n1)
								file = "/usr/share/enigma2/MetrixHD/" + self.EHDres + line[(n1+8):(n2+4)]  
								if path.exists(file):
									strnew = "MetrixHD/" + self.EHDres + line[(n1+8):n2]
									line = line[:n1] + strnew + line[n2:]
								else:
									print "pixmap missing - line", i , file
									self.pixmap_error = True
						if 'skin_default/' in line and not '/skin_default/' in line and '.png"' in line:
							s = 0
							n2 = 0
							for s in range(0,line.count('skin_default/')):
								n1 = line.find('skin_default/', n2)
								n2 = line.find('.png', n1)
								file = "/usr/share/enigma2/MetrixHD/" + self.EHDres + "/skin_default" + line[(n1+12):(n2+4)]
								if path.exists(file):
									strnew = "MetrixHD/" + self.EHDres + "/skin_default" + line[(n1+12):n2]
									line = line[:n1] + strnew + line[n2:]
								else:
									print "pixmap missing - line", i, file
									self.pixmap_error = True
#emc special start
					if 'widget name="list"' in line and ' Cool' in line and not ' CoolEvent' in line or 'render="EMCPositionGauge"' in line:
#CoolFont="epg_text;20" CoolSelectFont="epg_text;20" CoolDateFont="epg_text;30" 
						if fontsize >= 2:
							if 'CoolFont="' in line:
								n1 = line.find('CoolFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
							if 'CoolSelectFont="' in line:
								n1 = line.find('CoolSelectFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
							if 'CoolDateFont=' in line:
								n1 = line.find('CoolDateFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
#CoolSelNumTxtWidth="26" 
						if 'CoolSelNumTxtWidth="' in line:
							n1 = line.find('CoolSelNumTxtWidth=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDateHPos="1" 
						if 'CoolDateHPos="' in line:
							n1 = line.find('CoolDateHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolProgressHPos="1" 
						if 'CoolProgressHPos="' in line:
							n1 = line.find('CoolProgressHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMovieHPos="1" 
						if 'CoolMovieHPos="' in line:
							n1 = line.find('CoolMovieHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDirInfoWidth="110" 
						if 'CoolDirInfoWidth="' in line:
							n1 = line.find('CoolDirInfoWidth=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolCSWidth="110" 
						if 'CoolCSWidth="' in line:
							n1 = line.find('CoolCSWidth=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolProgressPos="35" 
						if 'CoolProgressPos="' in line:
							n1 = line.find('CoolProgressPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolIconPos="35"
						if 'CoolIconPos="' in line:
							n1 = line.find('CoolIconPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolIconHPos="35"
						if 'CoolIconHPos="' in line:
							n1 = line.find('CoolIconHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarPos="35"
						if 'CoolBarPos="' in line:
							n1 = line.find('CoolBarPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarHPos="10"
						if 'CoolBarHPos="' in line:
							n1 = line.find('CoolBarHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMoviePos="110"
						if 'CoolMoviePos="' in line:
							n1 = line.find('CoolMoviePos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDatePos="590"
						if 'CoolDatePos="' in line:
							n1 = line.find('CoolDatePos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMovieSize="490"
						if 'CoolMovieSize="' in line:
							n1 = line.find('CoolMovieSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolFolderSize="490"
						if 'CoolFolderSize="' in line:
							n1 = line.find('CoolFolderSize="', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDateWidth="110"
						if 'CoolDateWidth="' in line:
							n1 = line.find('CoolDateWidth=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolPiconPos="100" 
						if 'CoolPiconPos="' in line: 
							n1 = line.find('CoolPiconPos=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolPiconHPos="2" 
						if 'CoolPiconHPos="' in line: 
							n1 = line.find('CoolPiconHPos=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolPiconWidth="60" 
						if 'CoolPiconWidth="' in line: 
							n1 = line.find('CoolPiconWidth=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolPiconHeight="26" 
						if 'CoolPiconHeight="' in line: 
							n1 = line.find('CoolPiconHeight=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolMoviePiconPos="160" 
						if 'CoolMoviePiconPos="' in line: 
							n1 = line.find('CoolMoviePiconPos=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolMoviePiconSize="425" 
						if 'CoolMoviePiconSize="' in line: 
							n1 = line.find('CoolMoviePiconSize=', 0) 
							n2 = line.find('"', n1) 
							n3 = line.find('"', n2+1) 
							y = line[(n2+1):n3] 
							ynew = str(int(round(float(int(y)*FACT),r_par))) 
							strnew = line[n1:n2+1] + ynew + '"' 
							line = line[:n1] + strnew + line[(n3+1):] 
#CoolIconSize="24,24"
						if 'CoolIconSize="' in line:
							n1 = line.find('CoolIconSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find(',', n2+1)
							n4 = line.find('"', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							xnew = str(int(round(float(int(x)*FACT),r_par)))
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = 'CoolIconSize="' + xnew + ',' + ynew + '"'
							line = line[:n1] + strnew + line[(n4+1):]
#CoolBarSize="65,10"
						if 'CoolBarSize="' in line:
							n1 = line.find('CoolBarSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find(',', n2+1)
							n4 = line.find('"', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							xnew = str(int(round(float(int(x)*FACT),r_par)))
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = 'CoolBarSize="' + xnew + ',' + ynew + '"'
							line = line[:n1] + strnew + line[(n4+1):]
#CoolBarSizeSa="65,10"
						if 'CoolBarSizeSa="' in line:
							n1 = line.find('CoolBarSizeSa=', 0)
							n2 = line.find('"', n1)
							n3 = line.find(',', n2+1)
							n4 = line.find('"', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							xnew = str(int(round(float(int(x)*FACT),r_par)))
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = 'CoolBarSizeSa="' + xnew + ',' + ynew + '"'
							line = line[:n1] + strnew + line[(n4+1):]
#/CoolPointerRec.png:980,0"
						if '/CoolPointerRec.png:' in line:
							n1 = line.find('/CoolPointerRec.png', 0)
							n2 = line.find(':', n1)
							n3 = line.find(',', n2+1)
							n4 = line.find('"', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							xnew = str(int(round(float(int(x)*FACT),r_par)))
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = '/CoolPointerRec.png:' + xnew + ',' + ynew + '"'
							line = line[:n1] + strnew + line[(n4+1):]
#/CoolPointerRec2.png:1080,0"
						if '/CoolPointerRec2.png:' in line:
							n1 = line.find('/CoolPointerRec2.png', 0)
							n2 = line.find(':', n1)
							n3 = line.find(',', n2+1)
							n4 = line.find('"', n3) 
							x = line[(n2+1):n3]
							y = line[(n3+1):n4]
							xnew = str(int(round(float(int(x)*FACT),r_par)))
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = '/CoolPointerRec2.png:' + xnew + ',' + ynew + '"'
							line = line[:n1] + strnew + line[(n4+1):]

#emc special end
#cool tv guide special start
					if ('widget name="list"' in line or 'widget name="CoolEvent"' in line) and ' CoolEvent' in line:
#CoolFont="Regular;19" CoolServiceFont="Regular;19" CoolEventFont="Regular;19" 
						if fontsize >= 2:
							if 'CoolFont="' in line:
								n1 = line.find('CoolFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
							if 'CoolServiceFont="' in line:
								n1 = line.find('CoolServiceFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
							if 'CoolEventFont="' in line:
								n1 = line.find('CoolEventFont=', 0)
								n2 = line.find(';', n1)
								n3 = line.find('"', n2)
								y = line[(n2+1):n3]
								ynew = str(int(f_offset + round(float(int(y)*FFACT),r_par)))
								strnew = line[n1:n2+1] + ynew + '"'
								line = line[:n1] + strnew + line[(n3+1):]
#CoolServiceSize="220"
						if 'CoolServiceSize="' in line:
							n1 = line.find('CoolServiceSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolEventSize="720"
						if 'CoolEventSize="' in line:
							n1 = line.find('CoolEventSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolServicePos="4"
						if 'CoolServicePos="' in line:
							n1 = line.find('CoolServicePos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolServiceHPos="1"
						if 'CoolServiceHPos="' in line:
							n1 = line.find('CoolServiceHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolEventPos="355"
						if 'CoolEventPos="' in line:
							n1 = line.find('CoolEventPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolEventHPos="1"
						if 'CoolEventHPos="' in line:
							n1 = line.find('CoolEventHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarPos="240"
						if 'CoolBarPos="' in line:
							n1 = line.find('CoolBarPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarHPos="10"
						if 'CoolBarHPos="' in line:
							n1 = line.find('CoolBarHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarSize="100"
						if 'CoolBarSize="' in line:
							n1 = line.find('CoolBarSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolBarHigh="10"
						if 'CoolBarHigh="' in line:
							n1 = line.find('CoolBarHigh=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolTimePos="225"
						if 'CoolTimePos="' in line:
							n1 = line.find('CoolTimePos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolTimeHPos="2"
						if 'CoolTimeHPos="' in line:
							n1 = line.find('CoolTimeHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolTimeSize="120"
						if 'CoolTimeSize="' in line:
							n1 = line.find('CoolTimeSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDurationPos="1055"
						if 'CoolDurationPos="' in line:
							n1 = line.find('CoolDurationPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDurationSize="100"
						if 'CoolDurationSize="' in line:
							n1 = line.find('CoolDurationSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolPico="35"
						if 'CoolPico="' in line:
							n1 = line.find('CoolPico=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDaySize="100"
						if 'CoolDaySize="' in line:
							n1 = line.find('CoolDaySize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDayPos="0"
						if 'CoolDayPos="' in line:
							n1 = line.find('CoolDayPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDayHPos="2"
						if 'CoolDayHPos="' in line:
							n1 = line.find('CoolDayHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDayHPos="2"
						if 'CoolDayHPos="' in line:
							n1 = line.find('CoolDayHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDatePos="0"
						if 'CoolDatePos="' in line:
							n1 = line.find('CoolDatePos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDateHPos="0"
						if 'CoolDateHPos="' in line:
							n1 = line.find('CoolDateHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolDateSize="0"
						if 'CoolDateSize="' in line:
							n1 = line.find('CoolDateSize=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMarkerHPos="200"
						if 'CoolMarkerHPos="' in line:
							n1 = line.find('CoolMarkerHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMarkerPicPos="2"
						if 'CoolMarkerPicPos="' in line:
							n1 = line.find('CoolMarkerPicPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolMarkerPicHPos="2"
						if 'CoolMarkerPicHPos="' in line:
							n1 = line.find('CoolMarkerPicHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolPicoPos="2"
						if 'CoolPicoPos="' in line:
							n1 = line.find('CoolPicoPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#CoolPicoHPos="2"
						if 'CoolPicoHPos="' in line:
							n1 = line.find('CoolPicoHPos=', 0)
							n2 = line.find('"', n1)
							n3 = line.find('"', n2+1)
							y = line[(n2+1):n3]
							ynew = str(int(round(float(int(y)*FACT),r_par)))
							strnew = line[n1:n2+1] + ynew + '"'
							line = line[:n1] + strnew + line[(n3+1):]
#cool tv guide special end
			except:
				self.skinline_error = True
				print "error in line: ", i, line
				print "--------"
			f1.write(line)
			if self.skinline_error:
				break

		f.close()
		f1.close()
		print "complete"
		print "--------"

    def showHelperText(self):
        cur = self["menuList"].getCurrent()
        if cur and len(cur[0]) > 2 and cur[0][2] and cur[0][2] != _("helptext"):
            self["helpertext"].setText(cur[0][2])
        else:
            self["helpertext"].setText(" ")
