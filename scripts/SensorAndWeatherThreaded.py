from scripts import DEFAULT
from scripts.WaterProbeDriver import WaterProbeDriver
from scripts.Web import dbConnector,dbCredentials, Email
from scripts.ConfigDriver import ConfigDriver
from scripts.CustomTerminal import PrintColor
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5 import QtTest
import pyowm, datetime
class SensorAndWeatherThreaded(QObject):
    def __init__(self, dbLogin:dbCredentials, signal_to_emit, parent=None):
        self.dbLogin = dbLogin
        self.db = dbConnector(dbLogin)
        self.settingsConfig = ConfigDriver(jsonFile=DEFAULT.configFilePath)
        self.serielNumConfig = ConfigDriver(jsonFile=DEFAULT.serielNumFilePath)
        self.serielNum = str(self.serielNumConfig.getConfig()["deviceInfo"][0]["serielNum"])
        self.owmAPIkey = str(self.settingsConfig.getConfig()["owmApiKey"])
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
        self.running = True

    @pyqtSlot()
    def executeThread(self):
        self.signal_to_emit.emit('maxTempTxtBox', '...')
        self.signal_to_emit.emit('poolCoverStatusLabel', '...')
        while self.running:
            weather = self.getWeather(serielNum=self.serielNum, apiKey=self.owmAPIkey)
            if (weather):
                self.signal_to_emit.emit('outsideTempLabel', str(weather["outside"]))
            self.waterTemp()
            # GET MAX TEMP AND SET TEXT BOX
            self.signal_to_emit.emit('maxTempTxtBox', str(self.db.get(index=3,serielNum=self.serielNum)))
            self.signal_to_emit.emit('poolCoverStatusLabel', str(self.db.get(index=2,serielNum=self.serielNum)))
            QtTest.QTest.qWait(10000)

    def getWeather(self, serielNum, apiKey):
        try:
            owm = pyowm.OWM(apiKey) # TODO: Replace <api_key> with your API key
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
            self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'serielNum': serielNum, 'loc':'outside','temp':str(outside)})
        except Exception as e:
            PrintColor.red("Get Weather Error: " + str(e))
            outside="ERR"
        return {"outside":outside}

    def waterTemp(self):
        try:
            c, f = WaterProbeDriver().read_temp()

            water = f

            switch = self.db.get(index=2,serielNum=self.serielNum)

            if water > float(self.db.get(index=3)) and switch == "ACTIVE":
                msg = "Take off the damn pool cover the water temperature is " + str(round(water,1)) + "F" + " The outside temperature is " + str(self.getOutsideTemp()) + "F"
                # TODO GIVE THIS THE ACTAUL EMAIL LIST
                Email().send(msg,[])
                self.signal_to_emit.emit('poolCoverStatusLabel', 'DISABLED')
                self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'serielNum': self.serielNum, 'switch':'DISABLED'})

            waterTemp = round(water, 1)

            now = datetime.datetime.now()
            # GET TIME AND SET LABEL
            waterTempLastUpdated = now.strftime("%H:%M:%S %P")
            print('Water Last Updated...' + str(waterTempLastUpdated) + " " + str(waterTemp))

            self.signal_to_emit.emit('waterTempLabel', str(waterTemp))
            self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'serielNum': self.serielNum, 'loc':'water','temp':str(waterTemp)})
        except Exception as e:
            PrintColor.red('Get Water Temp Error: ' + str(e))
            pass