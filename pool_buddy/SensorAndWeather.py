from scripts import DEFAULT
from scripts.ConfigDriver import ConfigDriver
from scripts.CustomTerminal import PrintColor
from scripts.WaterProbeDriver import WaterProbeDriver
import pyowm
import datetime


class SensorAndWeather():
    def __init__(self):
        self.settingsConfig = ConfigDriver(jsonFile=DEFAULT.configFilePath)

    def getWeather(self):
        try:
            owm = pyowm.OWM(self.settingsConfig.getConfig()["owmApiKey"])
            owmMgr = owm.weather_manager()
            location = owmMgr.weather_at_place(self.settingsConfig.getConfig()["owmLocation"])
            locationWeather = location.weather
            if (self.settingsConfig.getConfig()["tempUnit"] == 0):
                outside = locationWeather.temperature('fahrenheit')
            elif(self.settingsConfig.getConfig()["tempUnit"] == 1):
                outside = locationWeather.temperature('celsius')
            outside = round(float(outside['temp']), 1)

            now = datetime.datetime.now()
            lastUpdated = now.strftime("%H:%M:%S")
            print('Outside Last Updated...' + str(lastUpdated))
            return {"outside":outside}
        except Exception as e:
            PrintColor.red("Get Weather Error: " + str(e))
            outside="ERR"

    def waterTemp(self):
        try:
            c, f = WaterProbeDriver().read_temp()

            water = f

            waterTemp = round(water, 1)

            now = datetime.datetime.now()
            # GET TIME AND SET LABEL
            waterTempLastUpdated = now.strftime("%H:%M:%S %P")
            print('Water Last Updated...' + str(waterTempLastUpdated) + " " + str(waterTemp))

            return waterTemp
        except Exception as e:
            PrintColor.red('Get Water Temp Error: ' + str(e))
            return None