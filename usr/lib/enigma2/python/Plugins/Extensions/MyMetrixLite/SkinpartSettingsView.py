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

from enigma import ePicLoad, getDesktop
from os import listdir, remove, symlink, makedirs

from os.path import exists, isdir, isfile, islink
from shutil import copy
from six import ensure_str

from Components.ActionMap import ActionMap
from Components.config import configfile, getConfigListEntry, ConfigYesNo, ConfigSubList, ConfigSubDict, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Label import Label
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists

from . import _, PLUGIN_PATH

#############################################################


class SkinpartSettingsView(ConfigListScreen, Screen):
	MAIN_IMAGE_PATH = PLUGIN_PATH + "/images/%s.png"
	skin = """
	<screen name="MyMetrixLiteOtherView" position="0,0" size="1280,720" flags="wfNoBorder" backgroundColor="transparent">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="#00000000" transparent="0" />
	<widget source="titleText" position="60,55" size="590,50" render="Label" font="Regular; 40" foregroundColor="#00ffffff" backgroundColor="#00000000" valign="center" transparent="1" />
	<widget name="config" position="61,124" size="590,480" backgroundColor="#00000000" foregroundColor="#00ffffff" scrollbarMode="showOnDemand" transparent="1" />
	<widget source="key_red" position="70,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="key_green" position="257,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="key_yellow" position="445,640" size="160,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<widget source="key_blue" position="631,640" size="360,30" render="Label" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#00000000" halign="left" transparent="1" />
	<eLabel position="55,635" size="5,40" backgroundColor="#00e61700" />
	<eLabel position="242,635" size="5,40" backgroundColor="#0061e500" />
	<eLabel position="430,635" size="5,40" backgroundColor="#00e5dd00" />
	<eLabel position="616,635" size="5,40" backgroundColor="#000064c7" />
	<widget name="helperimage" position="840,222" size="256,256" backgroundColor="#00000000" zPosition="1" transparent="1" alphatest="blend" />
	<widget name="helpertext" position="800,490" size="336,160" font="Regular; 18" backgroundColor="#00000000" foregroundColor="#00ffffff" halign="center" valign="center" transparent="1"/>
	</screen>
"""

	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.skinName = "MetrixSettingsView"

		self.PicLoad = ePicLoad()
		self["helperimage"] = Pixmap()
		self["helpertext"] = Label()

		self["titleText"] = StaticText("")
		self["titleText"].setText(_("Skinpart settings"))

		self["key_red"] = StaticText("")
		self["key_red"].setText(_("Cancel"))

		self["key_green"] = StaticText("")
		self["key_green"].setText(_("Save"))

		self["key_yellow"] = StaticText("")
		self["key_yellow"].setText(_("Defaults"))

		self["key_blue"] = StaticText("")
		self["key_blue"].setText(_("Zoom"))

		self.linkGlobalSkinParts()
		self.getSkinParts()

		ConfigListScreen.__init__(
			self,
			self.getMenuItemList(),
			session=session,
			on_change=self.selectionChanged
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
			"red": self.keyCancel,
			"green": self.save,
			"blue": self.zoom,
			"yellow": self.defaults,
			"cancel": self.keyCancel
		}, -1)

		self.onLayoutFinish.append(self.UpdatePicture)

	def selectionChanged(self):
		cur = self["config"].getCurrent()
		cur = cur and len(cur) > 3 and cur[3]

		if cur == "ENABLED":
			self["config"].setList(self.getMenuItemList())

	def getMenuItemList(self):
		list = []
		char = 150
		tab = " " * 10
		sep = "-"
		nodesc = _("No description available.")
		noprev = _("\n(No preview picture available.)")

		section = _("/usr/share/enigma2/MetrixHD/skinparts/[part]/[part].xml")
		list.append(getConfigListEntry(section + tab + sep * (char - len(section) - len(tab)), ))
		pidx = 0
		for part in self.partlist:
			if not isfile(self.parts[pidx][0][0] + self.parts[pidx][0][1] + '.xml'):
				part.value = '0'
				itext = _("Skinpart are not available - can't be activated.")
			else:
				if not self.parts[pidx][0][3]:
					itext = nodesc
				else:
					itext = self.parts[pidx][0][3]
				if not self.parts[pidx][0][2]:
					itext += noprev
			preview = self.parts[pidx][0][0] + self.parts[pidx][0][2]
			list.append(getConfigListEntry(tab + self.parts[pidx][0][1], part, itext, 'ENABLED', preview))
			if int(part.value) > 1:
				sidx = 0
				for screen in self.screenlist[pidx]:
					if not self.screens[pidx][sidx][3]:
						itext = nodesc
					else:
						itext = self.screens[pidx][sidx][3]
					if not self.screens[pidx][sidx][2]:
						itext += noprev
					preview = self.parts[pidx][0][0] + '/' + self.screens[pidx][sidx][2]
					list.append(getConfigListEntry(tab * 2 + self.screens[pidx][sidx][1], screen, itext, 'ENABLED', preview))
					sidx += 1
			pidx += 1

		return list

	def linkGlobalSkinParts(self):
		dir_global_skinparts = "/usr/share/enigma2/skinparts"
		dir_local_skinparts = "/usr/share/enigma2/MetrixHD/skinparts"
		if exists(dir_global_skinparts):
			for pack in listdir(dir_global_skinparts):
				if isdir(dir_global_skinparts + "/" + pack):
					for d in listdir(dir_global_skinparts + "/" + pack):
						if exists(dir_global_skinparts + "/" + pack + "/" + d + "/" + d + ".xml"):
							if not exists(dir_local_skinparts + "/" + d):
								makedirs(dir_local_skinparts + "/" + d)
							for f in listdir(dir_global_skinparts + "/" + pack + "/" + d):
								print(dir_local_skinparts + "/" + d + "/" + f)
								print(dir_global_skinparts + "/" + pack + "/" + d + "/" + f)
								if (not islink(dir_local_skinparts + "/" + d + "/" + f)) and (not exists(dir_local_skinparts + "/" + d + "/" + f)):
									print("1")
									symlink(dir_global_skinparts + "/" + pack + "/" + d + "/" + f, dir_local_skinparts + "/" + d + "/" + f)

	def getSkinParts(self):
		self.parts = {}
		self.screens = {}
		self.partlist = ConfigSubList()
		self.screenlist = ConfigSubDict()
		self.idx = 0
		self.readSkinParts("/usr/share/enigma2/MetrixHD/skinparts/")

	def readSkinParts(self, skinpartdir):
		for skinpart in listdir(skinpartdir):
			enabled = '0'
			partname = skinpart
			partpath = skinpartdir + skinpart + '/'
			partfile = partpath + skinpart + '.xml'
			if not isfile(partpath[:-1]):
				if isfile(partpath + 'enabled'):
					enabled = '1'
				self.readSkinPartScreens(partpath, partname)
				if len(self.screenlist[self.idx]):
					self.partlist.append(ConfigSelection(default='0', choices=[("0", _("No")), ("2", _("Yes, show screens")), ("1", _("Yes")), ("3", _("Yes, show screens"))]))
				else:
					self.partlist.append(ConfigSelection(default='0', choices=[("0", _("No")), ("1", _("Yes"))]))
				self.partlist[self.idx].value = enabled
				self.idx += 1

	def readSkinPartScreens(self, partpath, partname):
		part = []
		screen = []
		lines = []
		self.screenlist[self.idx] = ConfigSubList()

		lidx = screenname = previewfile = description = ''
		enabled = p_nfo = s_nfo = False

		if isfile(partpath + partname + '.xml'):
			f = open(partpath + partname + '.xml', 'r')
			lines = f.readlines()
			f.close()
			if isfile(partpath + partname + '.txt'):
				try:
					f = open(partpath + partname + '.txt', 'r')
					description = f.read()
				except UnicodeDecodeError:
					print("[MetrixHD] - WARNING : (" + partpath + partname + ") should be UTF-8")
					f.close()
					f = open(partpath + partname + '.txt', 'rb')
					description = f.read()
					f.close()
					try:
						description = description.decode("latin-1")
					except UnicodeDecodeError:
						print("[MetrixHD] - WARNING : (" + partpath + partname + ") must be UTF-8 or latin-1")
						description = description.decode("utf-8", "ignore")
			if isfile(partpath + partname + '.png'):
				previewfile = partname + '.png'
			elif isfile(partpath + partname + '.jpg'):
				previewfile = partname + '.jpg'

		idx = 0
		for line in lines:
			idx += 1
			if '<screen' in line or '</screen>' in line:
				if p_nfo:
					description = description.replace('\t', '').lstrip('\n').rstrip('\n').strip()
					part.append((partpath, partname, previewfile, description))
					previewfile = description = ''
					p_nfo = False
				elif s_nfo:
					description = description.replace('\t', '').lstrip('\n').rstrip('\n').strip()
					screen.append((lidx, screenname, previewfile, description.rstrip('\n'), enabled))
					lidx = screenname = previewfile = description = ''
					enabled = s_nfo = False

			if '<skin>' in line:
				p_nfo = True
			if '<screen' in line and '#hide#' not in line:
				s_nfo = True
				a = line.find('name=')
				b = line.find('"', a)
				c = line.find('"', b + 1)
				name = line[b + 1:c]
				#// fix old typo
				name = name.replace('#deactivatd#', '#deactivated#')
				#//
				sname = name.replace('#deactivated#', '')
				if isfile(partpath + sname + '.txt'):
					try:
						f = open(partpath + sname + '.txt', 'r')
						description = f.read()
					except UnicodeDecodeError:
						print("[MetrixHD] - WARNING : (" + partpath + sname + ") should be UTF-8")
						f.close()
						f = open(partpath + sname + '.txt', 'rb')
						description = f.read()
						f.close()
						try:
							description = description.decode("latin-1")
						except UnicodeDecodeError:
							print("[MetrixHD] - WARNING : (" + partpath + sname + ") must be UTF-8 or latin-1")
							description = description.decode("utf-8", "ignore")
						description = ensure_str(description)
				if isfile(partpath + sname + '.png'):
					previewfile = sname + '.png'
				elif isfile(partpath + sname + '.jpg'):
					previewfile = sname + '.jpg'

				if '#deactivated#' in name:
					screenname = name.replace('#deactivated#', '')
					enabled = False
				else:
					screenname = name
					enabled = True
				lidx = idx

			if '#description#' in line:
				a = line.find('#description#')
				description += line[a + 13:]
			elif '#previewfile#' in line:
				a = line.find('#previewfile#')
				file = line[a + 13:].replace('\n', '').replace('\t', '').lstrip('/').strip()
				if isfile(partpath + file):
					previewfile = file

		if not part:
			part.append((partpath, partname, previewfile, description))
		self.parts[self.idx] = part
		self.screens[self.idx] = screen

		idx = 0
		for screen in self.screens[self.idx]:
			self.screenlist[self.idx].append(ConfigYesNo(default=False))
			self.screenlist[self.idx][idx].value = self.screens[self.idx][idx][4]  # screen[4]
			idx += 1

	def GetPicturePath(self):
		zoomEnable = False
		if len(self["config"].getCurrent()) > 3:
			picturepath = self["config"].getCurrent()[4]
			if isfile(picturepath):
				zoomEnable = True
		if not zoomEnable or not isfile(picturepath):
			picturepath = resolveFilename(SCOPE_CURRENT_SKIN, "mymetrixlite/MyMetrixLiteSkinpart.png")
			if not fileExists(picturepath):
				picturepath = self.MAIN_IMAGE_PATH % "MyMetrixLiteSkinpart"

		if zoomEnable and "blue" not in self["actions"].actions:
			self["actions"].actions.update({"blue": self.zoom})
			self["key_blue"].setText(_("Zoom"))
		elif not zoomEnable and "blue" in self["actions"].actions:
			del self["actions"].actions["blue"]
			self["key_blue"].setText("")

		return picturepath

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["helperimage"].instance.size().width(), self["helperimage"].instance.size().height(), 1, 1, 0, 1, "#00000000"])
		self.PicLoad.startDecode(self.GetPicturePath())
		self.showHelperText()

	def DecodePicture(self, PicInfo=""):
		ptr = self.PicLoad.getData()
		self["helperimage"].instance.setPixmap(ptr)

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def zoom(self):
		self.session.open(zoomPreview, self.GetPicturePath())

	def save(self):
		idxerrtxt = ''
		idxerrcnt = 0
		pidx = 0
		for part in self.partlist:
			idxerr = False
			efile = self.parts[pidx][0][0] + 'enabled'
			sfile = self.parts[pidx][0][0] + self.parts[pidx][0][1] + '.xml'
			tfile = self.parts[pidx][0][0] + self.parts[pidx][0][1] + '.xml.tmp'
			if part.value != '0':
				f = open(efile, 'w').close()
				if isfile(sfile):
					f = open(sfile, 'r')
					source = f.readlines()
					f.close()
					sidx = 0
					for screen in self.screenlist[pidx]:
						idx = self.screens[pidx][sidx][0] - 1
						if len(source) > idx:
							line = source[idx]
							screenname = ''
							if '<screen' in line:
								a = line.find('name=')
								b = line.find('"', a)
								c = line.find('"', b + 1)
								name = line[b + 1:c]
								#// fix old typo
								if '#deactivatd#' in name:
									screenname = name = name.replace('#deactivatd#', '#deactivated#')
								#//
								if name.replace('#deactivated#', '') == self.screens[pidx][sidx][1]:
									if not screen.value and '#deactivated#' not in name:
										screenname = '#deactivated#' + name
									elif screen.value and '#deactivated#' in name:
										screenname = name.replace('#deactivated#', '')
									if screenname:
										line = line[:b + 1] + screenname + line[c:]
										source[idx] = line
								else:
									idxerr = True
									if idxerrcnt:
										idxerrtxt += '\n'
									idxerrcnt += 1
									idxerrtxt += '%d. name error - file: %s, line: %s, screen: %s (%s)' % (idxerrcnt, self.parts[pidx][0][1] + '.xml', self.screens[pidx][sidx][0], self.screens[pidx][sidx][1], name)
									break
							else:
								idxerr = True
								if idxerrcnt:
									idxerrtxt += '\n'
								idxerrcnt += 1
								idxerrtxt += '%d. index error - file: %s, line: %s, screen: %s' % (idxerrcnt, self.parts[pidx][0][1] + '.xml', self.screens[pidx][sidx][0], self.screens[pidx][sidx][1])
								break
						else:
							idxerr = True
							if idxerrcnt:
								idxerrtxt += '\n'
							idxerrcnt += 1
							idxerrtxt += '%d. file error - file: %s (index > lines)\n' % (sfile)
							break
						sidx += 1
					if not idxerr:
						f = open(tfile, 'w')
						f.writelines(source)
						f.close()
			else:
				if isfile(efile):
					remove(efile)
			if not idxerr and isfile(tfile) and isfile(sfile):
				copy(tfile, sfile)
				remove(tfile)
			pidx += 1

		if idxerrcnt:
			self.session.open(MessageBox, idxerrtxt, MessageBox.TYPE_ERROR)
			self.close()

		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()

		configfile.save()
		self.close()

	def defaults(self):
		for x in self["config"].list:
			if len(x) > 1:
				self.setInputToDefault(x[1])
				x[1].save()
		if self.session:
			self["config"].setList(self.getMenuItemList())
			self.ShowPicture()
		else:
			configfile.save()

	def setNewValue(self, configItem, newValue):
		configItem.setValue(newValue)

	def setInputToDefault(self, configItem):
		configItem.setValue(configItem.default)

	def showHelperText(self):
		cur = self["config"].getCurrent()
		if cur and len(cur) > 2 and cur[2] and cur[2] != _("helptext"):
			self["helpertext"].setText(cur[2])
		else:
			self["helpertext"].setText(" ")


class zoomPreview(Screen):
	x = getDesktop(0).size().width()
	y = getDesktop(0).size().height()
	skin = """<screen flags="wfNoBorder" position="0,0" size="%d,%d" title="zoomPreview" backgroundColor="#00000000">""" % (x, y)
	skin += """<widget name="preview" position="0,0" size="%d,%d" zPosition="1" alphatest="on" />""" % (x, y)
	skin += """</screen>"""

	def __init__(self, session, previewPic=None):
		self.skin = zoomPreview.skin
		Screen.__init__(self, session)
		self.session = session
		self.previewPic = previewPic
		self.PicLoad = ePicLoad()
		self["preview"] = Pixmap()
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"blue": self.close,
		}, -1)

		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def DecodePicture(self, PicInfo=""):
		ptr = self.PicLoad.getData()
		self["preview"].instance.setPixmap(ptr)

	def ShowPicture(self):
		self.PicLoad.setPara([self["preview"].instance.size().width(), self["preview"].instance.size().height(), 1, 1, 0, 1, "#00000000"])
		self.PicLoad.startDecode(self.previewPic)
