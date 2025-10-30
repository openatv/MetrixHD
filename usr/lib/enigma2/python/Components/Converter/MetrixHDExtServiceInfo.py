# -*- coding: UTF-8 -*-
##
## Extended Service-Info Converter
## by AliAbdul
##
## Example usage in the skin.xml:
##		<widget source="session.CurrentService" render="Label" position="164,435" size="390,28" font="Regular;26" transparent="1" >
##			<convert type="MetrixHDExtServiceInfo">Config</convert>
##		</widget>
##
## Known issues with the ServiceNumber Converter:
## If you have one service in different bouquets the first index of the service will be taken
## If you rename, move, delete or add a channel the numbers will not be OK any more. You have to restart E2 then
##
from Components.config import config
from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import iServiceInformation
from xml.etree.cElementTree import parse

##########################################################################


class MetrixHDExtServiceInfo(Converter):
	SERVICENAME = 0
	SERVICENUMBER = 1
	SERVICENUMBERANDNAME = 2
	ORBITALPOSITION = 3
	SATNAME = 4
	PROVIDER = 5
	FROMCONFIG = 6
	ALL = 7

	def __init__(self, type):
		Converter.__init__(self, type)
		self.satNames = {}
		if type == "ServiceName":
			self.type = self.SERVICENAME
		elif type == "ServiceNumber":
			self.type = self.SERVICENUMBER
		elif type == "ServiceNumberAndName":
			self.type = self.SERVICENUMBERANDNAME
		elif type == "OrbitalPosition":
			self.type = self.ORBITALPOSITION
		elif type == "SatName":
			self.readSatXml()
			self.type = self.SATNAME
		elif type == "Provider":
			self.type = self.PROVIDER
		elif type == "Config":
			self.readSatXml()
			self.type = self.FROMCONFIG
		else:
			self.type = self.ALL

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""

		text = ""
		name = info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\x86', '').replace('\x87', '')
		try:
			service = self.source.serviceref
			num = service and service.getChannelNum() or None
		except Exception:
			num = None
		number = str(num) if num is not None else ""
		orbital = self.getOrbitalPosition(info)

		if len(number) > 5:
			number = ""
		if self.type == self.SERVICENAME:
			text = name
		elif self.type == self.SERVICENUMBER:
			text = number
		elif self.type == self.SERVICENUMBERANDNAME:
			text = f"{number} {name}"
		elif self.type == self.ORBITALPOSITION:
			text = orbital
		elif self.type == self.SATNAME:
			satName = self.satNames.get(orbital, orbital)
			text = satName
		elif self.type == self.PROVIDER:
			text = info.getInfoString(iServiceInformation.sProvider)
		elif self.type == self.FROMCONFIG:
			satName = self.satNames.get(orbital, orbital)
			if config.plugins.ExtendedServiceInfo.showServiceNumber.value is True and number != "":
				text = f"{number}. {name}"
			else:
				text = name
			if config.plugins.ExtendedServiceInfo.showOrbitalPosition.value is True and orbital != "":
				if config.plugins.ExtendedServiceInfo.orbitalPositionType.value == "name":
					text = f"{text} ({satName})"
				else:
					text = f"{text} ({orbital})"
		else:
			text = name if number == "" else f"{number} {name}"
			if orbital != "":
				text = f"{text} ({orbital})"

		return text

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)

	def readSatXml(self):
		try:
			satXml = parse("/etc/enigma2/satellites.xml").getroot()
		except Exception:
			satXml = parse("/etc/tuxbox/satellites.xml").getroot()
		if satXml is not None:
			for sat in satXml.findall("sat"):
				name = sat.get("name") or None
				position = sat.get("position") or None
				if name is not None and position is not None:
					position = f"{position[:-1]}.{position[-1:]}"
					if position.startswith("-"):
						position = f"{position[1:]}W"
					else:
						position = f"{position}E"
					if position.startswith("."):
						position = f"0{position}"
					self.satNames[position] = name

	def getOrbitalPosition(self, info):
		transponderData = info.getInfoObject(iServiceInformation.sTransponderData)
		if transponderData is not None:
			if isinstance(transponderData, float):
				return ""
			if "tuner_type" in transponderData:
				if (transponderData["tuner_type"] == "DVB-S") or (transponderData["tuner_type"] == "DVB-S2"):
					orbital = transponderData["orbital_position"]
					orbital = int(orbital)
					return str((float(3600 - orbital)) / 10.0) + "W" if orbital > 1800 else str((float(orbital)) / 10.0) + "E"
		return ""
