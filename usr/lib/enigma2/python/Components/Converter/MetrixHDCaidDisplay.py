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
from Components.Converter.Poll import Poll
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig
from Components.config import config
import six
initOtherConfig()


class MetrixHDCaidDisplay(Poll, Converter, object):
	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		self.type = type
		self.systemCaids = {
			"26": "BiSS",
			"01": "SEC",
			"06": "IRD",
			"17": "BET",
			"05": "VIA",
			"18": "NAG",
			"09": "NDS",
			"0B": "CON",
			"0D": "CRW",
			"4A": "DRE"}

		self.poll_interval = 1000
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
						caidlist[cs] = (self.systemCaids.get(cs), 0)
					for caid in caids:
						c = "%x" % int(caid)
						if len(c) == 3:
							c = "0%s" % c
						c = c[:2].upper()
						if c in self.systemCaids:
							caidlist[c] = (self.systemCaids.get(c), 1)
					ecm_info = self.ecmfile()
					if ecm_info:
						emu_caid = ecm_info.get("caid", "")
						if emu_caid and emu_caid != "0x000":
							c = emu_caid.lstrip("0x")
							if len(c) == 3:
								c = "0%s" % c
							c = c[:2].upper()
							caidlist[c] = (self.systemCaids.get(c), 2)
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
						'''# caid
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
						return textvalue'''

						show_reader = config.plugins.MyMetrixLiteOther.showExtended_reader.value
						if show_reader:
							typ = 'READER'
							oscsource = ecm_info.get("reader", None)
						else:
							typ = 'SOURCE'
							oscsource = ecm_info.get("from", None)
						if not oscsource:
							using = ecm_info.get("using", None)
							if not using:
								source = ecm_info.get("source", None)
								if not source:
									decode = ecm_info.get("decode", None)
									if not decode:
										return textvalue
						show_caid = config.plugins.MyMetrixLiteOther.showExtended_caid.value
						show_prov = config.plugins.MyMetrixLiteOther.showExtended_prov.value
						show_pid = config.plugins.MyMetrixLiteOther.showExtended_pid.value
						show_source = config.plugins.MyMetrixLiteOther.showExtended_source.value
						show_protocol = config.plugins.MyMetrixLiteOther.showExtended_protocol.value
						show_hops = config.plugins.MyMetrixLiteOther.showExtended_hops.value
						show_ecmtime = config.plugins.MyMetrixLiteOther.showExtended_ecmtime.value

						#caid or caid:prov - pid - address or oscsource or source or decode - protocol - hops - ecm time

						# caid
						caid = ""
						if show_caid:
							caid = ecm_info.get("caid", "####")
							caid = caid.lstrip("0x")
							caid = caid.upper()
							caid = caid.zfill(4)
							caid = "CAID: %s" % caid
						# hops
						hops = ""
						if show_hops:
							hops = ecm_info.get("hops", '#')
							if show_caid or show_source or ((show_pid or show_protocol) and oscsource):
								hops = " - HOPS: %s" % hops
							else:
								hops = "HOPS: %s" % hops
						# ecm time
						ecm_time = ""
						if show_ecmtime:
							ecm_time = ecm_info.get("ecm time", '#')
							if "msec" in ecm_time:
								ecm_time = "%s" % ecm_time
							else:
								ecm_time = "%ss" % ecm_time
							if show_caid or show_source or show_hops or ((show_pid or show_protocol) and oscsource):
								ecm_time = " - ECM: %s" % ecm_time
							else:
								ecm_time = "ECM: %s" % ecm_time

						# source
						# oscam
						if oscsource:
							if show_source:
								if show_caid or show_pid:
									oscsource = " - %s" % oscsource
								else:
									oscsource = "%s: %s" % (typ, oscsource)
							else:
								oscsource = ""
							pid = ""
							if show_pid:
								pid = ecm_info.get("pid", '####')
								pid = pid.lstrip("0x")
								pid = pid.upper()
								pid = pid.zfill(4)
								if show_caid:
									pid = " - PID: %s" % pid
								else:
									pid = "PID: %s" % pid
							# protocol
							protocol = ""
							if show_protocol:
								protocol = ecm_info.get("protocol", '#')
								if show_caid or show_pid:
									protocol = " - %s" % protocol
								else:
									protocol = "PROT: %s" % protocol
							# prov
							prov = ""
							if show_caid and show_prov:
								prov = ecm_info.get("prov", '######')
								prov = prov.lstrip("0x")
								prov = prov.upper()
								prov = prov.zfill(6)
								caid = "%s:%s" % (caid, prov)
							textvalue = "%s%s%s%s%s%s" % (caid, pid, oscsource, protocol, hops, ecm_time)
						# emu,cccam
						elif using:
							# address
							if show_source:
								address = ecm_info.get("address", '#')
								if show_caid:
									address = " - %s" % address
								else:
									address = "SOURCE: %s" % address
							else:
								address = ""
							if using == "emu":
								textvalue = "(EMU) %s%s" % (caid, ecm_time)
							elif using == "CCcam-s2s":
								textvalue = "(NET) %s%s%s%s" % (caid, address, hops, ecm_time)
							else:
								textvalue = "%s%s%s%s" % (caid, address, hops, ecm_time)
						# mgcamd
						elif source:
							if source == "emu":
								textvalue = "(EMU) %s" % (caid)
							else:
								if show_source:
									if show_caid:
										source = " - %s" % source
									else:
										source = "SOURCE: %s" % source
								else:
									source = ""
								textvalue = "%s%s%s" % (caid, source, ecm_time)
						# gbox
						elif decode:
							if decode == "Internal":
								textvalue = "(EMU) %s" % (caid)
							else:
								if show_source:
									if show_caid:
										decode = " - %s" % decode
									else:
										decode = "SOURCE: %s" % decode
								else:
									decode = ""
								textvalue = "%s%s" % (caid, decode)
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
					except:
						pass
			if ecm:
				for line in ecm:
					line = six.ensure_str(line)
					x = line.lower().find("msec")
					if x != -1:
						info["ecm time"] = line[0:x + 4]
					else:
						item = line.split(":", 1)
						if len(item) > 1:
							info[item[0].strip().lower()] = item[1].strip()
						else:
							if "caid" not in info:
								x = line.lower().find("caid")
								if x != -1:
									y = line.find(",")
									if y != -1:
										info["caid"] = line[x + 5:y]

		return info

	def changed(self, what):
		if (what[0] == self.CHANGED_SPECIFIC and what[1] == iPlayableService.evUpdatedInfo) or what[0] == self.CHANGED_POLL:
			Converter.changed(self, what)
