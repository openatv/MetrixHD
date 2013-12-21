#
#  CaidDisplay - Converter
#
#  Coded by Dr.Best & weazle (c) 2010
#  Support: www.dreambox-tools.info
#
#  This plugin is licensed under the Creative Commons 
#  Attribution-NonCommercial-ShareAlike 3.0 Unported 
#  License. To view a copy of this license, visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed and executed on hardware which
#  is licensed by Dream Multimedia GmbH.
#
#  This plugin is NOT free software. It is open source, you are allowed to
#  modify it (if you keep the license), but it may not be commercially 
#  distributed other than under the conditions noted above.
#

from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService
from Components.Element import cached
from Poll import Poll

class MetrixHDCaidDisplay(Poll, Converter, object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.type = type
		self.systemCaids = {
			"26" : "BiSS",
			"01" : "SEC",
			"06" : "IRD",
			"17" : "BET",
			"05" : "VIA",
			"18" : "NAG",
			"09" : "NDS",
			"0B" : "CON",
			"0D" : "CRW",
			"4A" : "DRE" }

		self.poll_interval = 2000
		self.poll_enabled = True

	@cached
	def get_caidlist(self):
		caidlist = {}
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				caids = info.getInfoObject(iServiceInformation.sCAIDs)
				if caids:
					for cs in self.systemCaids:
						caidlist[cs] = (self.systemCaids.get(cs),0)
					for caid in caids:
						c = "%x" % int(caid)
						if len(c) == 3:
							c = "0%s" % c
						c = c[:2].upper()
						if self.systemCaids.has_key(c):
							caidlist[c] = (self.systemCaids.get(c),1)
					ecm_info = self.ecmfile()
					if ecm_info:
						emu_caid = ecm_info.get("caid", "")
						if emu_caid and emu_caid != "0x000":
							c = emu_caid.lstrip("0x")
							if len(c) == 3:
								c = "0%s" % c
							c = c[:2].upper()
							caidlist[c] = (self.systemCaids.get(c),2)
		return caidlist

	getCaidlist = property(get_caidlist)

	@cached
	def getText(self):
		textvalue = ""
		service = self.source.service
		if service:
			info = service and service.info()
			if info:
				if info.getInfoObject(iServiceInformation.sCAIDs):
					ecm_info = self.ecmfile()
					if ecm_info:
						# caid
						caid = ecm_info.get("caid", "")
						caid = caid.lstrip("0x")
						caid = caid.upper()
						caid = caid.zfill(4)
						caid = "CAID: %s" % caid
						# hops
						hops = ecm_info.get("hops", None)
						hops = "HOPS: %s" % hops
						# ecm time	
						ecm_time = ecm_info.get("ecm time", None)
						if ecm_time:
							if "msec" in ecm_time:
								ecm_time = "ECM: %s " % ecm_time
							else:
								ecm_time = "ECM: %s s" % ecm_time
						# address
						address = ecm_info.get("address", "")
						# source
						using = ecm_info.get("using", "")
						if using:
							if using == "emu":
								textvalue = "(EMU) %s - %s" % (caid, ecm_time)
							elif using == "CCcam-s2s":
								textvalue = "(NET) %s - %s - %s - %s" % (caid, address, hops, ecm_time)
							else:
								textvalue = "%s - %s - %s - %s" % (caid, address, hops, ecm_time)
						else:
							# mgcamd
							source = ecm_info.get("source", None)
							if source:
								if source == "emu":
									textvalue = "(EMU) %s" % (caid)
								else:
									textvalue = "%s - %s - %s" % (caid, source, ecm_time)
							# oscam
							oscsource = ecm_info.get("from", None)
							if oscsource:
								textvalue = "%s - %s - %s - %s" % (caid, oscsource, hops, ecm_time)
							# gbox
							decode = ecm_info.get("decode", None)
							if decode:
								if decode == "Internal":
									textvalue = "(EMU) %s" % (caid)
								else:
									textvalue = "%s - %s" % (caid, decode)
		return textvalue 

	text = property(getText)

	def ecmfile(self):
		ecm = None
		info = {}
		service = self.source.service
		if service:
			frontendInfo = service.frontendInfo()
			if frontendInfo:
				try:
					ecmpath = "/tmp/ecm%s.info" % frontendInfo.getAll(False).get("tuner_number")
					ecm = open(ecmpath, "rb").readlines()
				except:
					try:
						ecm = open("/tmp/ecm.info", "rb").readlines()
					except: pass
			if ecm:
				for line in ecm:
					x = line.lower().find("msec")
					if x != -1:
						info["ecm time"] = line[0:x+4]
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if not info.has_key("caid"):
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x+5:y]

		return info

	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)
