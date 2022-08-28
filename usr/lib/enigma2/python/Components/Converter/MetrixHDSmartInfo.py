#
#  Coded by Vali
#


from enigma import iServiceInformation
from Components.Converter.Converter import Converter
from Components.Element import cached
from Components.config import config
from Components.Converter.Poll import Poll


class MetrixHDSmartInfo(Poll, Converter, object):
	SMART_INFO_H = 1

	def __init__(self, type):
		Converter.__init__(self, type)
		Poll.__init__(self)
		self.type = {
				"ExpertInfo": self.SMART_INFO_H,
			}[type]
		self.poll_interval = 30000
		self.poll_enabled = True
		self.ar_fec = ["Auto", "1/2", "2/3", "3/4", "5/6", "7/8", "3/5", "4/5", "8/9", "9/10", "None", "None", "None", "None", "None"]
		self.ar_pol = ["H", "V", "CL", "CR", "na", "na", "na", "na", "na", "na", "na", "na"]

	@cached
	def getText(self):
		service = self.source.service
		info = service and service.info()
		if not info:
			return ""
		Ret_Text = ""
		Sec_Text = ""
		if (self.type == self.SMART_INFO_H):  # HORIZONTAL
			decID = ""
			decCI = "0x000"
			decFrom = ""
			eMasTime = ""
			res = ""
			dccmd = ""
			searchIDs = []
			foundIDs = []
			xresol = info.getInfo(iServiceInformation.sVideoWidth)
			yresol = info.getInfo(iServiceInformation.sVideoHeight)
			feinfo = (service and service.frontendInfo())
			if (feinfo is not None) and (xresol > 0):
				#Ret_Text = str(xresol) + "x" + str(yresol) + "   "
				#if (yresol > 580):
					#Ret_Text = "HD     "
				#else:
					#Ret_Text = "SD     "
				frontendData = (feinfo and feinfo.getAll(True))
				if (frontendData is not None):
					if ((frontendData.get("tuner_type") == "DVB-S") or (frontendData.get("tuner_type") == "DVB-C")):
						frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
						symbolrate = (str((frontendData.get("symbol_rate") / 1000)) + "")
						try:
							if (frontendData.get("tuner_type") == "DVB-S"):
								polarisation_i = frontendData.get("polarization")
							else:
								polarisation_i = 0
							fec_i = frontendData.get("fec_inner")
							Ret_Text = Ret_Text + frequency + "  " + self.ar_pol[polarisation_i] + "  " + self.ar_fec[fec_i] + "  " + symbolrate + " "
						except:
							Ret_Text = Ret_Text + frequency + " " + symbolrate + " "
						orb_pos = ""
						if (frontendData.get("tuner_type") == "DVB-S"):
							orbital_pos = int(frontendData["orbital_position"])
							if orbital_pos > 1800:
								if orbital_pos == 3590:
									orb_pos = 'Thor/Intelsat (1.0W)'
								elif orbital_pos == 3560:
									orb_pos = 'Amos (4.0W)'
								elif orbital_pos == 3550:
									orb_pos = 'Atlantic Bird (5.0W)'
								elif orbital_pos == 3530:
									orb_pos = 'Nilesat/Atlantic Bird (7.0W)'
								elif orbital_pos == 3520:
									orb_pos = 'Atlantic Bird (8.0W)'
								elif orbital_pos == 3475:
									orb_pos = 'Atlantic Bird (12.5W)'
								elif orbital_pos == 3460:
									orb_pos = 'Express (14.0W)'
								elif orbital_pos == 3450:
									orb_pos = 'Telstar (15.0W)'
								elif orbital_pos == 3420:
									orb_pos = 'Intelsat (18.0W)'
								elif orbital_pos == 3380:
									orb_pos = 'Nss (22.0W)'
								elif orbital_pos == 3355:
									orb_pos = 'Intelsat (24.5W)'
								elif orbital_pos == 3325:
									orb_pos = 'Intelsat (27.5W)'
								elif orbital_pos == 3300:
									orb_pos = 'Hispasat (30.0W)'
								elif orbital_pos == 3285:
									orb_pos = 'Intelsat (31.5W)'
								elif orbital_pos == 3170:
									orb_pos = 'Intelsat (43.0W)'
								elif orbital_pos == 3150:
									orb_pos = 'Intelsat (45.0W)'
								elif orbital_pos == 3070:
									orb_pos = 'Intelsat (53.0W)'
								elif orbital_pos == 3045:
									orb_pos = 'Intelsat (55.5W)'
								elif orbital_pos == 3020:
									orb_pos = 'Intelsat 9 (58.0W)'
								elif orbital_pos == 2990:
									orb_pos = 'Amazonas (61.0W)'
								elif orbital_pos == 2900:
									orb_pos = 'Star One (70.0W)'
								elif orbital_pos == 2880:
									orb_pos = 'AMC 6 (72.0W)'
								elif orbital_pos == 2875:
									orb_pos = 'Echostar 6 (72.7W)'
								elif orbital_pos == 2860:
									orb_pos = 'Horizons (74.0W)'
								elif orbital_pos == 2810:
									orb_pos = 'AMC5 (79.0W)'
								elif orbital_pos == 2780:
									orb_pos = 'NIMIQ 4 (82.0W)'
								elif orbital_pos == 2690:
									orb_pos = 'NIMIQ 1 (91.0W)'
								elif orbital_pos == 3592:
									orb_pos = 'Thor/Intelsat (0.8W)'
								elif orbital_pos == 2985:
									orb_pos = 'Echostar 3,12 (61.5W)'
								elif orbital_pos == 2830:
									orb_pos = 'Echostar 8 (77.0W)'
								elif orbital_pos == 2630:
									orb_pos = 'Galaxy 19 (97.0W)'
								elif orbital_pos == 2500:
									orb_pos = 'Echostar 10,11 (110.0W)'
								elif orbital_pos == 2502:
									orb_pos = 'DirectTV 5 (110.0W)'
								elif orbital_pos == 2410:
									orb_pos = 'Echostar 7 Anik F3 (119.0W)'
								elif orbital_pos == 2391:
									orb_pos = 'Galaxy 23 (121.0W)'
								elif orbital_pos == 2390:
									orb_pos = 'Echostar 9 (121.0W)'
								elif orbital_pos == 2412:
									orb_pos = 'DirectTV 7S (119.0W)'
								elif orbital_pos == 2310:
									orb_pos = 'Galaxy 27 (129.0W)'
								elif orbital_pos == 2311:
									orb_pos = 'Ciel 2 (129.0W)'
								elif orbital_pos == 2120:
									orb_pos = 'Echostar 2 (148.0W)'
								else:
									orb_pos = str((float(3600 - orbital_pos)) / 10.0) + "W"
							elif orbital_pos > 0:
								if orbital_pos == 192:
									orb_pos = 'Astra 1F (19.2E)'
								elif orbital_pos == 130:
									orb_pos = 'Hot Bird 6,7A,8 (13.0E)'
								elif orbital_pos == 235:
									orb_pos = 'Astra 1E (23.5E)'
								elif orbital_pos == 1100:
									orb_pos = 'BSat 1A,2A (110.0E)'
								elif orbital_pos == 1101:
									orb_pos = 'N-Sat 110 (110.0E)'
								elif orbital_pos == 1131:
									orb_pos = 'KoreaSat 5 (113.0E)'
								elif orbital_pos == 1440:
									orb_pos = 'SuperBird 7,C2 (144.0E)'
								elif orbital_pos == 1006:
									orb_pos = 'AsiaSat 2 (100.5E)'
								elif orbital_pos == 1030:
									orb_pos = 'Express A2 (103.0E)'
								elif orbital_pos == 1056:
									orb_pos = 'Asiasat 3S (105.5E)'
								elif orbital_pos == 1082:
									orb_pos = 'NSS 11 (108.2E)'
								elif orbital_pos == 881:
									orb_pos = 'ST1 (88.0E)'
								elif orbital_pos == 900:
									orb_pos = 'Yamal 201 (90.0E)'
								elif orbital_pos == 917:
									orb_pos = 'Mesat (91.5E)'
								elif orbital_pos == 950:
									orb_pos = 'Insat 4B (95.0E)'
								elif orbital_pos == 951:
									orb_pos = 'NSS 6 (95.0E)'
								elif orbital_pos == 765:
									orb_pos = 'Telestar (76.5E)'
								elif orbital_pos == 785:
									orb_pos = 'ThaiCom 5 (78.5E)'
								elif orbital_pos == 800:
									orb_pos = 'Express (80.0E)'
								elif orbital_pos == 830:
									orb_pos = 'Insat 4A (83.0E)'
								elif orbital_pos == 850:
									orb_pos = 'Intelsat 709 (85.2E)'
								elif orbital_pos == 750:
									orb_pos = 'Abs (75.0E)'
								elif orbital_pos == 720:
									orb_pos = 'Intelsat (72.0E)'
								elif orbital_pos == 705:
									orb_pos = 'Eutelsat W5 (70.5E)'
								elif orbital_pos == 685:
									orb_pos = 'Intelsat (68.5E)'
								elif orbital_pos == 620:
									orb_pos = 'Intelsat 902 (62.0E)'
								elif orbital_pos == 600:
									orb_pos = 'Intelsat 904 (60.0E)'
								elif orbital_pos == 570:
									orb_pos = 'Nss (57.0E)'
								elif orbital_pos == 530:
									orb_pos = 'Express AM22 (53.0E)'
								elif orbital_pos == 480:
									orb_pos = 'Eutelsat 2F2 (48.0E)'
								elif orbital_pos == 450:
									orb_pos = 'Intelsat (45.0E)'
								elif orbital_pos == 420:
									orb_pos = 'Turksat 2A (42.0E)'
								elif orbital_pos == 400:
									orb_pos = 'Express AM1 (40.0E)'
								elif orbital_pos == 390:
									orb_pos = 'Hellas Sat 2 (39.0E)'
								elif orbital_pos == 380:
									orb_pos = 'Paksat 1 (38.0E)'
								elif orbital_pos == 360:
									orb_pos = 'Eutelsat Sesat (36.0E)'
								elif orbital_pos == 335:
									orb_pos = 'Astra 1M (33.5E)'
								elif orbital_pos == 330:
									orb_pos = 'Eurobird 3 (33.0E)'
								elif orbital_pos == 328:
									orb_pos = 'Galaxy 11 (32.8E)'
								elif orbital_pos == 315:
									orb_pos = 'Astra 5A (31.5E)'
								elif orbital_pos == 310:
									orb_pos = 'Turksat (31.0E)'
								elif orbital_pos == 305:
									orb_pos = 'Arabsat (30.5E)'
								elif orbital_pos == 285:
									orb_pos = 'Eurobird 1 (28.5E)'
								elif orbital_pos == 284:
									orb_pos = 'Eurobird/Astra (28.2E)'
								elif orbital_pos == 282:
									orb_pos = 'Eurobird/Astra (28.2E)'
								elif orbital_pos == 1220:
									orb_pos = 'AsiaSat (122.0E)'
								elif orbital_pos == 1380:
									orb_pos = 'Telstar 18 (138.0E)'
								elif orbital_pos == 260:
									orb_pos = 'Badr 3/4 (26.0E)'
								elif orbital_pos == 255:
									orb_pos = 'Eurobird 2 (25.5E)'
								elif orbital_pos == 215:
									orb_pos = 'Eutelsat (21.5E)'
								elif orbital_pos == 216:
									orb_pos = 'Eutelsat W6 (21.6E)'
								elif orbital_pos == 210:
									orb_pos = 'AfriStar 1 (21.0E)'
								elif orbital_pos == 160:
									orb_pos = 'Eutelsat W2 (16.0E)'
								elif orbital_pos == 100:
									orb_pos = 'Eutelsat W1 (10.0E)'
								elif orbital_pos == 90:
									orb_pos = 'Eurobird 9 (9.0E)'
								elif orbital_pos == 70:
									orb_pos = 'Eutelsat W3A (7.0E)'
								elif orbital_pos == 50:
									orb_pos = 'Sirius 4 (5.0E)'
								elif orbital_pos == 48:
									orb_pos = 'Sirius 4 (4.8E)'
								elif orbital_pos == 30:
									orb_pos = 'Telecom 2 (3.0E)'
								else:
									orb_pos = str((float(orbital_pos)) / 10.0) + "E"
						Ret_Text = Ret_Text + "" + orb_pos + ""
					elif (frontendData.get("tuner_type") == "DVB-T"):
						frequency = (str((frontendData.get("frequency") / 1000)) + " MHz")
						Ret_Text = Ret_Text + "Frequency: " + frequency
				prvd = info.getInfoString(iServiceInformation.sProvider)
				#Ret_Text = prvd + "  " + Ret_Text
			res = ""
			Ret_Text = Ret_Text
			return Ret_Text
		return ""

	text = property(getText)

	def changed(self, what):
		Converter.changed(self, what)

	def kurz(self, langTxt):
		if (len(langTxt) > 23):
			retT = langTxt[:20] + "..."
			return retT
		else:
			return langTxt
