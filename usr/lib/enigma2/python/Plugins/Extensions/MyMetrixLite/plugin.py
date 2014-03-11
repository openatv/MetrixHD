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

from . import _
from MainSettingsView import MainSettingsView
from Plugins.Plugin import PluginDescriptor

#############################################################

def main(session, **kwargs):
    session.open(MainSettingsView)

def Plugins(**kwargs):
    return PluginDescriptor(name="MyMetrixLite", description=_("openATV configuration tool for MetrixHD"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)
