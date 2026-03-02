from pool_buddy.CustomTerminal import PrintColor
from pool_buddy import WaterProbeDriver
import pyowm
import datetime


class SensorAndWeather():
    def __init__(self, owm_api_key, owm_location, temp_unit, water_sensor_seriel):
        self.owm_api_key = owm_api_key
        self.owm_location = owm_location
        self.temp_unit = temp_unit
        self.water_sensor_seriel = water_sensor_seriel

    def getWeather(self):
        try:
            owm = pyowm.OWM(self.owm_api_key)
            owmMgr = owm.weather_manager()
            location = owmMgr.weather_at_place(self.owm_location)
            locationWeather = location.weather
            if (self.temp_unit == 0):
                outside = locationWeather.temperature('fahrenheit')
            elif(self.temp_unit == 1):
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
            c, f = WaterProbeDriver(water_sensor_seriel=self.water_sensor_seriel).read_temp()

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