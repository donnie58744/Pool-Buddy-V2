from scripts import DEFAULT
from scripts.CustomTerminal import PrintColor
from scripts.Web import dbConnector,dbCredentials
from scripts.ConfigDriver import ConfigDriver
from PyQt5.QtCore import pyqtSlot, QObject
from PyQt5 import QtTest
try:
    import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(17, GPIO.OUT)
except ImportError as e:
    print(e)
class HardwareDriverThreaded(QObject):
    def __init__(self, dbLogin:dbCredentials, signal_to_emit, parent=None):
        super().__init__(parent)
        self.settingsConfig=ConfigDriver(jsonFile=DEFAULT.configFilePath)
        self.serielNumConfig = ConfigDriver(jsonFile=DEFAULT.serielNumFilePath)
        self.dbLogin = dbLogin
        self.db = dbConnector(self.dbLogin)
        self.serielNum = str(self.serielNumConfig.getConfig()["deviceInfo"][0]["serielNum"])
        self.resetSwitchPin = self.settingsConfig.getConfig()["ResetSwitchPin"]
        self.resetLEDPin = self.settingsConfig.getConfig()["ResetLEDPin"]
        self.signal_to_emit = signal_to_emit
        self.running = True

    @pyqtSlot()
    def executeThread(self):
        while self.running:
            try:
                self.switch(dbLogin=self.dbLogin, serielNum=self.serielNum, resetSwitchPin=self.resetSwitchPin, resetLEDPin=self.resetLEDPin)
            except Exception as e:
                print('Hardware Error: ' + str(e))

    def switch(self, dbLogin:dbCredentials, serielNum,resetSwitchPin,resetLEDPin):
        try:
            button = GPIO.input(resetSwitchPin)

            if button == False:
                resetLED = GPIO.output(resetLEDPin, GPIO.HIGH)
                QtTest.QTest.qWait(3000)
                resetLED = GPIO.output(resetLEDPin, GPIO.LOW)
                self.signal_to_emit.emit('poolCoverStatusLabel', 'ACTIVE')
                self.db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'serielNum': serielNum, 'switch':'ACTIVE'})
        except Exception as e:
            #PrintColor.red("Switch ERROR: " + str(e))
            pass