import datetime
from pool_buddy import ConfigDriver
from pool_buddy import SensorAndWeather
from pool_buddy import HardwareDriver
from scripts.Web import dbCredentials,dbConnector
from scripts.ui.guiFunctions import guiFunctions
from scripts.ui.SettingsUI import SettingsUI
from scripts.Web import *

from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5 import QtTest

class GetDateTimeThread(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
        self.running = True

    @pyqtSlot()
    def executeThread(self):
        while self.running:
            # GET DATE AND SET LABEL
            now = datetime.datetime.now()
            # dd/mm/YY H:M:S
            date = now.strftime("%m/%d/%Y")
            self.signal_to_emit.emit('dateLabel', str(date))

            # GET TIME AND SET LABEL
            now = datetime.datetime.now()
            date = now.strftime("%I:%M:%S %p")
            self.signal_to_emit.emit('timeLabel', str(date))

            QtTest.QTest.qWait(1000)

class HardwareDriverThread(QObject):
    def __init__(self, signal_to_emit, dbLogin:dbCredentials, serielNum, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
        self.running = True
        self.hardware_driver = HardwareDriver()
        self.db = dbConnector(login=dbLogin)
        self.serielNum = serielNum

    @pyqtSlot()
    def executeThread(self):
        while self.running:
            if (self.hardware_driver.switch()):
                self.signal_to_emit.emit('poolCoverStatusLabel', 'ACTIVE')
                self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'serielNum': self.serielNum, 'switch':'ACTIVE'})
            QtTest.QTest.qWait(500)

class SensorAndWeatherThread(QObject):
    def __init__(self, signal_to_emit, dbLogin:dbCredentials, serielNum, parent=None):
        self.dbLogin = dbLogin
        self.db = dbConnector(dbLogin)
        self.serielNum = serielNum
        self.sensor_weather = SensorAndWeather()
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit
        self.running = True

    @pyqtSlot()
    def executeThread(self):
        try:
            self.signal_to_emit.emit('maxTempTxtBox', '...')
            self.signal_to_emit.emit('poolCoverStatusLabel', '...')
            while self.running:
                weather = self.sensor_weather.getWeather()
                waterTemp = self.sensor_weather.waterTemp()

                if (weather):
                    self.signal_to_emit.emit('outsideTempLabel', str(weather["outside"]))

                switch = self.db.get(index=2,serielNum=self.serielNum)

                if (waterTemp != None):
                    if waterTemp > float(self.db.get(index=3, serielNum=self.serielNum)) and switch == "ACTIVE":
                        msg = "Take off the damn pool cover the water temperature is " + str(waterTemp) + "F" + " The outside temperature is " + str(self.sensor_weather.getWeather()["outside"]) + "F"
                        Email().send(msg,[])
                        self.signal_to_emit.emit('poolCoverStatusLabel', 'DISABLED')
                        self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'serielNum': self.serielNum, 'switch':'DISABLED'})

                self.signal_to_emit.emit('waterTempLabel', str(waterTemp))
                self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'serielNum': self.serielNum, 'loc':'water','temp':str(waterTemp)})

                self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'serielNum': self.serielNum, 'loc':'outside','temp':str(weather["outside"])})

                # GET MAX TEMP AND SET TEXT BOX
                self.signal_to_emit.emit('maxTempTxtBox', str(self.db.get(index=3,serielNum=self.serielNum)))
                self.signal_to_emit.emit('poolCoverStatusLabel', str(self.db.get(index=2,serielNum=self.serielNum)))

                QtTest.QTest.qWait(10000)
        except Exception as e:
            print(e)
            pass

class PoolbuddyOSui(QMainWindow):
    # Signal for checking water/outside temp from CheckTempsThreaded
    tempThreadSig = pyqtSignal(str,str)
    datetimeThreadSig = pyqtSignal(str,str)
    hardwareThreadSig = pyqtSignal(str,str)
    def __init__(self, dbLogin:dbCredentials, root_dir, parent=None):
        self.db = dbConnector(dbLogin)
        self.startBtnState = False
        super().__init__()
        self.dir_path = root_dir
        self.w = None  # No external window yet.
        uic.loadUi(self.dir_path+'/ui/PoolBuddyV2.ui', self)
        # Setup vars
        self.serielNumConfig = ConfigDriver(jsonFile="/serielNum.json")
        self.settingsConfig = ConfigDriver(jsonFile="/config.json")
        self.serielNum = str(self.serielNumConfig.getConfig()["deviceInfo"][0]["serielNum"])
        self.owmAPIkey = str(self.settingsConfig.getConfig()["owmApiKey"])
        # Start CheckTempsThreaded
        self.tempsThreaded = SensorAndWeatherThread(signal_to_emit=self.tempThreadSig,dbLogin=dbLogin,serielNum=self.serielNum)
        self.tempsThread = QThread(self)
        self.tempsThreaded.moveToThread(self.tempsThread)
        self.tempsThread.start()
        # Start date time thread
        self.dateTimeUpdate = GetDateTimeThread(self.datetimeThreadSig)
        self.dateTimeThread = QThread(self)
        self.dateTimeUpdate.moveToThread(self.dateTimeThread)
        self.dateTimeThread.start()
        # Start Hardware Thread
        self.hardwareUpdate = HardwareDriverThread(self.hardwareThreadSig,dbLogin=dbLogin, serielNum=self.serielNum)
        self.hardwareThread = QThread(self)
        self.hardwareUpdate.moveToThread(self.hardwareThread)
        self.hardwareThread.start()
        self.serielNumLabel.setText('Seriel: ' + str(self.serielNum))
        self.startStopBtn.clicked.connect(self.tempsThreaded.executeThread)
        self.startStopBtn.clicked.connect(self.dateTimeUpdate.executeThread)
        self.startStopBtn.clicked.connect(self.hardwareUpdate.executeThread)
        self.startStopBtn.clicked.connect(self.startStop)
        self.setMaxTempBtn.clicked.connect(lambda: self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateMaxTemp.php', pload={'serielNum':self.serielNum, 'waterTempMax':str(self.maxTempTxtBox.text())}))
        self.settingsButton.clicked.connect(lambda: guiFunctions.openWindow(self, SettingsUI(dbLogin=dbLogin, dir_path=self.dir_path), True))
        self.tempThreadSig.connect(self.updateGUI)
        self.datetimeThreadSig.connect(self.updateGUI)
        self.hardwareThreadSig.connect(self.updateGUI)

    @pyqtSlot(str,str)
    def updateGUI(self, label, text):
        getattr(self,label).setText(text)

    @pyqtSlot()
    def executeHardwareDriverThread(self):
        while self.running:
            try:
                self.switch(dbLogin=self.dbLogin, serielNum=self.serielNum, resetSwitchPin=self.resetSwitchPin, resetLEDPin=self.resetLEDPin)
            except Exception as e:
                print('Hardware Error: ' + str(e))

    def startStop(self):
        # Set threads running state oppisite of button state aka off
        self.tempsThreaded.running = not self.startBtnState
        self.dateTimeUpdate.running = not self.startBtnState
        self.hardwareUpdate.running = not self.startBtnState
        
        # Set button state to oppisite
        self.startBtnState = not self.startBtnState