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

from . import _, initColorsConfig, initWeatherConfig, initOtherConfig, getTunerPositionList, appendSkinFile, \
    SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP, COLOR_IMAGE_PATH, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_SOURCE, \
    SKIN_SECOND_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET_TMP, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP, \
    SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP, \
    SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP, \
	SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP

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
from shutil import move
from enigma import ePicLoad, eListboxPythonMultiContent, gFont
from ColorsSettingsView import ColorsSettingsView
from WeatherSettingsView import WeatherSettingsView
from OtherSettingsView import OtherSettingsView

#############################################################

class MainMenuList(MenuList):
    def __init__(self, list, font0 = 24, font1 = 16, itemHeight = 50, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont("Regular", font0))
        self.l.setFont(1, gFont("Regular", font1))
        self.l.setItemHeight(itemHeight)

#############################################################

def MenuEntryItem(itemDescription, key):
    res = [(itemDescription, key)]
    res.append(MultiContentEntryText(pos=(10, 5), size=(440, 40), font=0, text=itemDescription))
    return res

#############################################################

class MainSettingsView(Screen):
    skin = """
  <screen name="MyMetrixLiteMainSettingsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
    <widget name="menuList" position="61,124" size="590,490" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
    <widget source="applyBtn" position="257,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
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
        self["titleText"].setText(_("MyMetrixLite"))

        self["cancelBtn"] = StaticText("")
        self["cancelBtn"].setText(_("Cancel"))

        self["applyBtn"] = StaticText("")
        self["applyBtn"].setText(_("Apply changes"))

        initColorsConfig()
        initWeatherConfig()
        initOtherConfig()

        self.applyChangesFirst = args
        if self.applyChangesFirst:
            self.applyChanges()

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
                "green": self.applyChanges,
                "cancel": self.exit
            }, -1)

        list = []
        list.append(MenuEntryItem(_("Color settings"), "COLOR"))
        list.append(MenuEntryItem(_("Weather settings"), "WEATHER"))
        list.append(MenuEntryItem(_("Other settings"), "OTHER"))

        self["menuList"] = MainMenuList([], font0=24, font1=15, itemHeight=50)
        self["menuList"].l.setList(list)

        if not self.__selectionChanged in self["menuList"].onSelectionChanged:
            self["menuList"].onSelectionChanged.append(self.__selectionChanged)

        self.onChangedEntry = []

        self.onLayoutFinish.append(self.UpdatePicture)

    def __del__(self):
        self["menuList"].onSelectionChanged.remove(self.__selectionChanged)

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        if self["helperimage"] is None or self["helperimage"].instance is None:
            return

        cur = self["menuList"].getCurrent()

        imageUrl = COLOR_IMAGE_PATH % "FFFFFF"

        if cur:
            selectedKey = cur[0][1]

            if selectedKey == "COLOR":
                imageUrl = COLOR_IMAGE_PATH % "MyMetrixLiteColor"
            elif selectedKey == "WEATHER":
                imageUrl = COLOR_IMAGE_PATH % "MyMetrixLiteWeather"
            elif selectedKey == "OTHER":
                imageUrl = COLOR_IMAGE_PATH % "MyMetrixLiteOther"

        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(imageUrl)

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

    def reboot(self, message = None):
        if message is None:
            message = _("Do you really want to reboot now?")

        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, message, MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Restart GUI"))

    def applyChanges(self):
        print"MyMetrixLite apply Changes"
        try:
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

            if config.plugins.MyMetrixLiteOther.setTunerAuto.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', '<panel name="INFOBARTUNERINFO-%d" />' % config.plugins.MyMetrixLiteOther.setTunerManual.getValue()])
            else:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-2" />', '<panel name="INFOBARTUNERINFO-%d" />' % self.getTunerCount()])

            if config.plugins.MetrixWeather.enabled.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARWEATHERWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showInfoBarServiceIcons.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARSERVICEINFO" />', ''])

            channelNameXML = self.getChannelNameXML(
                "35,455",
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                config.plugins.MyMetrixLiteOther.showChannelName.getValue()
            )
            infobarSkinSearchAndReplace.append(['<panel name="CHANNELNAME" />', channelNameXML])

            if config.plugins.MyMetrixLiteOther.showInfoBarResolution.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="INFOBARRESOLUTION" />', ''])

            if config.plugins.MyMetrixLiteOther.showInfoBarClock.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            if config.plugins.MyMetrixLiteOther.showCPULoad.getValue() is False and config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="CPULOADSYSTEMP" />', ''])
            elif config.plugins.MyMetrixLiteOther.showCPULoad.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="CPULOADSYSTEMP" />', '<panel name="SYSTEMP" />'])
            elif config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is False:
                infobarSkinSearchAndReplace.append(['<panel name="CPULOADSYSTEMP" />', '<panel name="CPULOAD" />'])

            # InfoBar
            skin_lines = appendSkinFile(SKIN_INFOBAR_SOURCE, infobarSkinSearchAndReplace)

            xFile = open(SKIN_INFOBAR_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()


            move(SKIN_INFOBAR_TARGET_TMP, SKIN_INFOBAR_TARGET)


            # SecondInfoBar
            skin_lines = appendSkinFile(SKIN_SECOND_INFOBAR_SOURCE, infobarSkinSearchAndReplace)

            xFile = open(SKIN_SECOND_INFOBAR_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()


            move(SKIN_SECOND_INFOBAR_TARGET_TMP, SKIN_SECOND_INFOBAR_TARGET)



            ################
            # ChannelSelection
            ################

            channelSelectionSkinSearchAndReplace = []

            channelSelectionSkinSearchAndReplace.append(['<panel name="CHANNELSELECTION-1" />', '<panel name="%s" />' % config.plugins.MyMetrixLiteOther.channelSelectionStyle.getValue()])

            skin_lines = appendSkinFile(SKIN_CHANNEL_SELECTION_SOURCE, channelSelectionSkinSearchAndReplace)

            xFile = open(SKIN_CHANNEL_SELECTION_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            move(SKIN_CHANNEL_SELECTION_TARGET_TMP, SKIN_CHANNEL_SELECTION_TARGET)



            ################
            # MoviePlayer
            ################

            moviePlayerSkinSearchAndReplace = []

            channelNameXML = self.getChannelNameXML(
                "35,465",
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                #config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                False,
				config.plugins.MyMetrixLiteOther.showMovieName.getValue()
            )
            moviePlayerSkinSearchAndReplace.append(['<panel name="MOVIENAME" />', channelNameXML])

            if config.plugins.MyMetrixLiteOther.showInfoBarClock.getValue() is False:
                moviePlayerSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            # InfoBar
            skin_lines = appendSkinFile(SKIN_MOVIEPLAYER_SOURCE, moviePlayerSkinSearchAndReplace)

            xFile = open(SKIN_MOVIEPLAYER_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()


            move(SKIN_MOVIEPLAYER_TARGET_TMP, SKIN_MOVIEPLAYER_TARGET)

            ################
            # EMC
            ################

            EMCSkinSearchAndReplace = []

            channelNameXML = self.getChannelNameXML(
                "35,465",
                config.plugins.MyMetrixLiteOther.infoBarChannelNameFontSize.getValue(),
                #config.plugins.MyMetrixLiteOther.showChannelNumber.getValue(),
                False,
				config.plugins.MyMetrixLiteOther.showMovieName.getValue()
            )
            EMCSkinSearchAndReplace.append(['<panel name="MOVIENAME" />', channelNameXML])

            if config.plugins.MyMetrixLiteOther.showInfoBarClock.getValue() is False:
                EMCSkinSearchAndReplace.append(['<panel name="CLOCKWIDGET" />', ''])

            # InfoBar
            skin_lines = appendSkinFile(SKIN_EMC_SOURCE, EMCSkinSearchAndReplace)

            xFile = open(SKIN_EMC_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()


            move(SKIN_EMC_TARGET_TMP, SKIN_EMC_TARGET)



            ################
            # Skin
            ################

            channelselectionservice = ('name="layer-a-channelselection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservice.value + '"')
            channelselectionserviceselected = ('name="layer-a-channelselection-foregroundColorSelected" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionserviceselected.value + '"')
            channelselectionservicedescription = ('name="layer-a-channelselection-foreground-ServiceDescription" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservicedescription.value + '"')
            channelselectionservicedescriptionselected = ('name="layer-a-channelselection-foreground-ServiceDescriptionSelected" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionservicedescriptionselected.value + '"')

            windowtitletext = ('name="title-foreground" value="#' + config.plugins.MyMetrixLiteColors.windowtitletexttransparency.value + config.plugins.MyMetrixLiteColors.windowtitletext.value + '"')
            backgroundtext = ('name="background-text" value="#' + config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value + config.plugins.MyMetrixLiteColors.backgroundtext.value + '"')

            layerabackground = ('name="layer-a-background" value="#' + config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerabackground.value + '"')
            layeraforeground = ('name="layer-a-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraforeground.value + '"')
            layeraselectionbackground = ('name="layer-a-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layeraselectionbackground.value + '"')
            layeraselectionforeground = ('name="layer-a-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraselectionforeground.value + '"')
            layeraaccent1 = ('name="layer-a-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent1.value + '"')
            layeraaccent2 = ('name="layer-a-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent2.value + '"')
            layeraprogress = ('name="layer-a-progress" value="#' + config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value + config.plugins.MyMetrixLiteColors.layeraprogress.value + '"')

            layerbbackground = ('name="layer-b-background" value="#' + config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbbackground.value + '"')
            layerbforeground = ('name="layer-b-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbforeground.value + '"')
            layerbselectionbackground = ('name="layer-b-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbselectionbackground.value + '"')
            layerbselectionforeground = ('name="layer-b-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbselectionforeground.value + '"')
            layerbaccent1 = ('name="layer-b-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent1.value + '"')
            layerbaccent2 = ('name="layer-b-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent2.value + '"')
            layerbprogress = ('name="layer-b-progress" value="#' + config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value + config.plugins.MyMetrixLiteColors.layerbprogress.value + '"')

            skinSearchAndReplace = []

            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground" value="#00FFFFFF"', channelselectionservice ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foregroundColorSelected" value="#00FFFFFF"', channelselectionserviceselected ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-ServiceDescription" value="#00CCCCCC"', channelselectionservicedescription ])
            skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-ServiceDescriptionSelected" value="#00FFFFFF"', channelselectionservicedescriptionselected ])

            skinSearchAndReplace.append(['name="title-foreground" value="#11FFFFFF"', windowtitletext ])
            skinSearchAndReplace.append(['name="background-text" value="#96FFFFFF"', backgroundtext ])

            skinSearchAndReplace.append(['name="layer-a-background" value="#1E0F0F0F"', layerabackground ])
            skinSearchAndReplace.append(['name="layer-a-foreground" value="#00FFFFFF"', layeraforeground ])
            skinSearchAndReplace.append(['name="layer-a-selection-background" value="#1E27408B"', layeraselectionbackground ])
            skinSearchAndReplace.append(['name="layer-a-selection-foreground" value="#00FFFFFF"', layeraselectionforeground ])
            skinSearchAndReplace.append(['name="layer-a-accent1" value="#00CCCCCC"', layeraaccent1 ])
            skinSearchAndReplace.append(['name="layer-a-accent2" value="#007F7F7F"', layeraaccent2 ])
            skinSearchAndReplace.append(['name="layer-a-progress" value="#1E27408B"', layeraprogress ])

            skinSearchAndReplace.append(['name="layer-b-background" value="#1E27408B"', layerbbackground ])
            skinSearchAndReplace.append(['name="layer-b-foreground" value="#00FFFFFF"', layerbforeground ])
            skinSearchAndReplace.append(['name="layer-b-selection-background" value="#1E0F0F0F"', layerbselectionbackground ])
            skinSearchAndReplace.append(['name="layer-b-selection-foreground" value="#00FFFFFF"', layerbselectionforeground ])
            skinSearchAndReplace.append(['name="layer-b-accent1" value="#00CCCCCC"', layerbaccent1 ])
            skinSearchAndReplace.append(['name="layer-b-accent2" value="#007F7F7F"', layerbaccent2 ])
            skinSearchAndReplace.append(['name="layer-b-progress" value="#1EFFFFFF"', layerbprogress ])

            skinSearchAndReplace.append(['skin_00a_InfoBar.xml', 'skin_00a_InfoBar.MySkin.xml'])
            skinSearchAndReplace.append(['skin_00b_SecondInfoBar.xml', 'skin_00b_SecondInfoBar.MySkin.xml'])
            skinSearchAndReplace.append(['skin_00e_ChannelSelection.xml', 'skin_00e_ChannelSelection.MySkin.xml'])
            skinSearchAndReplace.append(['skin_00f_MoviePlayer.xml', 'skin_00f_MoviePlayer.MySkin.xml'])
            skinSearchAndReplace.append(['skin_00g_EMC.xml', 'skin_00g_EMC.MySkin.xml'])

            skin_lines = appendSkinFile(SKIN_SOURCE, skinSearchAndReplace)

            xFile = open(SKIN_TARGET_TMP, "w")
            for xx in skin_lines:
                xFile.writelines(xx)
            xFile.close()

            move(SKIN_TARGET_TMP, SKIN_TARGET)

            if not self.applyChangesFirst:
                config.skin.primary_skin.setValue("MetrixHD/skin.MySkin.xml")
                config.skin.save()
                configfile.save()
                self.reboot(_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"))

        except Exception as error:
            print error
            if not self.applyChangesFirst:
                self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

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
            return '''<widget font="SetrixHD;''' + fontSize + '''" backgroundColor="layer-a-background" foregroundColor="background-text" noWrap="1" position="''' \
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

