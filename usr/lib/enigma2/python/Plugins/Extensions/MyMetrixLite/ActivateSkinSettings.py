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

from . import _, initColorsConfig, initWeatherConfig, initOtherConfig, initFontsConfig, getTunerPositionList, appendSkinFile, \
	SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP, \
	SKIN_TEMPLATES_SOURCE, SKIN_TEMPLATES_TARGET, SKIN_TEMPLATES_TARGET_TMP, \
	SKIN_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP, \
	SKIN_SECOND_INFOBAR_SOURCE, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP, \
	SKIN_SECOND_INFOBAR_ECM_SOURCE, SKIN_SECOND_INFOBAR_ECM_TARGET, SKIN_SECOND_INFOBAR_ECM_TARGET_TMP, \
	SKIN_INFOBAR_LITE_SOURCE, SKIN_INFOBAR_LITE_TARGET, SKIN_INFOBAR_LITE_TARGET_TMP, \
	SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP, \
	SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP, \
	SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP, \
	SKIN_OPENVISION_SOURCE, SKIN_OPENVISION_TARGET, SKIN_OPENVISION_TARGET_TMP, \
	SKIN_PLUGINS_SOURCE, SKIN_PLUGINS_TARGET, SKIN_PLUGINS_TARGET_TMP, \
	SKIN_UNCHECKED_SOURCE, SKIN_UNCHECKED_TARGET, SKIN_UNCHECKED_TARGET_TMP, \
	SKIN_DESIGN_SOURCE, SKIN_DESIGN_TARGET, SKIN_DESIGN_TARGET_TMP

from Components.config import config, configfile
from Components.NimManager import nimmanager
from shutil import move, copy, rmtree, copytree
from enigma import getDesktop, getBoxType
from os import path, remove, statvfs, listdir, system, mkdir
from PIL import Image, ImageFont, ImageDraw
import math

#############################################################

class ActivateSkinSettings:

	def __init__(self):
		self.ErrorCode = None
		self.ButtonEffect = None

	def WriteSkin(self, silent=False):
		#silent = True  -> returned int value for defined error code
		#silent = False -> tuple returned -> ident, message

		#error codes for silent mode 
		#(called from SystemPlugins/SoftwareManager/BackupRestore.py after restore settings and from skin.py after flash a new image (fast restore function))
		#0:"No Error"
		#1:"Unknown Error creating Skin. Please check after reboot MyMetrixLite-Plugin and apply your settings."
		#2:"Error creating HD-Skin. Not enough flash memory free."
		#3:"Error creating FullHD-Skin. Not enough flash memory free. Using HD-Skin!"
		#4:"Error creating FullHD-Skin. Icon package download not available. Using HD-Skin!"
		#5:"Error creating FullHD-Skin. Using HD-Skin!"
		#6:"Some FullHD-Icons are missing. Using HD-Icons!"
		#7:"Error, unknown Result!"

		self.silent = silent
		if self.silent:
			self.E2settings = open("/etc/enigma2/settings", "r").read()
			if config.skin.primary_skin.value != "MetrixHD/skin.MySkin.xml" and not 'config.skin.primary_skin=MetrixHD/skin.MySkin.xml' in self.E2settings:
				print 'MetrixHD is not the primary skin or runs with default settings. No restore action needed!'
				return 0
			from Components.PluginComponent import plugins #need for fast restore in skin.py
		self.initConfigs()
		self.CheckSettings()
		if self.ErrorCode is None:
			if self.silent:
				self.ErrorCode = 7
			else:
				self.ErrorCode = 'unknown', _('Error, unknown Result!')
		return self.ErrorCode

	def initConfigs(self):
		initOtherConfig()
		initColorsConfig()
		initWeatherConfig()
		initFontsConfig()

	def RefreshIcons(self,restore=False):
		# called from SystemPlugins/SoftwareManager/plugin.py after software update and from Screens/SkinSelector.py after changing skin
		self.initConfigs()
		self.getEHDSettings()
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

	def getEHDSettings(self, onlyCheck=False):
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
			self.EHDenabled = False
			self.EHDfactor = 1
			self.EHDres = 'HD'
			self.EHDtxt = 'Standard HD'
			if onlyCheck or not self.silent:
				self.ErrorCode = 'checkEHDsettings', _("Your enhanced hd settings are inconsistent. Please check this.")

	def CheckSettings(self, onlyCheck=False):
		#first check is ehd tested, ehd-settings and available ehd-icons
		self.getEHDSettings(onlyCheck)

		if self.EHDenabled:
			self.service_name = 'enigma2-plugin-skins-metrix-vision-%s-icons' % self.EHDres.lower()
			if system('/usr/bin/opkg list-installed ' + self.service_name + ' | grep ' + self.service_name):
				if onlyCheck or not self.silent:
					self.ErrorCode = 'checkEHDsettings', _("Your enhanced hd settings are inconsistent. Please check this.")
				elif self.silent:
					stat = statvfs("/usr/share/enigma2/MetrixHD/")
					freeflash = stat.f_bavail * stat.f_bsize / 1024 / 1024
					filesize = 10
					if self.EHDres == 'UHD':
						filesize = 25
					if freeflash < filesize:
						self.ErrorCode = 3
					else:
						system('/usr/bin/opkg update')
						ret = str(system('/usr/bin/opkg install ' + self.service_name))
						if 'Unknown package' in ret or "Collected errors" in ret:
							self.ErrorCode = 4
					if self.ErrorCode:
						self.EHDenabled = False
						self.EHDfactor = 1
						self.EHDres = 'HD'
						self.EHDtxt = 'Standard HD'

		if onlyCheck or self.ErrorCode:
			return self.ErrorCode
		self.applyChanges()

	def applyChanges(self):
		print"MyMetrixLite apply Changes"

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

			skinfiles = [(SKIN_SOURCE, SKIN_TARGET, SKIN_TARGET_TMP),
						(SKIN_TEMPLATES_SOURCE, SKIN_TEMPLATES_TARGET, SKIN_TEMPLATES_TARGET_TMP),
						(SKIN_INFOBAR_SOURCE, SKIN_INFOBAR_TARGET, SKIN_INFOBAR_TARGET_TMP),
						(SKIN_SECOND_INFOBAR_SOURCE, SKIN_SECOND_INFOBAR_TARGET, SKIN_SECOND_INFOBAR_TARGET_TMP),
						(SKIN_SECOND_INFOBAR_ECM_SOURCE, SKIN_SECOND_INFOBAR_ECM_TARGET, SKIN_SECOND_INFOBAR_ECM_TARGET_TMP),
						(SKIN_INFOBAR_LITE_SOURCE, SKIN_INFOBAR_LITE_TARGET, SKIN_INFOBAR_LITE_TARGET_TMP),
						(SKIN_CHANNEL_SELECTION_SOURCE, SKIN_CHANNEL_SELECTION_TARGET, SKIN_CHANNEL_SELECTION_TARGET_TMP),
						(SKIN_MOVIEPLAYER_SOURCE, SKIN_MOVIEPLAYER_TARGET, SKIN_MOVIEPLAYER_TARGET_TMP),
						(SKIN_EMC_SOURCE, SKIN_EMC_TARGET, SKIN_EMC_TARGET_TMP),
						(SKIN_OPENVISION_SOURCE, SKIN_OPENVISION_TARGET, SKIN_OPENVISION_TARGET_TMP),
						(SKIN_PLUGINS_SOURCE, SKIN_PLUGINS_TARGET, SKIN_PLUGINS_TARGET_TMP),
						(SKIN_UNCHECKED_SOURCE, SKIN_UNCHECKED_TARGET, SKIN_UNCHECKED_TARGET_TMP),
						(SKIN_DESIGN_SOURCE, SKIN_DESIGN_TARGET, SKIN_DESIGN_TARGET_TMP)]
			buttons = [
						('info.png', _('INFO')),
						('key_audio.png', _('AUDIO')),
						('key_av.png', _('AV')),
						('key_bouquet.png', _('BOUQUET')),
						('key_end.png', _('END')),
						('key_epg.png', _('EPG')),
						('key_exit.png', _('EXIT')),
						('key_help.png', _('HELP')),
						('key_home.png', _('HOME')),
						('key_leftright.png', _('< >')),
						('key_tv.png', _('TV')),
						('key_updown.png', _('< >')),
						('menu.png', _('MENU')),
						('ok.png', _('OK')),
						('text.png', _('TEXT'))
						]
			buttonpath = {'HD':'/usr/share/enigma2/MetrixHD/buttons/', 'FHD':'/usr/share/enigma2/MetrixHD/FHD/buttons/', 'UHD':'/usr/share/enigma2/MetrixHD/UHD/buttons/'}

			################
			# check free flash for _TARGET and _TMP files 
			################

			stat = statvfs("/usr/share/enigma2/MetrixHD/")
			freeflash = stat.f_bavail * stat.f_bsize / 1024

			filesize = 0
			for file in skinfiles:
				if path.exists(file[1]):
					filesize += path.getsize(file[1])
				else:
					if path.exists(file[0]):
						filesize += path.getsize(file[0]) * 2

			reserve = 256
			filesize = filesize/1024 + reserve 

			if freeflash < filesize:
				self.ErrorCode = 2
				if not self.silent:
					self.ErrorCode = 'ErrorCode_2', _("Not enough free flash memory to create the new %s skin files. ( %d kb is required )") % (self.EHDtxt, filesize)
				return

			################
			# InfoBar
			################

			infobarSkinSearchAndReplace = []

			if config.plugins.MyMetrixLiteOther.showTunerinfo.getValue() is True:
				if config.plugins.MyMetrixLiteOther.setTunerAuto.getValue() is False:
					infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-X" />', '<panel name="INFOBARTUNERINFO-%s" />' % config.plugins.MyMetrixLiteOther.setTunerManual.getValue()])
				#else:
				#    infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-X" />', '<panel name="INFOBARTUNERINFO-%d" />' % self.getTunerCount()])
			else:
				infobarSkinSearchAndReplace.append(['<panel name="INFOBARTUNERINFO-X" />', '']) 

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
			else:
				moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_2" />', '<panel name="MoviePlayer_%s" />'  %(config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.value)])
				if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "3":
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
				moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_2_time" />', '<panel name="MoviePlayer_' + config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() + '_time" />' ])
			else:
				moviePlayerSkinSearchAndReplace.append(['<panel name="MoviePlayer_2_time" />', '' ])

			if config.plugins.MyMetrixLiteOther.showMovieListScrollbar.value:
				moviePlayerSkinSearchAndReplace.append(['scrollbarMode="showNever"', 'scrollbarMode="showOnDemand"'])

			if config.plugins.MyMetrixLiteOther.showMovieListRunningtext.value:
				delay = str(config.plugins.MyMetrixLiteOther.runningTextStartdelay.value)
				speed = str(config.plugins.MyMetrixLiteOther.runningTextSpeed.value)
				moviePlayerSkinSearchAndReplace.append(['movetype=none,startdelay=600,steptime=60', 'movetype=running,startdelay=%s,steptime=%s' %(delay,speed)])

			if config.plugins.MyMetrixLiteOther.movielistStyle.value == 'right':
				moviePlayerSkinSearchAndReplace.append(['<panel name="MovieSelection_left"/>', '<panel name="MovieSelection_right"/>' ])

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
					if config.plugins.MyMetrixLiteOther.showMovieName.value:
						EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenterCover_no" />', '<panel name="EMCMediaCenterCover_small_infobar" />'])
					else:
						EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenterCover_no" />', '<panel name="EMCMediaCenterCover_large_infobar" />'])
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

			posNR = config.plugins.MyMetrixLiteOther.showEMCSelectionPicon.value == 'right'
			progress = False
			if not self.silent:
				try:
					config.EMC.skin_able.setValue(True)
					config.EMC.use_orig_skin.setValue(False)
					config.EMC.movie_cover.setValue(config.plugins.MyMetrixLiteOther.showEMCSelectionCover.value != 'no')
					config.EMC.movie_picons.setValue(config.plugins.MyMetrixLiteOther.showEMCSelectionPicon.value != 'no')
					config.EMC.save()
					progress = 'P' in config.EMC.movie_progress.value
				except:
					print "Error: find emc config - it's not installed ?"
			else:
				progress = "config.EMC.movie_progress=P" in self.E2settings or not "config.EMC.movie_progress=" in self.E2settings

			sizeW = 700
			sizeH = 480
			gap = 5
			margin = 2
			scale = config.plugins.MyMetrixLiteFonts.epgtext_scale.value / 95.0 # 95% standard scale
			if config.plugins.MyMetrixLiteOther.showMovieListScrollbar.value:
				sizeW -= margin + config.plugins.MyMetrixLiteOther.SkinDesignScrollbarSliderWidth.value + config.plugins.MyMetrixLiteOther.SkinDesignScrollbarBorderWidth.value*2 # place for scrollbar
				EMCSkinSearchAndReplace.append(['scrollbarMode="showNever"', 'scrollbarMode="showOnDemand"' ])

			if config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "+8":
				itemHeight = 20
				rowfactor = itemHeight / 30.0
				offsetHicon = 0
				offsetPosIcon = 6
				offsetHbar = -2
			elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "+6":
				sizeH = 484
				itemHeight = 22
				rowfactor = itemHeight / 30.0
				offsetHicon = 0
				offsetPosIcon = 4
				offsetHbar = -2
			elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "+4":
				itemHeight = 24
				rowfactor = itemHeight / 30.0
				offsetHicon = 0
				offsetPosIcon = 2
				offsetHbar = -2
			elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "+2":
				sizeH = 486
				itemHeight = 27
				rowfactor = itemHeight / 30.0
				offsetPosIcon = 0
				offsetHicon = 1
				offsetHbar = -1
			elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "-2":
				sizeH = 476
				itemHeight = 34
				rowfactor = itemHeight / 30.0
				offsetHicon = 1
				offsetPosIcon = 0
				offsetHbar = 1
			elif config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value == "-4":
				itemHeight = 40
				rowfactor = itemHeight / 30.0
				offsetPosIcon = 0
				offsetHicon = 3
				offsetHbar = 4
			else:
				itemHeight = 30
				rowfactor = 1
				offsetPosIcon = 0
				offsetHicon = 0
				offsetHbar = 0

			#font
			CoolFont = int(20 * rowfactor)
			CoolSelectFont = int(20 * rowfactor)
			CoolDateFont = int(20 * rowfactor)
			#height
			CoolBarSizeV = int(10 * rowfactor)
			CoolPiconHPos = 2
			CoolPiconHeight = itemHeight - CoolPiconHPos * 2
			CoolIconHPos = 2 + offsetHicon
			CoolBarHPos = 12 + offsetHbar
			CoolMovieHPos = 2 + offsetHicon
			CoolDateHPos = 2 + offsetHicon
			CoolProgressHPos = 2 + offsetHicon
			#width
			if progress:
				CoolBarSizeH = int(config.plugins.MyMetrixLiteOther.setEMCbarsize.value)
			else:
				CoolBarSizeH = 0
			CoolDateWidth = int(int(config.plugins.MyMetrixLiteOther.setEMCdatesize.value) * scale * rowfactor)
			CoolPiconWidth = int(CoolPiconHeight * 1.73)
			CoolCSDirInfoWidth = int(int(config.plugins.MyMetrixLiteOther.setEMCdirinfosize.value) * scale * rowfactor)
			CoolFolderSize = sizeW - CoolCSDirInfoWidth - gap - margin - 38 # 38 is progressbar position
			if not CoolCSDirInfoWidth:
				CoolFolderSize = sizeW - 35# - margin
			CoolMoviePos = 38 + CoolBarSizeH  + gap
			#if not CoolBarSizeH:
			#    CoolMoviePos = 38
			CoolMovieSize = sizeW - CoolDateWidth - CoolMoviePos - gap - margin
			if not CoolDateWidth:
				CoolMovieSize = sizeW - CoolMoviePos# - margin
			CoolMoviePiconSize = CoolMovieSize - CoolPiconWidth - gap
			CoolDatePos = sizeW - CoolDateWidth - margin
			CoolCSPos = sizeW - CoolCSDirInfoWidth - margin
			CoolIconPos = 4 + offsetPosIcon

			EMCSkinSearchAndReplace.append(['size="700,480" itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;20" CoolDateFont="epg_text;20"'\
											,'size="700,%s" itemHeight="%s" CoolFont="epg_text;%s" CoolSelectFont="epg_text;%s" CoolDateFont="epg_text;%s"' %(sizeH, itemHeight, CoolFont, CoolSelectFont, CoolDateFont) ])

			EMCSkinSearchAndReplace.append(['size="700,240" itemHeight="30" CoolFont="epg_text;20" CoolSelectFont="epg_text;20" CoolDateFont="epg_text;20"'\
											,'size="700,%s" itemHeight="%s" CoolFont="epg_text;%s" CoolSelectFont="epg_text;%s" CoolDateFont="epg_text;%s"' %(sizeH/2, itemHeight, CoolFont, CoolSelectFont, CoolDateFont) ])

			EMCSkinSearchAndReplace.append(['CoolProgressHPos="2" CoolIconPos="4" CoolIconHPos="2" CoolIconSize="26,26" CoolBarPos="35" CoolBarHPos="12" CoolBarSize="50,10" CoolBarSizeSa="50,10" CoolMoviePos="90"'\
											,'CoolProgressHPos="%s" CoolIconPos="%s" CoolIconHPos="%s" CoolIconSize="26,26" CoolBarPos="35" CoolBarHPos="%s" CoolBarSize="%s,%s" CoolBarSizeSa="%s,%s" CoolMoviePos="%s"' %(CoolProgressHPos, CoolIconPos, CoolIconHPos, CoolBarHPos, CoolBarSizeH, CoolBarSizeV, CoolBarSizeH, CoolBarSizeV, CoolMoviePos - margin) ])

			CoolMoviePiconPos = CoolMoviePos + CoolPiconWidth + gap - margin
			CoolPiconPos = CoolMoviePos - margin
			EMCSkinSearchAndReplace.append(['CoolMovieHPos="2" CoolMovieSize="494" CoolFolderSize="475" CoolDatePos="592" CoolDateHPos="2" CoolDateWidth="104" CoolPiconPos="90" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="140" CoolMoviePiconSize="445" CoolCSWidth="140" CoolDirInfoWidth="140" CoolCSPos="555"'\
											,'CoolMovieHPos="%s" CoolMovieSize="%s" CoolFolderSize="%s" CoolDatePos="%s" CoolDateHPos="%s" CoolDateWidth="%s" CoolPiconPos="%s" CoolPiconHPos="%s" CoolPiconWidth="%s" CoolPiconHeight="%s" CoolMoviePiconPos="%s" CoolMoviePiconSize="%s" CoolCSWidth="%s" CoolDirInfoWidth="%s" CoolCSPos="%s"' %(CoolMovieHPos, CoolMovieSize, CoolFolderSize, CoolDatePos, CoolDateHPos, CoolDateWidth, CoolPiconPos, CoolPiconHPos, CoolPiconWidth, CoolPiconHeight, CoolMoviePiconPos, CoolMoviePiconSize, CoolCSDirInfoWidth, CoolCSDirInfoWidth, CoolCSPos) ])

			CoolMoviePiconPos = CoolMoviePos - margin
			CoolPiconPos = CoolDatePos - CoolPiconWidth - gap - margin
			if not CoolDateWidth:
				CoolPiconPos = CoolDatePos - CoolPiconWidth
			EMCSkinSearchAndReplace.append(['CoolMovieHPos="2" CoolMovieSize="494" CoolFolderSize="475" CoolDatePos="592" CoolDateHPos="2" CoolDateWidth="104" CoolPiconPos="540" CoolPiconHPos="2" CoolPiconWidth="45" CoolPiconHeight="26" CoolMoviePiconPos="90" CoolMoviePiconSize="445" CoolCSWidth="140" CoolDirInfoWidth="140" CoolCSPos="555"'\
											,'CoolMovieHPos="%s" CoolMovieSize="%s" CoolFolderSize="%s" CoolDatePos="%s" CoolDateHPos="%s" CoolDateWidth="%s" CoolPiconPos="%s" CoolPiconHPos="%s" CoolPiconWidth="%s" CoolPiconHeight="%s" CoolMoviePiconPos="%s" CoolMoviePiconSize="%s" CoolCSWidth="%s" CoolDirInfoWidth="%s" CoolCSPos="%s"' %(CoolMovieHPos, CoolMovieSize, CoolFolderSize, CoolDatePos, CoolDateHPos, CoolDateWidth, CoolPiconPos, CoolPiconHPos, CoolPiconWidth, CoolPiconHeight, CoolMoviePiconPos, CoolMoviePiconSize, CoolCSDirInfoWidth, CoolCSDirInfoWidth, CoolCSPos) ])

			if posNR:
				EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionList_picon_left" />', '<panel name="EMCSelectionList_picon_right" />'])
				EMCSkinSearchAndReplace.append(['<panel name="EMCSelectionList_large_description_picon_left" />', '<panel name="EMCSelectionList_large_description_picon_right" />'])

			namepos = "30,465"
			if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "2":
				if config.plugins.MyMetrixLiteOther.showMoviePlayerResolutionExtended.getValue() is True:
					EMCSkinSearchAndReplace.append(['<panel name="RESOLUTIONMOVIEPLAYER" />', '<panel name="RESOLUTIONMOVIEPLAYER-2" />' ])
			else:
				EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_2" />', '<panel name="EMCMediaCenter_%s" />' %(config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.value)])
				if config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() == "3": 
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
				EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_2_time" />', '<panel name="EMCMediaCenter_' + config.plugins.MyMetrixLiteOther.InfoBarMoviePlayerDesign.getValue() + '_time" />' ])
			else:
				EMCSkinSearchAndReplace.append(['<panel name="EMCMediaCenter_2_time" />', '' ])

			EMCSkinSearchAndReplace.append(['WatchingColor="#D8C100"', 'WatchingColor="#' + config.plugins.MyMetrixLiteColors.emcWatchingColor.value + '"' ])
			EMCSkinSearchAndReplace.append(['FinishedColor="#5FA816"', 'FinishedColor="#' + config.plugins.MyMetrixLiteColors.emcFinishedColor.value + '"' ])
			EMCSkinSearchAndReplace.append(['RecordingColor="#E51400"', 'RecordingColor="#' + config.plugins.MyMetrixLiteColors.emcRecordingColor.value + '"' ])

			if config.plugins.MyMetrixLiteColors.emcCoolHighlightColor.getValue() is False:
				EMCSkinSearchAndReplace.append(['CoolHighlightColor="1"', 'CoolHighlightColor="0"' ])

			if config.plugins.MyMetrixLiteOther.showMovieListRunningtext.value:
				delay = str(config.plugins.MyMetrixLiteOther.runningTextStartdelay.value)
				speed = str(config.plugins.MyMetrixLiteOther.runningTextSpeed.value)
				EMCSkinSearchAndReplace.append(['movetype=none,startdelay=600,steptime=60', 'movetype=running,startdelay=%s,steptime=%s' %(delay,speed)])

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

			if config.plugins.MyMetrixLiteOther.showChannelListScrollbar.value:
				mode = "showOnDemand"
			else:
				mode = "showNever"
			margin = str(config.plugins.MyMetrixLiteOther.setFieldMargin.value)
			distance = str(config.plugins.MyMetrixLiteOther.setItemDistance.value)
			DESIGNSkinSearchAndReplace.append(['scrollbarMode="showNever" fieldMargins="5" itemsDistances="5"', 'scrollbarMode="%s" fieldMargins="%s" itemsDistances="%s"' %(mode,margin,distance)])

			delay = config.plugins.MyMetrixLiteOther.runningTextStartdelay.value
			speed = config.plugins.MyMetrixLiteOther.runningTextSpeed.value
			if config.plugins.MyMetrixLiteOther.showChannelListRunningtext.value:
				DESIGNSkinSearchAndReplace.append(['movetype=none,startdelay=600,steptime=60', 'movetype=running,startdelay=%s,steptime=%s' %(delay,speed)]) #event description
			if config.plugins.MyMetrixLiteOther.showInfoBarRunningtext.value:
				DESIGNSkinSearchAndReplace.append(['movetype=none,startdelay=900,steptime=1,step=3', 'movetype=running,startdelay=%s,steptime=1,step=%s' %(int(delay*1.5),speed/20)]) #infobar

			#show menu buttons
			if not config.plugins.MyMetrixLiteOther.SkinDesignMenuButtons.value:
				DESIGNSkinSearchAndReplace.append(['<panel name="MenuButtons_template"/>', '<!--panel name="MenuButtons_template"/-->' ])

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
			channelselectionprogress = ('name="layer-a-channelselection-progressbar" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionprogress.value + '"')
			channelselectionprogressborder = ('name="layer-a-channelselection-progressbarborder" value="#00' + config.plugins.MyMetrixLiteColors.channelselectionprogressborder.value + '"')
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
			epgprimetimeforeground = ('name="epg-primetime-foreground" value="#00' + config.plugins.MyMetrixLiteColors.epgprimetimeforeground.value + '"')
			epgprimetimebackground = ('name="epg-primetime-background" value="#' + config.plugins.MyMetrixLiteColors.epgprimetimebackgroundtransparency.value + config.plugins.MyMetrixLiteColors.epgprimetimebackground.value + '"')
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
			scrollbarSlidercolor = ('name="scrollbarSlidercolor" value="#' + config.plugins.MyMetrixLiteColors.scrollbarSlidertransparency.value + config.plugins.MyMetrixLiteColors.scrollbarSlidercolor.value + '"')
			scrollbarSliderbordercolor = ('name="scrollbarSliderbordercolor" value="#' + config.plugins.MyMetrixLiteColors.scrollbarSliderbordertransparency.value + config.plugins.MyMetrixLiteColors.scrollbarSliderbordercolor.value + '"')

			skinSearchAndReplace = []
			orgskinSearchAndReplace = [] # needed for some attributes (e.g. borderset setting was lost after using plugin media portal - because restored settings from skin.xml and not from skin.MySkin.xml)
			skinSearchAndReplace.append(['<!-- original file -->',''])
			orgskinSearchAndReplace.append(['<!-- original file -->','<!-- !!!copied and changed file!!! -->'])

			skinSearchAndReplace.append(['name="layer-a-channelselection-foreground" value="#00FFFFFF"', channelselectionservice ])
			skinSearchAndReplace.append(['name="layer-a-channelselection-foregroundColorSelected" value="#00FFFFFF"', channelselectionserviceselected ])
			skinSearchAndReplace.append(['name="layer-a-channelselection-foreground-ServiceDescription" value="#00BDBDBD"', channelselectionservicedescription ])
			skinSearchAndReplace.append(['name="layer-a-channelselection-progressbar" value="#00BDBDBD"', channelselectionprogress ])
			skinSearchAndReplace.append(['name="layer-a-channelselection-progressbarborder" value="#00BDBDBD"', channelselectionprogressborder ])
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
			skinSearchAndReplace.append(['name="epg-primetime-foreground" value="#00008A00"', epgprimetimeforeground ])
			skinSearchAndReplace.append(['name="epg-primetime-background" value="#1A0F0F0F"', epgprimetimebackground ])
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
			skinSearchAndReplace.append(['name="scrollbarSlidercolor" value="#00FFFFFF"', scrollbarSlidercolor ])
			skinSearchAndReplace.append(['name="scrollbarSliderbordercolor" value="#0027408B"', scrollbarSliderbordercolor ])

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
			old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_button" scale="90" />'
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
				new = '<font filename="' + type + '" name="global_large_screen" scale="0" />'
				skinSearchAndReplace.append([old, new ])
			elif config.plugins.MyMetrixLiteOther.SkinDesignShowLargeText.value == "screens":
				old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
				new = '<font filename="' + type + '" name="global_large_menu" scale="0" />'
				skinSearchAndReplace.append([old, new ])
				old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
				new = '<font filename="' + type + '" name="global_large_screen" scale="' + str(scale) + '" />'
				skinSearchAndReplace.append([old, new ])
			else:
				old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_menu" scale="100" />'
				new = '<font filename="' + type + '" name="global_large_menu" scale="0" />'
				skinSearchAndReplace.append([old, new ])
				old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf" name="global_large_screen" scale="100" />'
				new = '<font filename="' + type + '" name="global_large_screen" scale="0" />'
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
			old = '<font filename="/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf" name="epg_event" scale="95" />'
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

			#skinfiles
			skinSearchAndReplace.append(['skin_00_templates.xml', 'skin_00_templates.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00a_InfoBar.xml', 'skin_00a_InfoBar.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00b_SecondInfoBar.xml', 'skin_00b_SecondInfoBar.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00c_SecondInfoBarECM.xml', 'skin_00c_SecondInfoBarECM.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00d_InfoBarLite.xml', 'skin_00d_InfoBarLite.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00e_ChannelSelection.xml', 'skin_00e_ChannelSelection.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00f_MoviePlayer.xml', 'skin_00f_MoviePlayer.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00g_EMC.xml', 'skin_00g_EMC.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00o_openvision.xml', 'skin_00o_openvision.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00p_plugins.xml', 'skin_00p_plugins.MySkin.xml'])
			skinSearchAndReplace.append(['skin_00u_unchecked.xml', 'skin_00u_unchecked.MySkin.xml'])
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
						TARGETpath = skinpartdir + skinpart + '/' + skinpart + '.MySkin.xml'
						TMPpath = skinpartdir + skinpart + '/' + skinpart + '.MySkin.xml.tmp'
						#remove old MySkin files
						if path.isfile(TARGETpath):
							remove(TARGETpath)
					if file == 'enabled':
						enabled = True
				if partname and enabled:
					if skinparts:
						skinparts += '\n\t<include filename="%s" />' %TARGETpath
					else:
						skinparts = '<include filename="%s" />' %TARGETpath
					skinfiles.append((partpath, TARGETpath, TMPpath))

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
			# Buttons
			################

			if config.plugins.MyMetrixLiteOther.SkinDesignButtons.value:
				#backup
				for button in buttons:
					buttonfile = buttonpath[self.EHDres]+button[0]
					buttonbackupfile = buttonfile + '.backup'
					if path.exists(buttonfile) and not path.exists(buttonbackupfile):
						copy(buttonfile,buttonbackupfile)
					self.makeButtons(buttonfile,button[1])
				self.ButtonEffect = None
			else:
				#restore
				for button in buttons:
					buttonfile = buttonpath[self.EHDres]+button[0]
					buttonbackupfile = buttonfile + '.backup'
					if path.exists(buttonbackupfile):
						move(buttonbackupfile,buttonfile)

			################
			# EHD-skin + ALL-skin files
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
			print "--------   option%s   --------" % self.EHDres
			for file in skinfiles:
				if self.skinline_error:
					break
				if path.exists(file[2]):
					self.optionEHD(file[2],file[1])
				else:
					self.optionEHD(file[0],file[1])
				#additional files
				if False and self.EHDenabled and self.EHD_addfiles: #deactivated
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

			#remove old _TMP files
			for file in skinfiles:
				if path.exists(file[2]):
					remove(file[2])
				if self.skinline_error:
					copy(file[0],file[1])

			if self.skinline_error:
				self.ErrorCode = 5
				plustext = plustext + _("Error creating %s skin. HD skin is used!\n\n") % self.EHDres
			elif not self.skinline_error and self.pixmap_error:
				self.ErrorCode = 6
				plustext = plustext + _("One or more %s icons are missing. Using HD icons for this.\n\n") % self.EHDres

			text = plustext + _("GUI needs a restart to apply a new skin.\nDo you want to Restart the GUI now?")

			if not self.ErrorCode:
				self.ErrorCode = 0
			if not self.silent:
				self.ErrorCode = 'reboot', text

			config.skin.primary_skin.setValue("MetrixHD/skin.MySkin.xml")

		except Exception as error:
			print '[ActivateSkinSettings]', error
			self.ErrorCode = 1
			if not self.silent:
				self.ErrorCode = 'error', _("Error creating Skin!")

			#restore skinfiles
			if path.exists(SKIN_SOURCE + bname):
				 move(SKIN_SOURCE + bname,SKIN_SOURCE)
			for file in skinfiles:
				if path.exists(file[1]):
					remove(file[1])
				if path.exists(file[2]):
					remove(file[2])
			#retore buttons
			for button in buttons:
				buttonfile = buttonpath["HD"]+button[0]
				buttonbackupfile = buttonfile + '.backup'
				if path.exists(buttonbackupfile):
					move(buttonbackupfile,buttonfile)
			#retore icons
			self.iconFileCopy("HD")
			self.iconFolderCopy("HD")

			config.skin.primary_skin.setValue("MetrixHD/skin.xml")

		config.skin.primary_skin.save()
		configfile.save()

	def makeButtons(self, button, text):
		try:
			#makeButtons
			self.getEHDSettings()

			sizex = int(80*self.EHDfactor)
			sizey = int(40*self.EHDfactor)
			framesize = config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameSize.value
			fonttyp = config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextFont.value
			fontsize = int(config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextSize.value*self.EHDfactor)

			color = config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColor.value
			trans = config.plugins.MyMetrixLiteOther.SkinDesignButtonsFrameColorTransparency.value
			framecolor = rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), 255-int(trans,16))
			color = config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColor.value
			trans = config.plugins.MyMetrixLiteOther.SkinDesignButtonsBackColorTransparency.value
			backcolor = rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), 255-int(trans,16))
			color = config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColor.value
			trans = config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextColorTransparency.value
			textcolor = rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), 255-int(trans,16))
			color = config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectColor.value
			trans = config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectIntensity.value
			glossycolor = rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), int(trans,16))

			#symbols
			symbolpos = 0
			if 'key_leftright.png' in button or 'key_updown.png' in button:
				unicodechar = 'setrixHD' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextFont.value or 'Raleway' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextFont.value
				if unicodechar:
					symbolpos = -2
					fonttyp = '/usr/share/enigma2/MetrixHD/fonts/setrixHD.ttf'
					fontsize += int(fontsize/2)
					if 'key_leftright.png' in button:
						text = u'\u02c2'+' '+u'\u02c3'
					else:
						text = u'\u02c4'+' '+u'\u02c5'
				else:
					symbolpos = 0
					fonttyp = '/usr/share/enigma2/MetrixHD/fonts/OpenSans-Regular.ttf'
					fontsize += int(fontsize/2)
			else:
				text = u'%s' %text
			#autoshrink text
			x = 0
			fontx = sizex + 1
			while fontx > sizex:
				font = ImageFont.truetype(fonttyp, fontsize-x)
				fontx, fonty = font.getsize(text)
				x += 1
			#frame
			img = Image.new("RGBA",(sizex, sizey), framecolor)
			draw = ImageDraw.Draw(img)
			#button
			draw.rectangle(((framesize, framesize), (sizex-framesize-1, sizey-framesize-1)),fill=backcolor)
			#text
			imgtxt = Image.new("RGBA",(sizex, sizey), (textcolor[0],textcolor[1],textcolor[2],0))
			drawtxt = ImageDraw.Draw(imgtxt)
			drawtxt.text((int((sizex-fontx)/2), int((sizey-fonty)/2)+ symbolpos + config.plugins.MyMetrixLiteOther.SkinDesignButtonsTextPosition.value), text, fill=textcolor, font=font)
			#rotate updown
			if 'key_updown.png' in button and not unicodechar: #rotation disabled - if using unicode charachters
				top = int(font.getsize('<')[0]/2)-1
				lefta = int((sizex-fontx)/2)
				righta = lefta + font.getsize('<')[0]
				leftb = lefta + fontx - font.getsize('<')[0]
				rightb = leftb + font.getsize('<')[0]
				upper = int((sizey - fonty + font.getsize('<')[1])/2) - top
				lower = upper + font.getsize('<')[0]
				imga = imgtxt.crop((lefta,upper,righta,lower)).rotate(-90)
				imgb = imgtxt.crop((leftb,upper,rightb,lower)).rotate(-90)
				drawtxt.rectangle(((0, 0), (sizex, sizey)),fill=(textcolor[0],textcolor[1],textcolor[2],0))
				imgtxt.paste(imga,(lefta,top+1))
				imgtxt.paste(imgb,(leftb,top+1))
			#text under glossy
			if config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectOverText.value:
				img.paste(imgtxt,(0,0),imgtxt)
			#glossy effect
			if config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value != 'no':
				if 'frame' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value:
					fs = 0
					sy = sizey
					sx = sizex
				else:
					fs = framesize
					sy = sizey - fs*2
					sx = sizex - fs*2
				if not self.ButtonEffect:
					a = glossycolor[3]
					esy = sy*float(config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectSize.value)
					if 'solid' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value:
						imga = Image.new("RGBA",(sizex-fs*2, int(esy)), glossycolor)
					elif 'gradient' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value:
						imga = Image.new("RGBA",(sizex-fs*2, int(esy)), (glossycolor[0],glossycolor[1],glossycolor[2],0))
						draw = ImageDraw.Draw(imga)
						s = a/esy
						for l in range(0,int(esy+1)):
							draw.line([(0,l), (sizex-fs*2,l)], fill=(glossycolor[0],glossycolor[1],glossycolor[2],int(a)))
							a-=s
					elif 'circle' in config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffect.value:
						epx = sx*float(config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosX.value)
						epy = sy*float(config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectPosY.value)
						esx = sx*float(config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectSize.value)
						imga = Image.new("RGBA",(sx, sy))
						for y in range(sy):
							for x in range(sx):
								s = a*(float(math.sqrt((x - epx) ** 2 + (y - epy) ** 2)) / math.sqrt((esx ** 2) + (esy ** 2)))
								imga.putpixel((x, y), (glossycolor[0],glossycolor[1],glossycolor[2],a-int(s)))
					self.ButtonEffect = imga
				img.paste(self.ButtonEffect,(fs,fs),self.ButtonEffect)
			#text over glossy
			if not config.plugins.MyMetrixLiteOther.SkinDesignButtonsGlossyEffectOverText.value:
				img.paste(imgtxt,(0,0),imgtxt)
			img.save(button)
			return 1
		except:
			return 0

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
		# ibts background
		color = config.plugins.MyMetrixLiteColors.layerabackground.value
		alpha = config.plugins.MyMetrixLiteColors.layerabackgroundtransparency.value
		cgfile = "/usr/share/enigma2/MetrixHD/ibts/background.png"
		self.makeColorField(cgfile, int(1280*factor), int(32*factor), color, alpha)

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

	def makeColorField(self, name, sizex, sizey, color, alpha):
		rgba = (int(color[-6:][:2],16), int(color[-4:][:2],16), int(color[-2:][:2],16), 255 - int(alpha,16))
		imga = Image.new("RGBA",(sizex, sizey), rgba)
		imga.save(name)

	def iconFileCopy(self, target):

		#skin root
		spath = "/usr/share/enigma2/MetrixHD/%s/copy/" % self.EHDres
		dpath = "/usr/share/enigma2/MetrixHD/"
		self.FileCopy(target, spath, dpath)

		#skin icons
		spath = "/usr/share/enigma2/MetrixHD/%s/copy/icons/" % self.EHDres
		dpath = "/usr/share/enigma2/MetrixHD/icons/"
		self.FileCopy(target, spath, dpath)

		#skin countries
		spath = "/usr/share/enigma2/MetrixHD/%s/copy/countries/" % self.EHDres
		dpath = "/usr/share/enigma2/MetrixHD/countries/"
		if not path.exists(dpath):
			mkdir(dpath)
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

		#plugin Infobar Tunerstate
		spath = "/usr/share/enigma2/MetrixHD/%s/copy/ibts/" % self.EHDres
		dpath = "/usr/share/enigma2/MetrixHD/ibts/"
		self.FileCopy(target,spath,dpath)

		#plugin EnhancedMovieCenter
		spath = "/usr/share/enigma2/MetrixHD/%s/copy/emc/" % self.EHDres
		dpath = "/usr/share/enigma2/MetrixHD/emc/"
		if int(config.plugins.MyMetrixLiteOther.showEMCSelectionRows.value) > 3:
			if self.EHDres == "FHD":
				self.FileCopy('HD',spath,dpath)
			elif self.EHDres == "UHD" and path.exists("/usr/share/enigma2/MetrixHD/FHD/copy/emc/"):
				self.FileCopy('FHD',"/usr/share/enigma2/MetrixHD/FHD/copy/emc/",dpath)
		else:
			self.FileCopy(target,spath,dpath)

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
		tunerCount = min(8, tunerCount)

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
#options for all skin files
			line = line.replace('scrollbarWidth="10"', 'scrollbarWidth="%s"' %(config.plugins.MyMetrixLiteOther.SkinDesignScrollbarSliderWidth.value + config.plugins.MyMetrixLiteOther.SkinDesignScrollbarBorderWidth.value*2))
			line = line.replace('scrollbarSliderBorderWidth="1"', 'scrollbarSliderBorderWidth="%s"' %config.plugins.MyMetrixLiteOther.SkinDesignScrollbarBorderWidth.value)
			if config.plugins.MyMetrixLiteColors.backgroundtextborderwidth.value and ' font="global_large' in line and not ' borderWidth=' in line and not ' borderColor=' in line:
				line = line.replace(' font=', ' borderWidth="%s" borderColor="#%s%s" font=' %(config.plugins.MyMetrixLiteColors.backgroundtextborderwidth.value, config.plugins.MyMetrixLiteColors.backgroundtextbordertransparency.value, config.plugins.MyMetrixLiteColors.backgroundtextbordercolor.value))
#options for all skin files end
			if self.EHDenabled:
				try: 
#start additional files
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
							if 'Font' in line:
								parcount = len(line[n2:n12+1].split(';'))
							else:
								parcount = len(line[n2:n12+1].split(','))
							strnew = ""
							if parcount == 1:
								p1 = int(round(float(int(line[(n2+1):n12])*FACT),r_par))
								strnew = 'value="%d"' %(p1)
							elif parcount == 2:
								if 'Font' in line:
									n3 = line.find(';', n2) 
									p1 = line[(n2+1):n3]
									p2 = int(f_offset + round(float(int(line[(n3+1):n12])*FFACT),r_par))
									strnew = 'value="%s;%d"' %(p1,p2)
								else:
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
#TimeFontVertical="epg_event;22" EventFontVertical="epg_event;18"
						if 'FontVertical=' in line and not ' Cool' in line and fontsize >= 2:
							s = 0
							n3 = 0
							for s in range(0,line.count('FontVertical="')):
								n1 = line.find('FontVertical="', n3)
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
						if 'scale="' in line and not 'scale="0"' in line and fontsize != 2:
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
#progressbarBorderWidth="1" -> deactivated (channel list)
						#if 'progressbarBorderWidth="' in line:
						#	n1 = line.find('progressbarBorderWidth="', 0)
						#	n2 = line.find('"', n1)
						#	n3 = line.find('"', n2+1) 
						#	y = line[(n2+1):n3]

						#	ynew = str(int(round(float(int(y)*FACT),r_par)))
						#	strnew = line[n1:n2+1] + ynew + '"'
						#	line = line[:n1] + strnew + line[(n3+1):]
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
#CoolCSPos"590"
							if 'CoolCSPos="' in line:
								n1 = line.find('CoolCSPos=', 0)
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

