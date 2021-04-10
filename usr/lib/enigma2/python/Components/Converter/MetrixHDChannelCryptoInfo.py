from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.Converter.Poll import Poll
import os
import six
ECM_INFO = '/tmp/ecm.info'
old_ecm_mtime = None
data = None


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

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.poll_interval = 2000
		self.poll_enabled = True
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
		else:
			self.poll_enabled = False
		return False

	boolean = property(getBoolean)

	def getCrypt(self, iscaid, caids):
		if caids and len(caids) > 0:
			for caid in caids:
				caid = self.int2hex(caid)
				if len(caid) == 3:
					caid = '0%s' % caid
				caid = caid[:2]
				caid = caid.upper()
				if caid == iscaid:
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
				caid = '0%s' % caid
			caid = caid[:2]
			caid = caid.upper()
		return caid

	def int2hex(self, int):
		return '%x' % int

	def changed(self, what):
		Converter.changed(self, what)
