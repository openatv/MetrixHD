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

from . import _, SKIN_TARGET_TMP, SKIN_SOURCE, COLOR_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from skin import parseColor
from Components.Pixmap import Pixmap
from enigma import ePicLoad


#############################################################


ColorList = [
            ("F0A30A", _("Amber")),
            ("825A2C", _("Brown")),
            ("0050EF", _("Cobalt")),
            ("911D10", _("Crimson")),
            ("1BA1E2", _("Cyan")),
            ("00008B", _("Darkblue")),
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

config.plugins.MyMetrixLiteColors.backgroundtext = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.backgroundtexttransparency = ConfigSelection(default="80", choices = TransparencyList)

config.plugins.MyMetrixLiteColors.layerabackground = ConfigSelection(default="1C1C1C", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerabackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
config.plugins.MyMetrixLiteColors.layeraforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraselectionbackground = ConfigSelection(default="0050EF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
config.plugins.MyMetrixLiteColors.layeraselectionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraaccent1 = ConfigSelection(default="BDBDBD", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraaccent2 = ConfigSelection(default="6E6E6E", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraprogress = ConfigSelection(default="0050EF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layeraprogresstransparency = ConfigSelection(default="1A", choices = TransparencyList)

config.plugins.MyMetrixLiteColors.layerbbackground = ConfigSelection(default="0050EF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
config.plugins.MyMetrixLiteColors.layerbforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbselectionbackground = ConfigSelection(default="1C1C1C", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency = ConfigSelection(default="1A", choices = TransparencyList)
config.plugins.MyMetrixLiteColors.layerbselectionforeground = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbaccent1 = ConfigSelection(default="BDBDBD", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbaccent2 = ConfigSelection(default="6E6E6E", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbprogress = ConfigSelection(default="FFFFFF", choices = ColorList)
config.plugins.MyMetrixLiteColors.layerbprogresstransparency = ConfigSelection(default="1A", choices = TransparencyList)

#######################################################################

class ColorsSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteColorsView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <eLabel position="60,55" size="500,50" text="MyMetrixLite - MetrixColors" font="Regular; 40" valign="center" transparent="1" backgroundColor="#00000000" />
    <widget name="config" position="61,114" size="590,500" backgroundColor="#00000000" foregroundColor="00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="70,640" size="160,30" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="257,640" size="160,30" text="Save" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="445,640" size="160,30" text="Defaults" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self.picPath = COLOR_IMAGE_PATH % "FFFFFF"
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

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

        config.plugins.MyMetrixLiteColors.save()

        self.exit()

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

        try:
            self.backgroundtext = ('name="background-text" value="#' + config.plugins.MyMetrixLiteColors.backgroundtexttransparency.value + config.plugins.MyMetrixLiteColors.backgroundtext.value + '"')

            self.layerabackground = ('name="layer-a-background" value="#' + config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerabackground.value + '"')
            self.layeraforeground = ('name="layer-a-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraforeground.value + '"')
            self.layeraselectionbackground = ('name="layer-a-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layeraselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layeraselectionbackground.value + '"')
            self.layeraselectionforeground = ('name="layer-a-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layeraselectionforeground.value + '"')
            self.layeraaccent1 = ('name="layer-a-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent1.value + '"')
            self.layeraaccent2 = ('name="layer-a-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layeraaccent2.value + '"')
            self.layeraprogress = ('name="layer-a-progress" value="#' + config.plugins.MyMetrixLiteColors.layeraprogresstransparency.value + config.plugins.MyMetrixLiteColors.layeraprogress.value + '"')

            self.layerbbackground = ('name="layer-b-background" value="#' + config.plugins.MyMetrixLiteColors.layerbbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbbackground.value + '"')
            self.layerbforeground = ('name="layer-b-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbforeground.value + '"')
            self.layerbselectionbackground = ('name="layer-b-selection-background" value="#' + config.plugins.MyMetrixLiteColors.layerbselectionbackgroundtransparency.value + config.plugins.MyMetrixLiteColors.layerbselectionbackground.value + '"')
            self.layerbselectionforeground = ('name="layer-b-selection-foreground" value="#00' + config.plugins.MyMetrixLiteColors.layerbselectionforeground.value + '"')
            self.layerbaccent1 = ('name="layer-b-accent1" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent1.value + '"')
            self.layerbaccent2 = ('name="layer-b-accent2" value="#00' + config.plugins.MyMetrixLiteColors.layerbaccent2.value + '"')
            self.layerbprogress = ('name="layer-b-progress" value="#' + config.plugins.MyMetrixLiteColors.layerbprogresstransparency.value + config.plugins.MyMetrixLiteColors.layerbprogress.value + '"')

            self.skinSearchAndReplace = []

            self.skinSearchAndReplace.append(['name="background-text" value="#96FFFFFF"', self.backgroundtext ])

            self.skinSearchAndReplace.append(['name="layer-a-background" value="#1E0F0F0F"', self.layerabackground ])
            self.skinSearchAndReplace.append(['name="layer-a-foreground" value="#00FFFFFF"', self.layeraforeground ])
            self.skinSearchAndReplace.append(['name="layer-a-selection-background" value="#1E27408B"', self.layeraselectionbackground ])
            self.skinSearchAndReplace.append(['name="layer-a-selection-foreground" value="#00FFFFFF"', self.layeraselectionforeground ])
            self.skinSearchAndReplace.append(['name="layer-a-accent1" value="#00CCCCCC"', self.layeraaccent1 ])
            self.skinSearchAndReplace.append(['name="layer-a-accent2" value="#007F7F7F"', self.layeraaccent2 ])
            self.skinSearchAndReplace.append(['name="layer-a-progress" value="#1E27408B"', self.layeraprogress ])

            self.skinSearchAndReplace.append(['name="layer-b-background" value="#1E27408B"', self.layerbbackground ])
            self.skinSearchAndReplace.append(['name="layer-b-foreground" value="#00FFFFFF"', self.layerbforeground ])
            self.skinSearchAndReplace.append(['name="layer-b-selection-background" value="#1E0F0F0F"', self.layerbselectionbackground ])
            self.skinSearchAndReplace.append(['name="layer-b-selection-foreground" value="#00FFFFFF"', self.layerbselectionforeground ])
            self.skinSearchAndReplace.append(['name="layer-b-accent1" value="#00CCCCCC"', self.layerbaccent1 ])
            self.skinSearchAndReplace.append(['name="layer-b-accent2" value="#007F7F7F"', self.layerbaccent2 ])
            self.skinSearchAndReplace.append(['name="layer-b-progress" value="#1EFFFFFF"', self.layerbprogress ])

            self.appendSkinFile(SKIN_SOURCE)

            xFile = open(SKIN_TARGET_TMP, "w")
            for xx in self.skin_lines:
                xFile.writelines(xx)
            xFile.close()
        except:
            self.session.open(MessageBox, _("Error creating Skin!"), MessageBox.TYPE_ERROR)

        configfile.save()
        self.exit()

    def appendSkinFile(self, appendFileName, skinPartSearchAndReplace=None):
        """
        add skin file to main skin content

        appendFileName:
         xml skin-part to add

        skinPartSearchAndReplace:
         (optional) a list of search and replace arrays. first element, search, second for replace
        """
        skFile = open(appendFileName, "r")
        file_lines = skFile.readlines()
        skFile.close()

        tmpSearchAndReplace = []

        if skinPartSearchAndReplace is not None:
            tmpSearchAndReplace = self.skinSearchAndReplace + skinPartSearchAndReplace
        else:
            tmpSearchAndReplace = self.skinSearchAndReplace

        for skinLine in file_lines:
            for item in tmpSearchAndReplace:
                skinLine = skinLine.replace(item[0], item[1])
            self.skin_lines.append(skinLine)

    def exit(self):
        for x in self["config"].list:
            if len(x) > 1:
                    x[1].cancel()
            else:
                    pass
        self.close()
