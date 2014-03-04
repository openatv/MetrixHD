#######################################################################
#
#    MyMetrixLite by arn354 and svox
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
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext
from os import environ

#############################################################

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("MyMetrixLite", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/MyMetrixLite/locale/"))

def _(txt):
    t = gettext.dgettext("MyMetrixLite", txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t

#############################################################

SKIN_TARGET = "/usr/share/enigma2/MetrixHD/skin.MySkin.xml"
SKIN_TARGET_TMP = SKIN_TARGET + ".tmp"
SKIN_SOURCE = "/usr/share/enigma2/MetrixHD/skin.xml"

#############################################################

COLOR_IMAGE_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/MyMetrixLite/images/%s.png"