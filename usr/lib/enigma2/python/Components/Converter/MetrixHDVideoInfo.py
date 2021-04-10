# -*- coding: UTF-8 -*-
##
## Example usage in the skin.xml:
##		<widget source="session.CurrentService" render="Label" position="164,435" size="390,28" font="Regular;26" transparent="1" >
##			<convert type="MetrixHDVideoInfo">VideoMode</convert>
##		</widget>
##
from __future__ import print_function, division
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eServiceCenter, eServiceReference, iServiceInformation
from Components.Converter.Poll import Poll

##########################################################################


class MetrixHDVideoInfo(Poll, Converter, object):

	VIDEOMODE = 0
	VIDEOSIZE = 1
	VIDEOSIZEWIDTH = 3
	VIDEOSIZEHEIGHT = 4
	VIDEOSIZESHORT = 5
	VIDEOCODEC = 6
	VIDEOFORMAT = 7

	ALL = 10

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2000
		self.poll_enabled = True

		if type == "VideoMode":
			self.type = self.VIDEOMODE
		elif type == "VideoSize":
			self.type = self.VIDEOSIZE
		elif type == "VideoSizeWidth":
			self.type = self.VIDEOSIZEWIDTH
		elif type == "VideoSizeHeight":
			self.type = self.VIDEOSIZEHEIGHT
		elif type == "VideoSizeShort":
			self.type = self.VIDEOSIZESHORT
		elif type == "VideoCodec":
			self.type = self.VIDEOCODEC
		elif type == "VideoFormat":
			self.type = self.VIDEOFORMAT
		else:
			self.type = self.ALL

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""

		text = ""
		width = info.getInfo(iServiceInformation.sVideoWidth)
		height = info.getInfo(iServiceInformation.sVideoHeight)

		if self.type == self.VIDEOMODE:
			if width > 0 and height > 0:
				f = open("/proc/stb/video/videomode")
				text = f.read()[:-1].replace('\n', '')
				f.close()
		elif self.type == self.VIDEOSIZE:
			if width > 0 and height > 0:
				sProgressive = info.getInfo(iServiceInformation.sProgressive)
				text = "%dx%d" % (width, height)
				#text += ("i", "p", " ")[sProgressive]
				if sProgressive:
					text += "p" + str((info.getInfo(iServiceInformation.sFrameRate) + 499) // 1000)
				else:
					text += "i" + str((info.getInfo(iServiceInformation.sFrameRate) + 499) // 500)
		elif self.type == self.VIDEOSIZEWIDTH:
			if width > 0:
				text = "%d" % (width)
		elif self.type == self.VIDEOSIZEHEIGHT:
			if height > 0:
				sProgressive = info.getInfo(iServiceInformation.sProgressive)
				text = "%d" % (height)
				#text += ("i", "p", " ")[sProgressive]
				if sProgressive:
					text += "p" + str((info.getInfo(iServiceInformation.sFrameRate) + 499) // 1000)
				else:
					text += "i" + str((info.getInfo(iServiceInformation.sFrameRate) + 499) // 500)
		elif self.type == self.VIDEOSIZESHORT:
			if width > 0 and height > 0:
				text = "%dx%d" % (width, height)
		elif self.type == self.VIDEOCODEC:
			from Components.Converter.PliExtraInfo import codec_data
			text = codec_data.get(self.info.getInfo(iServiceInformation.sVideoType), "N/A")
		elif self.type == self.VIDEOFORMAT:
			if width > 0 and height > 0:
				text = info.getInfo(iServiceInformation.sAspect)
				if text == -2:
					text = info.getInfoString(iServiceInformation.sAspect)
				elif text == -1:
					text = _("N/A")
				if text in (1, 2, 5, 6, 9, 0xA, 0xD, 0xE):
					text = "4:3"
				else:
					text = "16:9"
		else:
			print("type must be {VideoMode, VideoSize, VideoSizeWidth, VideoSizeHeight, VideoSizeShort, VideoCodec, VideoFormat} for MetrixHDVideoInfo converter")
			text = "type-error"

		return text

	text = property(getText)
