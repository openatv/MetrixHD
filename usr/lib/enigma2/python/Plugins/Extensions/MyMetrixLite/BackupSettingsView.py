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

from . import _, MAIN_IMAGE_PATH, BACKUP_FILE
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, getConfigListEntry, ConfigSelectionNumber, ConfigText
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from enigma import ePicLoad, eTimer
from os import path
import pickle
from time import time, localtime, strftime
from ColorsSettingsView import ColorsSettingsView
from WeatherSettingsView import WeatherSettingsView
from OtherSettingsView import OtherSettingsView
from FontsSettingsView import FontsSettingsView
from ActivateSkinSettings import ActivateSkinSettings
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists

#############################################################

class BackupSettingsView(ConfigListScreen, Screen):
	skin = """
	<screen name="MyMetrixLiteBackupView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
	<widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
	<widget name="config" position="61,124" size="590,210" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
	<widget source="cancelBtn" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="loadBtn" position="257,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="saveBtn" position="444,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="deleteBtn" position="631,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
	<eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
	<eLabel position="429,635" size="5,40" backgroundColor="#00e5dd00" />
	<eLabel position="616,635" size="5,40" backgroundColor="#000064c7" />
	<widget name="HelpWindow" position="55,400" size="604,126" zPosition="1" transparent="1" alphatest="blend" />
	<widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
	<widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
	</screen>
"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self.session = session
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()

		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()

		self["helperimage"] = Pixmap()
		self["helpertext"] = Label()

		self["titleText"] = StaticText("")
		self["titleText"].setText(_("Backup & Restore my settings"))

		self["cancelBtn"] = StaticText("")
		self["cancelBtn"].setText(_("Cancel"))

		self["saveBtn"] = StaticText("")
		self["saveBtn"].setText(_("Backup"))

		self["loadBtn"] = StaticText("")
		self["loadBtn"].setText(_("Restore"))

		self["deleteBtn"] = StaticText("")
		self["deleteBtn"].setText(_("Delete"))

		self.myset = ConfigSelectionNumber(1, 99, 1, default = 1, wraparound = True)
		self.myname = ConfigText(default = _("My Backup No. %d") % self.myset.value, visible_width = 50, fixed_size = False)
		self.mydate = ""
		self.mylastBackup = ""
		self.mylastRestore = ""
		self.file = []

		ConfigListScreen.__init__(
			self,
			self.getMenuItemList(),
			session = session,
			on_change = self.changedEntry
		)

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
			"green": self.restoreQ,
			"yellow": self.backupQ,
			"blue": self.deleteQ,
			"cancel": self.exit,
			"ok": self.renameName
		}, -1)

		self.changedEntry(True)
		self.onLayoutFinish.append(self.UpdatePicture)

	def getMenuItemList(self):
		list = []
		char = 150
		sep = "-"
		tab = " "*10

		list.append(getConfigListEntry(_("My Backup Number"), self.myset, _("You can create up to 99 Backup-Sets.\nStored in:\n%s") % BACKUP_FILE, 'REFRESH'))
		list.append(getConfigListEntry(_("My Backup Description"), self.myname, _("You can here assign an individual name.") + _("\nPress 'OK-Button'")))
		list.append(getConfigListEntry(tab))
		list.append(getConfigListEntry((tab * 2) + _("My Backup Saved:   %s") % self.mydate))
		list.append(getConfigListEntry(sep * char))
		list.append(getConfigListEntry(tab))
		list.append(getConfigListEntry((tab + _("My Last Backup Entry:   %s") + tab + _("My Last Restored Entry:   %s")) % (self.mylastBackup, self.mylastRestore)))

		return list

	def renameName(self):
		if not isinstance(self["config"].getCurrent()[1], ConfigText): return
		self.oldname = self.myname.value
		self.session.openWithCallback(self.renameNameCB, VirtualKeyBoard, title=_("Please enter new name:"), text=self.myname.value)

	def renameNameCB(self, name):
		if name and self.oldname != name:
			self.myname.value = name

			set = self.myset.value
			name= self.myname.value
			newname = False
			data = []
			for entries in self.file:
				if "set%dname" %set in entries:
					data +=[("set%dname" %set, name)]
					newname = True
				else:
					data += [entries]

			if newname:
				self.file = data
				self.writeFile()

	def GetPicturePath(self):
		picturepath = resolveFilename(SCOPE_CURRENT_SKIN, "mymetrixlite/MyMetrixLiteBackup.png")
		if not fileExists(picturepath):
			picturepath = MAIN_IMAGE_PATH % "MyMetrixLiteBackup"
		return picturepath

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(),self["helperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#00000000"])
		self.PicLoad.startDecode(self.GetPicturePath())
		self.showHelperText()

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		#self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		#self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def writeFile(self):
		try:
			f = file(BACKUP_FILE,'wb')
			pickle.dump(self.file, f)
			f.close()
			self.changedEntry(True)
		except IOError:
			self.message(_("Can't create Backup-File!\n( %s )")% BACKUP_FILE, MessageBox.TYPE_ERROR)

	def readFile(self):

		if path.exists(BACKUP_FILE):
			try:
				f = file(BACKUP_FILE, "rb")
				self.file = pickle.load(f)
				f.close()
				return True
			except EOFError:
				pass
		return False

	def restore(self):
		self["titleText"].setText(_("Backup & Restore my settings"))
		if not self.readFile():
			self.message(_("No Backup-File found!\n( %s )")% BACKUP_FILE, MessageBox.TYPE_ERROR)
			return
		set = self.myset.value
		s=0

		# test backup-set
		for entries in self.file:
			if "set%dname" %set in entries:
				s+=1
			elif "set%ddate" %set in entries:
				s+=1
			elif "set%dcolor" %set in entries:
				s+=1
			elif "set%dfont" %set in entries:
				s+=1
			elif "set%dother" %set in entries:
				s+=1
			elif "set%dweather" %set in entries:
				s+=1

		if s == 6:
			pass
		elif s > 0:
			self.message(_("Backup-Set is not complete!"), MessageBox.TYPE_ERROR)
			return
		else:
			self.message(_("No Backup-Set found!"), MessageBox.TYPE_ERROR)
			return

		self.defaults()

		for entries in self.file:
			if "set%dcolor" %set in entries:
				config.plugins.MyMetrixLiteColors.setSavedValue(entries[1])
			elif "set%dfont" %set in entries:
				config.plugins.MyMetrixLiteFonts.setSavedValue(entries[1])
			elif "set%dother" %set in entries:
				config.plugins.MyMetrixLiteOther.setSavedValue(entries[1])
			elif "set%dweather" %set in entries:
				config.plugins.MetrixWeather.setSavedValue(entries[1])

		self.delete(writeFile = False, restore = True)
		self.file+=[("myLastRestore", set)]
		self.writeFile()
		configfile.save()
		self.message(_("Settings successfully restored."), MessageBox.TYPE_INFO)
		ActivateSkinSettings().initConfigs()
		self.exit()

	def message(self, text, type):
		self.session.open(MessageBox, text, type, timeout = 5)

	def messageQ(self, text, type, default, runnext):
		self.runnext = runnext
		self.session.openWithCallback(self.showHelpWindowQ, MessageBox, text, type, default = default, timeout = 5)

	def showHelpWindowQ(self, result):
		if result:
			self.delay = eTimer() # delay for closing messagebox
			if self.runnext == "delete":
				self.delay.callback.append(self.delete)
				self.delay.start(500, True)
			elif self.runnext == "backup":
				self.delay.callback.append(self.backup)
				self.delay.start(500, True)
			elif  self.runnext == "restore":
				self["titleText"].setText(_("Restoring Backup-Set %d ...") %self.myset.value)
				self.delay.callback.append(self.restore)
				self.delay.start(500, True)

	def delete(self, writeFile = True, restore = False):
		self.readFile()
		set = self.myset.value
		data = []

		for entries in self.file:
			if "set%dname" %set in entries and not restore:
				pass
			elif "set%ddate" %set in entries and not restore:
				pass
			elif "set%dcolor" %set in entries and not restore:
				pass
			elif "set%dfont" %set in entries and not restore:
				pass
			elif "set%dother" %set in entries and not restore:
				pass
			elif "set%dweather" %set in entries and not restore:
				pass
			elif "myLastBackup" in entries and not restore and not writeFile:
				pass
			elif "myLastBackup" in entries and entries[1] == set and writeFile:
				pass
			elif "myLastRestore" in entries and restore and not writeFile:
				pass
			elif "myLastRestore" in entries and entries[1] == set and writeFile:
				pass
			else:
				data += [entries]

		self.file = data
		if writeFile:
			self.writeFile()

	def deleteQ(self):
		run = True
		set = self.myset.value
		for entries in self.file:
			if "set%dname" %set in entries:
				self.messageQ(_("Delete current Backup-Set?"), MessageBox.TYPE_YESNO, False, "delete")
				run = False
				break
		if run:
			self.delete()

	def backupQ(self):
		run = True
		set = self.myset.value
		for entries in self.file:
			if "set%dname" %set in entries:
				self.messageQ(_("Overwrite current Backup-Set?"), MessageBox.TYPE_YESNO, False, "backup")
				run = False
				break
		if run:
			self.backup()

	def restoreQ(self):
		run = True
		set = self.myset.value
		for entries in self.file:
			if "set%dname" %set in entries:
				self.messageQ(_("Overwrite current Settings?"), MessageBox.TYPE_YESNO, False, "restore")
				run = False
				break
		if run:
			self.restore()

	def backup(self):
		set = self.myset.value
		name= self.myname.value
		date = strftime("%a, %d.%m.%Y, %H:%M:%S", localtime(time()))

		self.delete(writeFile = False)

		self.file+=[("myLastBackup", set)]
		self.file+=[("set%dname" %set, name)]
		self.file+=[("set%ddate" %set, date)]
		self.file+=[("set%dcolor" %set, config.plugins.MyMetrixLiteColors.getSavedValue())]
		self.file+=[("set%dfont" %set, config.plugins.MyMetrixLiteFonts.getSavedValue())]
		self.file+=[("set%dother" %set, config.plugins.MyMetrixLiteOther.getSavedValue())]
		self.file+=[("set%dweather" %set, config.plugins.MetrixWeather.getSavedValue())]
		self.writeFile()

	def exit(self):
		self.close()

	def defaults(self):
		ColorsSettingsView(None).defaults(True)
		FontsSettingsView(None).defaults(True)
		OtherSettingsView(None).defaults(True)
		WeatherSettingsView(None).defaults(True)

	def changedEntry(self, refresh = False):
		if not self.file:
			self.readFile()

		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == "REFRESH" or refresh:
			name = _("My Backup No. %d") % self.myset.value
			date = _("     ") + _("--- empty ---")
			backup = _("-")
			restore = _("-")

			if self.file:
				set = self.myset.value
				for entries in self.file:
					if "set%sname" %set in entries:
						name = entries[1]
					elif "set%sdate" %set in entries:
						date = entries[1]
					elif "set%sdate" %set in entries:
						date = entries[1]
					elif "myLastBackup" in entries:
						backup = entries[1]
					elif "myLastRestore" in entries:
						restore = entries[1]

			self.myname.value = name
			self.mydate = date
			self.mylastBackup = backup
			self.mylastRestore = restore

			self["config"].setList(self.getMenuItemList())
			self.hideHelpWindow()

	def showHelperText(self):
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")
		self.hideHelpWindow()

	def hideHelpWindow(self):
		if isinstance(self["config"].getCurrent()[1], ConfigText):
			if self["config"].getCurrent()[1].help_window.instance is not None:
				self["config"].getCurrent()[1].help_window.hide()
