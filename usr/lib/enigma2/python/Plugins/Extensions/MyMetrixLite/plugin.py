#######################################################################
#
#    ColorsSettingsView by arn354 and svox
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
from Components.config import config
from Plugins.Plugin import PluginDescriptor

from . import _
from .MainSettingsView import MainSettingsView
from .ActivateSkinSettings import applySkinSettings

config.plugins.MetrixWeather.currentWeatherDataValid.setValue(0)

#############################################################


def main(session, **kwargs):
	session.open(MainSettingsView)

def autostart(reason, **kwargs):
	if reason == 0:
		applySkinSettings(fullInit=True)

def Plugins(**kwargs):
	pluginList = []
	if "MetrixHD" in config.skin.primary_skin.value:
		pluginList.append(PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART], fnc=autostart))
		pluginList.append(PluginDescriptor(name="MyMetrixLite", description=_("openATV configuration tool for MetrixHD"), icon="plugin.png", where=[PluginDescriptor.WHERE_PLUGINMENU], fnc=main))
	return pluginList
