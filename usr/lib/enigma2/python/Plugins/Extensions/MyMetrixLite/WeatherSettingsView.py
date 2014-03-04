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

from . import _, COLOR_IMAGE_PATH
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber
from Components.ConfigList import ConfigListScreen
from Components.Pixmap import Pixmap
from enigma import ePicLoad

#############################################################

config.plugins.MetrixWeather = ConfigSubsection()

#MetrixWeather
'''
config.plugins.MetrixWeather.enabled = ConfigSelection(default="yes", choices = [
    ("yes", _("Yes")),
    ("no", _("No"))
])
'''

config.plugins.MetrixWeather.refreshInterval = ConfigNumber(default=10)
config.plugins.MetrixWeather.woeid = ConfigNumber(default=676757) #Location (visit metrixhd.info)
config.plugins.MetrixWeather.tempUnit = ConfigSelection(default="Celsius", choices = [
    ("Celsius", _("Celsius")),
    ("Fahrenheit", _("Fahrenheit"))
])

#######################################################################

class WeatherSettingsView(ConfigListScreen, Screen):
    skin = """
 <screen name="MyMetrixLiteWeatherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
    <eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
    <eLabel position="60,55" size="560,50" text="MyMetrixLite - MetrixWeather" font="Regular; 40" valign="center" transparent="1" backgroundColor="#00000000" />
    <widget name="config" position="61,114" size="590,500" backgroundColor="#00000000" foregroundColor="00ffffff" scrollbarMode="showOnDemand" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="70,640" size="160,30" text="Cancel" transparent="1" />
    <eLabel font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" position="257,640" size="160,30" text="Save" transparent="1" />
    <eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
    <eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
    <widget name="helperimage" position="840,222" size="256,256" backgroundColor="00000000" zPosition="1" transparent="1" alphatest="blend" />
  </screen>
"""

    def __init__(self, session, args = None):
        self.skin_lines = []
        Screen.__init__(self, session)
        self.session = session
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self["helperimage"] = Pixmap()

        list = []
        #list.append(getConfigListEntry(_("Enabled"), config.plugins.MyMetrixLiteWeather.enabled))
        list.append(getConfigListEntry(_("MetrixWeather ID"), config.plugins.MetrixWeather.woeid))
        list.append(getConfigListEntry(_("Unit"), config.plugins.MetrixWeather.tempUnit))
        list.append(getConfigListEntry(_("Refresh Interval (min)"), config.plugins.MetrixWeather.refreshInterval))

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
            "green": self.save,
            "cancel": self.exit
        }, -1)

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

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyDown(self):
        self["config"].instance.moveSelection(self["config"].instance.moveDown)

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)

    def showInfo(self):
        self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

    def save(self):
        for x in self["config"].list:
            if len(x) > 1:
                x[1].save()
            else:
                pass

        configfile.save()
        self.exit()

    def exit(self):
        for x in self["config"].list:
            if len(x) > 1:
                    x[1].cancel()
            else:
                    pass
        self.close()
