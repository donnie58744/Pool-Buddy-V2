from scripts.Web import dbCredentials,dbConnector
from scripts.ConfigDriver import ConfigDriver
from scripts.GetDateTimeThreaded import GetDateTimeThreaded
from scripts.SensorAndWeatherThreaded import SensorAndWeatherThreaded
from scripts.HardwareDriverThreaded import HardwareDriverThreaded
from scripts.ui.guiFunctions import guiFunctions
from scripts.ui.SettingsUI import SettingsUI

from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
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
        self.tempsThreaded = SensorAndWeatherThreaded(dbLogin=dbLogin,signal_to_emit=self.tempThreadSig)
        self.tempsThread = QThread(self)
        self.tempsThreaded.moveToThread(self.tempsThread)
        self.tempsThread.start()
        # Start date time thread
        self.dateTimeUpdate = GetDateTimeThreaded(self.datetimeThreadSig)
        self.dateTimeThread = QThread(self)
        self.dateTimeUpdate.moveToThread(self.dateTimeThread)
        self.dateTimeThread.start()
        # Start Hardware Thread
        self.hardwareUpdate = HardwareDriverThreaded(dbLogin=dbLogin,signal_to_emit=self.hardwareThreadSig)
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

    def startStop(self):
        # Set threads running state oppisite of button state aka off
        self.tempsThreaded.running = not self.startBtnState
        self.dateTimeUpdate.running = not self.startBtnState
        self.hardwareUpdate.running = not self.startBtnState
        
        # Set button state to oppisite
        self.startBtnState = not self.startBtnState