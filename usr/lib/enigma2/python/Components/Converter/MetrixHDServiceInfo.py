from enigma import eAVControl, iPlayableService, iServiceInformation

from Components.Converter.ServiceInfo import ServiceInfo
from Components.Element import cached


class MetrixHDServiceInfo(ServiceInfo):
	METRIX_VIDEO_INFO = 100

	def __init__(self, argument):
		ServiceInfo.__init__(self, argument if argument != "VideoInfo2" else "VideoInfo")
		if argument == "VideoInfo2":
			self.token = self.METRIX_VIDEO_INFO

	@cached
	def getText(self):
		if self.token == self.METRIX_VIDEO_INFO:
			service = self.source.service
			info = service and service.info()
			if info:
				videoData = info.getInfoString(iServiceInformation.sVideoInfo) or "-1|-1|-1|-1|-1|-1"
				videoData = [int(x) for x in videoData.split("|")]
				videoWidth = videoData[self.VIDEO_INFO_WIDTH] if videoData[self.VIDEO_INFO_WIDTH] != -1 else eAVControl.getInstance().getResolutionX(0)
				videoHeight = videoData[self.VIDEO_INFO_HEIGHT] if videoData[self.VIDEO_INFO_HEIGHT] != -1 else eAVControl.getInstance().getResolutionY(0)
				# videoAspect = videoData[self.VIDEO_INFO_ASPECT] if videoData[self.VIDEO_INFO_ASPECT] != -1 else eAVControl.getInstance().getAspect(0)
				videoGamma = videoData[self.VIDEO_INFO_GAMMA]

				# SD , HD , UHD, HDHDR, HDR, HDR10, HLG
				if videoWidth > 2160 and videoWidth <= 3840 and videoGamma == 1:
					return "4"
				if videoWidth > 2160 and videoWidth <= 3840 and videoGamma == 2:
					return "5"
				if videoWidth > 2160 and videoWidth <= 3840 and videoGamma == 3:
					return "6"
				if videoHeight > 1500 and videoWidth <= 3840 and videoGamma == 0:
					return "2"
				if videoHeight > 700 and videoHeight <= 1080 and videoGamma == 0:
					return "1"
				if videoHeight > 720 and videoHeight <= 1080 and videoGamma > 0:
					return "3"
				if videoHeight < 720:
					return "0"

			return ""

		result = ServiceInfo.getText(self)
		if result and self.token == self.VIDEO_INFORMATION:
			result = result.replace("Hz", "").replace(" ", "")
		return result

	text = property(getText)
