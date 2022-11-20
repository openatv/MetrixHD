from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Components.Converter.Poll import Poll


class MetrixHDWeather(Poll, Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type
		Poll.__init__(self)
		self.poll_interval = 60000
		self.poll_enabled = True

	@cached
	def getText(self):
		try:
			if self.type == "currentWeatherTemp":
				return config.plugins.MetrixWeather.currentWeatherTemp.value
			elif self.type == "currentWeatherCode":
				return config.plugins.MetrixWeather.currentWeatherCode.value
			elif self.type == "forecastTodayTempMin":
				return config.plugins.MetrixWeather.forecastTodayTempMin.value + " " + self.getCF()
			elif self.type == "forecastTodayTempMax":
				return config.plugins.MetrixWeather.forecastTodayTempMax.value + " " + self.getCF()
			elif self.type == "forecastTomorrowCode":
				return config.plugins.MetrixWeather.forecastTomorrowCode.value
			elif self.type == "forecastTomorrowTempMin":
				return config.plugins.MetrixWeather.forecastTomorrowTempMin.value + " " + self.getCF()
			elif self.type == "forecastTomorrowTempMax":
				return config.plugins.MetrixWeather.forecastTomorrowTempMax.value + " " + self.getCF()
			elif self.type == "CF":
				return self.getCF()
			else:
				return ""
		except:
			return ""

	@cached
	def getValue(self):
		if self.type == "currentDataValid":
			try:
				return config.plugins.MetrixWeather.currentWeatherDataValid.value
			except ValueError:
				return 0
		return -1

	def getCF(self):
		return "°F" if config.plugins.MetrixWeather.tempUnit.value == "Fahrenheit" else "°C"

	value = property(getValue)
	text = property(getText)
