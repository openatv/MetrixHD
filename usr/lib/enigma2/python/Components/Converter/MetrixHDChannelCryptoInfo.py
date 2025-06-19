from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
from Tools.Hex2strColor import Hex2strColor
from skin import parseColor

import os
import six
ECM_INFO = '/tmp/ecm.info'
old_ecm_mtime = None
data = None

CAIDS = {
	"06": "I",
	"17": "B",
	"01": "S",
	"05": "V",
	"18": "N",
	"0D": "CW",
	"0B": "CO",
	"09": "ND",
	"4A": "CG",
}


class MetrixHDChannelCryptoInfo(Poll, Converter, object):
	IRDCRYPT = 0
	SECACRYPT = 1
	NAGRACRYPT = 2
	VIACRYPT = 3
	CONAXCRYPT = 4
	BETACRYPT = 5
	CRWCRYPT = 6
	NDSCRYPT = 7
	IRDECM = 8
	SECAECM = 9
	NAGRAECM = 10
	VIAECM = 11
	CONAXECM = 12
	BETAECM = 13
	CRWECM = 14
	NDSECM = 15
	CRYPTOGUARD = 16
	CRYPTOGUARDECM = 17
	FULL = 100

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2000
		self.poll_enabled = True

		tokens = type.split(",")
		type = tokens[0]

		self.color1 = r"\c00f0f0f0"
		self.color2 = r"\c00ffffff"
		if len(tokens) == 3:
			self.color1 = Hex2strColor(parseColor(tokens[1]).argb())
			self.color2 = Hex2strColor(parseColor(tokens[2]).argb())

		if type == 'IrdCrypt':
			self.type = self.IRDCRYPT
		elif type == 'SecaCrypt':
			self.type = self.SECACRYPT
		elif type == 'NagraCrypt':
			self.type = self.NAGRACRYPT
		elif type == 'ViaCrypt':
			self.type = self.VIACRYPT
		elif type == 'ConaxCrypt':
			self.type = self.CONAXCRYPT
		elif type == 'BetaCrypt':
			self.type = self.BETACRYPT
		elif type == 'CrwCrypt':
			self.type = self.CRWCRYPT
		elif type == 'NdsCrypt':
			self.type = self.NDSCRYPT
		elif type == 'IrdEcm':
			self.type = self.IRDECM
		elif type == 'SecaEcm':
			self.type = self.SECAECM
		elif type == 'NagraEcm':
			self.type = self.NAGRAECM
		elif type == 'ViaEcm':
			self.type = self.VIAECM
		elif type == 'ConaxEcm':
			self.type = self.CONAXECM
		elif type == 'BetaEcm':
			self.type = self.BETAECM
		elif type == 'CrwEcm':
			self.type = self.CRWECM
		elif type == 'NdsEcm':
			self.type = self.NDSECM
		elif type == 'CryptoGuardEcm':
			self.type = self.CRYPTOGUARDECM
		elif type == 'CryptoGuard':
			self.type = self.CRYPTOGUARD
		elif type == 'Full':
			self.type = self.FULL

	@cached
	def getText(self):
		if self.type == self.FULL:
			service = self.source.service
			info = service and service.info()
			if not info:
				return ""
			if info.getInfo(iServiceInformation.sIsCrypted) == 1:
				results = []
				currentcaid = self.getCaid()
				if not currentcaid:
					return ""
				searchcaids = info.getInfoObject(iServiceInformation.sCAIDs)
				caids = list(set([self.int2hex(caid)[:2] for caid in searchcaids if caid]))
				for caid in caids:
					color = self.color2 if currentcaid == caid else self.color1
					caid = CAIDS.get(caid)
					if caid:
						results.append(color + caid)
				return " ".join(results)
			else:
				self.poll_enabled = False
				return ""

	text = property(getText)

	@cached
	def getBoolean(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return False
		if info.getInfo(iServiceInformation.sIsCrypted) == 1:
			currentcaid = self.getCaid()
			searchcaids = info.getInfoObject(iServiceInformation.sCAIDs)
			if self.type == self.IRDCRYPT:
				caemm = self.getCrypt('06', searchcaids)
				return caemm
			if self.type == self.SECACRYPT:
				caemm = self.getCrypt('01', searchcaids)
				return caemm
			if self.type == self.NAGRACRYPT:
				caemm = self.getCrypt('18', searchcaids)
				return caemm
			if self.type == self.VIACRYPT:
				caemm = self.getCrypt('05', searchcaids)
				return caemm
			if self.type == self.CONAXCRYPT:
				caemm = self.getCrypt('0B', searchcaids)
				return caemm
			if self.type == self.BETACRYPT:
				caemm = self.getCrypt('17', searchcaids)
				return caemm
			if self.type == self.CRWCRYPT:
				caemm = self.getCrypt('0D', searchcaids)
				return caemm
			if self.type == self.NDSCRYPT:
				caemm = self.getCrypt('09', searchcaids)
				return caemm
			if self.type == self.CRYPTOGUARD:
				caemm = self.getCrypt('4A', searchcaids)
				return caemm
			if self.type == self.IRDECM:
				if currentcaid == '06':
					return True
			elif self.type == self.SECAECM:
				if currentcaid == '01':
					return True
			elif self.type == self.NAGRAECM:
				if currentcaid == '18':
					return True
			elif self.type == self.VIAECM:
				if currentcaid == '05':
					return True
			elif self.type == self.CONAXECM:
				if currentcaid == '0B':
					return True
			elif self.type == self.BETAECM:
				if currentcaid == '17':
					return True
			elif self.type == self.CRWECM:
				if currentcaid == '0D':
					return True
			elif self.type == self.NDSECM:
				if currentcaid == '09':
					return True
			elif self.type == self.CRYPTOGUARDECM:
				if currentcaid == '4A':
					return True
		else:
			self.poll_enabled = False
		return False

	boolean = property(getBoolean)

	def getCrypt(self, iscaid, caids):
		if caids and len(caids) > 0:
			for caid in caids:
				if self.int2hex(caid)[:2] == iscaid:
					return True

		return False

	def getCaid(self):
		global old_ecm_mtime
		global data
		try:
			ecm_mtime = os.stat(ECM_INFO).st_mtime
		except:
			ecm_mtime = None

		if ecm_mtime != old_ecm_mtime:
			old_ecm_mtime = ecm_mtime
			data = self.getCaidFromEcmInfo()
		return data

	def getCaidFromEcmInfo(self):
		try:
			ecm = open(ECM_INFO, 'rb').readlines()
			info = {}
			for line in ecm:
				line = six.ensure_str(line)
				d = line.split(':', 1)
				if len(d) > 1:
					info[d[0].strip()] = d[1].strip()

			caid = info.get('caid', '')
		except:
			caid = ''

		if caid:
			idx = caid.index('x')
			caid = caid[idx + 1:]
			if len(caid) == 3:
				caid = f'0{caid}'
			caid = caid[:2]
			caid = caid.upper()
		return caid

	def int2hex(self, value):
		return f'{value:04X}'

	def changed(self, what):
		Converter.changed(self, what)
