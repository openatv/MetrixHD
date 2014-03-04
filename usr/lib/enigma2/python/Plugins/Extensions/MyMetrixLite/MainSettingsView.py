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

from . import _, appendSkinFile, SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP, COLOR_IMAGE_PATH, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP

import os

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Components.Pixmap import Pixmap
from shutil import move, copy
from skin import parseColor
from enigma import ePicLoad, eListboxPythonMultiContent, gFont
from ColorsSettingsView import ColorsSettingsView
from WeatherSettingsView import WeatherSettingsView

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
    <eLabel position="60,55" size="500,50" text="MyMetrixLite" font="Regular; 40" valign="center" transparent="1" backgroundColor="#00000000" />
    <widget name="menuList" position="61,114" size="590,500" backgroundColor="#00000000" foregroundColor="00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="70,640" size="160,30" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="257,640" size="160,30" text="Apply changes" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        Screen.__init__(self, session)
        self.session = session
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

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

        self["menuList"] = MainMenuList([], font0=24, font1=15, itemHeight=50)
        self["menuList"].l.setList(list)
        self["menuList"].onSelectionChanged.append(self.__selectionChanged)

        self.onChangedEntry = []

        self.onLayoutFinish.append(self.UpdatePicture)

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
        self.PicLoad.startDecode(COLOR_IMAGE_PATH % "FFFFFF")

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

    def reboot(self, message = None):
        if message is None:
            message = _("Do you really want to reboot now?")

        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, message, MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Restart GUI"))

    def applyChanges(self):

        try:
            if os.path.isfile(SKIN_TARGET_TMP) is False:
                #create tmp file
                copy(SKIN_SOURCE, SKIN_TARGET_TMP)

            if os.path.isfile(SKIN_INFOBAR_TARGET_TMP) and os.path.isfile(SKIN_SECOND_INFOBAR_TARGET_TMP):
                move(SKIN_INFOBAR_TARGET_TMP, SKIN_INFOBAR_TARGET)
                move(SKIN_SECOND_INFOBAR_TARGET_TMP, SKIN_SECOND_INFOBAR_TARGET)

                skinSearchAndReplace = []
                skinSearchAndReplace.append(['skin_00a_InfoBar.xml', 'skin_00a_InfoBar.MySkin.xml'])
                skinSearchAndReplace.append(['skin_00b_SecondInfoBar.xml', 'skin_00b_SecondInfoBar.MySkin.xml'])

                skin_lines = appendSkinFile(SKIN_TARGET_TMP, skinSearchAndReplace)

                xFile = open(SKIN_TARGET_TMP, "w")
                for xx in skin_lines:
                    xFile.writelines(xx)
                xFile.close()

            move(SKIN_TARGET_TMP, SKIN_TARGET)

            config.skin.primary_skin.setValue("MetrixHD/skin.MySkin.xml")
            config.skin.save()
        except:
            self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

        configfile.save()

        self.reboot(_("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?"))

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def exit(self):
        self.close()

    def __selectionChanged(self):
        pass