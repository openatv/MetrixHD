# -*- coding: UTF-8 -*-
#Embedded file name: /usr/lib/enigma2/python/Components/Converter/ServiceName2.py
from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceReference, eServiceCenter, eTimer
from Components.Element import cached
from Components.config import config
from Components.Converter.Poll import Poll
from six.moves import range
import six

SIGN = '°' if six.PY3 else str('\xc2\xb0')


class MetrixHDServiceName2(Poll, Converter, object):
	NAME = 0
	NUMBER = 1
	BOUQUET = 2
	PROVIDER = 3
	REFERENCE = 4
	ORBPOS = 5
	TPRDATA = 6
	SATELLITE = 7
	FORMAT = 8

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_enabled = True
		if type == 'Name' or not len(str(type)):
			self.type = self.NAME
		elif type == 'Number':
			self.type = self.NUMBER
		elif type == 'Bouquet':
			self.type = self.BOUQUET
		elif type == 'Provider':
			self.type = self.PROVIDER
		elif type == 'Reference':
			self.type = self.REFERENCE
		elif type == 'OrbitalPos':
			self.type = self.ORBPOS
		elif type == 'TpansponderInfo':
			self.type = self.TPRDATA
		elif type == 'Satellite':
			self.type = self.SATELLITE
		else:
			self.type = self.FORMAT
			self.sfmt = type[:]
		self.what = self.tpdata = None
		self.Timer = eTimer()
		self.Timer.callback.append(self.neededChange)

	def getServiceNumber(self, ref):

		def searchHelper(serviceHandler, num, bouquet):
			servicelist = serviceHandler.list(bouquet)
			if servicelist is not None:
				while True:
					s = servicelist.getNext()
					if not s.valid():
						break
					if not s.flags & (eServiceReference.isMarker | eServiceReference.isDirectory):
						num += 1
						if s == ref:
							return (s, num)

			return (None, num)

		if isinstance(ref, eServiceReference):
			isRadioService = ref.getData(0) in (2, 10)
			lastpath = isRadioService and config.radio.lastroot.value or config.tv.lastroot.value
			if lastpath.find('FROM BOUQUET') == -1:
				if 'FROM PROVIDERS' in lastpath:
					return ('P', 'Provider')
				if 'FROM SATELLITES' in lastpath:
					return ('S', 'Satellites')
				if ') ORDER BY name' in lastpath:
					return ('A', 'All Services')
				return (0, 'N/A')
			try:
				acount = config.plugins.NumberZapExt.enable.value and config.plugins.NumberZapExt.acount.value
			except:
				acount = False

			rootstr = ''
			for x in lastpath.split(';'):
				if x != '':
					rootstr = x

			serviceHandler = eServiceCenter.getInstance()
			if acount is True or not config.usage.multibouquet.value:
				bouquet = eServiceReference(rootstr)
				service, number = searchHelper(serviceHandler, 0, bouquet)
			else:
				if isRadioService:
					bqrootstr = '1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
				else:
					bqrootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
				number = 0
				cur = eServiceReference(rootstr)
				bouquet = eServiceReference(bqrootstr)
				bouquetlist = serviceHandler.list(bouquet)
				if bouquetlist is not None:
					while True:
						bouquet = bouquetlist.getNext()
						if not bouquet.valid():
							break
						if bouquet.flags & eServiceReference.isDirectory:
							service, number = searchHelper(serviceHandler, number, bouquet)
							if service is not None and cur == bouquet:
								break

			if service is not None:
				info = serviceHandler.info(bouquet)
				name = info and info.getName(bouquet) or ''
				return (number, name)
		return (0, '')

	def getProviderName(self, ref):
		if isinstance(ref, eServiceReference):
			from Screens.ChannelSelection import service_types_radio, service_types_tv
			typestr = ref.getData(0) in (2, 10) and service_types_radio or service_types_tv
			pos = typestr.rfind(':')
			rootstr = '%s (channelID == %08x%04x%04x) && %s FROM PROVIDERS ORDER BY name' % (typestr[:pos + 1],
			 ref.getUnsignedData(4),
			 ref.getUnsignedData(2),
			 ref.getUnsignedData(3),
			 typestr[pos + 1:])
			provider_root = eServiceReference(rootstr)
			serviceHandler = eServiceCenter.getInstance()
			providerlist = serviceHandler.list(provider_root)
			if providerlist is not None:
				while True:
					provider = providerlist.getNext()
					if not provider.valid():
						break
					if provider.flags & eServiceReference.isDirectory:
						servicelist = serviceHandler.list(provider)
						if servicelist is not None:
							while True:
								service = servicelist.getNext()
								if not service.valid():
									break
								if service == ref:
									info = serviceHandler.info(provider)
									return info and info.getName(provider) or 'Unknown'

		return 'N/A'

	def getTransponderInfo(self, info, ref, fmt):
		result = ''
		if self.tpdata is None:
			self.tpdata = ref and (info.getInfoObject(ref, iServiceInformation.sTransponderData) or -1) or info.getInfoObject(iServiceInformation.sTransponderData)
			if not isinstance(self.tpdata, dict):
				self.tpdata = None
				return result
		type = self.tpdata.get('tuner_type', '')
		if fmt == '' or fmt == '%T':
			if type == 'DVB-C':
				fmt = '%t %F %Y %i %f %M'
			elif type == 'DVB-T':
				fmt = '%t %F %h %m %g %c'
			else:
				fmt = '%O %F%p %Y %f'
		while True:
			pos = fmt.find('%')
			if pos == -1:
				result += fmt
				break
			result += fmt[:pos]
			pos += 1
			l = len(fmt)
			f = pos < l and fmt[pos] or '%'
			if f == 't':
				if type == 'DVB-S':
					result += _('Satellite')
				elif type == 'DVB-C':
					result += _('Cable')
				elif type == 'DVB-T':
					result += _('Terrestrial')
				else:
					result += 'N/A'
			elif f == 's':
				if type == 'DVB-S':
					x = self.tpdata.get('system', 0)
					result += x in range(2) and {0: 'DVB-S',
					 1: 'DVB-S2'}[x] or ''
				else:
					result += type
			elif f == 'F':
				result += '%d' % (self.tpdata.get('frequency', 0) / 1000)
			elif f == 'f':
				if type in ('DVB-S', 'DVB-C'):
					x = self.tpdata.get('fec_inner', 15)
					result += x in list(range(10)) + [15] and {0: 'Auto',
					 1: '1/2',
					 2: '2/3',
					 3: '3/4',
					 4: '5/6',
					 5: '7/8',
					 6: '8/9',
					 7: '3/5',
					 8: '4/5',
					 9: '9/10',
					 15: 'None'}[x] or ''
				elif type == 'DVB-T':
					x = self.tpdata.get('code_rate_lp', 5)
					result += x in list(range(6)) and {0: '1/2',
					 1: '2/3',
					 2: '3/4',
					 3: '5/6',
					 4: '7/8',
					 5: 'Auto'}[x] or ''
			elif f == 'i':
				x = self.tpdata.get('inversion', 2)
				result += x in list(range(3)) and {0: 'On',
				 1: 'Off',
				 2: 'Auto'}[x] or ''
			elif f == 'O':
				if type == 'DVB-S':
					x = self.tpdata.get('orbital_position', 0)
					result += x > 1800 and '%d.%d' + SIGN + 'W' % ((3600 - x) / 10, (3600 - x) % 10) or '%d.%d' + SIGN + 'E' % (x / 10, x % 10)
			elif f == 'M':
				x = self.tpdata.get('modulation', 1)
				if type == 'DVB-S':
					result += x in list(range(4)) and {0: 'Auto',
					 1: 'QPSK',
					 2: '8PSK',
					 3: 'QAM16'}[x] or ''
				elif type == 'DVB-C':
					result += x in list(range(6)) and {0: 'Auto',
					 1: 'QAM16',
					 2: 'QAM32',
					 3: 'QAM64',
					 4: 'QAM128',
					 5: 'QAM256'}[x] or ''
			elif f == 'p':
				if type == 'DVB-S':
					x = self.tpdata.get('polarization', 0)
					result += x in list(range(4)) and {0: 'H',
					 1: 'V',
					 2: 'L',
					 3: 'R'}[x] or '?'
			elif f == 'Y':
				if type in ('DVB-S', 'DVB-C'):
					result += '%d' % (self.tpdata.get('symbol_rate', 0) / 1000)
			elif f == 'r':
				x = self.tpdata.get('rolloff')
				if x is not None:
					result += x in list(range(3)) and {0: '0.35',
					 1: '0.25',
					 2: '0.20'}[x] or ''
			elif f == 'o':
				x = self.tpdata.get('pilot')
				if x is not None:
					result += x in list(range(3)) and {0: 'Off',
					 1: 'On',
					 2: 'Auto'}[x] or ''
			elif f == 'c':
				if type == 'DVB-T':
					x = self.tpdata.get('constellation', 3)
					result += x in list(range(4)) and {0: 'QPSK',
					 1: 'QAM16',
					 2: 'QAM64',
					 3: 'Auto'}[x] or ''
			elif f == 'l':
				if type == 'DVB-T':
					x = self.tpdata.get('code_rate_lp', 5)
					result += x in list(range(6)) and {0: '1/2',
					 1: '2/3',
					 2: '3/4',
					 3: '5/6',
					 4: '7/8',
					 5: 'Auto'}[x] or ''
			elif f == 'h':
				if type == 'DVB-T':
					x = self.tpdata.get('code_rate_hp', 5)
					result += x in list(range(6)) and {0: '1/2',
					 1: '2/3',
					 2: '3/4',
					 3: '5/6',
					 4: '7/8',
					 5: 'Auto'}[x] or ''
			elif f == 'm':
				if type == 'DVB-T':
					x = self.tpdata.get('transmission_mode', 2)
					result += x in list(range(3)) and {0: '2k',
					 1: '8k',
					 2: 'Auto'}[x] or ''
			elif f == 'g':
				if type == 'DVB-T':
					x = self.tpdata.get('guard_interval', 4)
					result += x in list(range(5)) and {0: '1/32',
					 1: '1/16',
					 2: '1/8',
					 3: '1/4',
					 4: 'Auto'}[x] or ''
			elif f == 'b':
				if type == 'DVB-T':
					x = self.tpdata.get('bandwidth', 1)
					result += x in list(range(4)) and {0: '8 MHz',
					 1: '7 MHz',
					 2: '6 MHz',
					 3: 'Auto'}[x] or ''
			elif f == 'e':
				if type == 'DVB-T':
					x = self.tpdata.get('hierarchy_information', 4)
					result += x in list(range(5)) and {0: 'None',
					 1: '1',
					 2: '2',
					 3: '4',
					 4: 'Auto'}[x] or ''
			else:
				result += f
			if pos + 1 >= l:
				break
			fmt = fmt[pos + 1:]

		return result

	def getSatelliteName(self, ref):
		name = 'N/A'
		if isinstance(ref, eServiceReference):
			orbpos = ref.getUnsignedData(4) >> 16
			if orbpos == 65535:
				name = _('Cable')
			elif orbpos == 61166:
				name = _('Terrestrial')
			else:
				orbpos = ref.getData(4) >> 16
				if orbpos < 0:
					orbpos += 3600
				try:
					from Components.NimManager import nimmanager
					name = str(nimmanager.getSatDescription(orbpos))
				except:
					name = orbpos > 1800 and '%d.%d' + SIGN + 'W' % ((3600 - orbpos) / 10, (3600 - orbpos) % 10) or '%d.%d' + SIGN + 'E' % (orbpos / 10, orbpos % 10)

		return name

	@cached
	def getText(self):
		service = self.source.service
		if isinstance(service, iPlayableServicePtr):
			info = service and service.info()
			ref = None
		else:
			info = service and self.source.info
			ref = service
		self.poll_enabled = False
		if info is None:
			return ''
		if self.type == self.NAME:
			name = ref and (info.getName(ref) or 'N/A') or info.getName() or 'N/A'
			return name.replace('\xc2\x86', '').replace('\xc2\x87', '').replace('\x86', '').replace('\x87', '')
		if self.type == self.NUMBER:
			num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
			return num and str(num) or ''
		if self.type == self.BOUQUET:
			num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
			return bouq
		if self.type == self.PROVIDER:
			return ref and self.getProviderName(ref) or info.getInfoString(iServiceInformation.sProvider)
		if self.type == self.REFERENCE:
			return ref and ref.toString() or info.getInfoString(iServiceInformation.sServiceref)
		if self.type == self.ORBPOS:
			return self.getTransponderInfo(info, ref, '%O')
		if self.type == self.TPRDATA:
			return self.getTransponderInfo(info, ref, '%T')
		if self.type == self.SATELLITE:
			return self.getSatelliteName(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
		if self.type == self.FORMAT:
			ret = num = bouq = ''
			if '%n' in self.sfmt or '%B' in self.sfmt:
				num, bouq = self.getServiceNumber(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
			tmp = self.sfmt[:]
			while True:
				pos = tmp.find('%')
				if pos == -1:
					ret += tmp
					break
				ret += tmp[:pos]
				pos += 1
				l = len(tmp)
				f = pos < l and tmp[pos] or '%'
				if f == 'N':
					name = ref and (info.getName(ref) or 'N/A') or info.getName() or 'N/A'
					ret += name.replace('\xc2\x86', '').replace('\xc2\x87', '')
				elif f == 'n':
					ret += num and str(num) or ''
				elif f == 'B':
					ret += bouq
				elif f == 'P':
					ret += ref and self.getProviderName(ref) or info.getInfoString(iServiceInformation.sProvider)
				elif f == 'R':
					ret += ref and ref.toString() or info.getInfoString(iServiceInformation.sServiceref)
				elif f == 'S':
					ret += self.getSatelliteName(ref or eServiceReference(info.getInfoString(iServiceInformation.sServiceref)))
				elif f in 'TtsFfiOMpYroclhmgbe':
					ret += self.getTransponderInfo(info, ref, '%' + f)
				else:
					ret += f
				if pos + 1 >= l:
					break
				tmp = tmp[pos + 1:]

			return '%s' % ret.replace('N/A', '')

	text = property(getText)

	def neededChange(self):
		if self.what:
			Converter.changed(self, self.what)
			self.what = None

	def changed(self, what):
		if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
			self.tpdata = None
			if self.type in (self.NUMBER, self.BOUQUET) or self.type == self.FORMAT and ('%n' in self.sfmt or '%B' in self.sfmt):
				self.what = what
				self.Timer.start(200, True)
			else:
				Converter.changed(self, what)
