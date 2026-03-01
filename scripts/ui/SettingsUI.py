from pool_buddy import DEFAULT
from pool_buddy import ConfigDriver
from scripts.Web import dbCredentials
from PyQt5 import uic
from PyQt5 import QtTest
from PyQt5.QtWidgets import QMainWindow
class SettingsUI(QMainWindow):
    def __init__(self, dbLogin:dbCredentials, dir_path, parent=None):
        super(SettingsUI, self).__init__(parent)
        self.username = dbLogin.username
        self.settingsConfig = ConfigDriver(jsonFile=DEFAULT.configFilePath)
        self.serielNumConfig = ConfigDriver(jsonFile=DEFAULT.serielNumFilePath)
        self.focusedBtn = ""
        self.secretsLock = True
        self.obscuredText = "****************"
        self.savedSettingsLabelText = "Saved!"
        self.savedSettingsLabelTime = 4
        uic.loadUi(dir_path+'/ui/settings.ui', self)  # Load the .ui file into the QFrame
        self.secretLineEdits = [self.owmAPIKeyLineEdit, self.serielNumLineEdit]
        self.changePage(self.aboutBtn, 0)
        self.obscureSecrets(self.secretLineEdits)
        self.savedSettingsLabel.setText("")
        # Sidebar Btns
        self.aboutBtn.clicked.connect(lambda: self.changePage(self.aboutBtn, 0))
        self.accountBtn.clicked.connect(lambda: self.changePage(self.accountBtn, 1))
        self.deviceBtn.clicked.connect(lambda: self.changePage(self.deviceBtn, 2))
        self.applyBtn.clicked.connect(lambda: self.saveSettings())
        self.cancelBtn.clicked.connect(lambda: self.restoreSettings())
        # Other Btns
        self.secretsLockBtn.clicked.connect(self.unlockSecrets)
        # Load Settings
        self.restoreSettings()
    
    def changePage(self, btn, index):
        # Change button style to focused
        try:
            self.focusedBtn.setProperty("class2", "")
            self.focusedBtn.setStyleSheet("")
        except Exception as e:
            pass
        self.focusedBtn=btn
        btn.setProperty("class2", "sidebarBtnFocus")
        btn.setStyleSheet("")

        self.SettingsLoader.setCurrentIndex(index)

    def unlockSecrets(self, lockOveride=False):
        owmAPIKey = str(self.settingsConfig.getConfig()["owmApiKey"])
        serielNum = str(self.serielNumConfig.getConfig()["deviceInfo"][0]["serielNum"])
        
        self.secretsLock = not self.secretsLock
        if (lockOveride):
            self.secretsLock = lockOveride
        if (self.secretsLock):
            self.secretsLockBtn.setProperty("class", "lockBtn")

            self.obscureSecrets(self.secretLineEdits)
        else:
            self.secretsLockBtn.setProperty("class", "unlockBtn")
            self.owmAPIKeyLineEdit.setText(owmAPIKey)
            self.serielNumLineEdit.setText(serielNum)
        # Enable Secret Line Edits
        for lineEdit in self.secretLineEdits:
            lineEdit.setEnabled(not self.secretsLock)
        # Refresh stylesheet
        self.secretsLockBtn.setStyleSheet("")

    def obscureSecrets(self, lineEdits):
        # Clear Line edit secrets, and obscure it if its not empty
        for object in lineEdits:
            object.setText(self.obscuredText)

    def savedLabellTimer(self):
        count = 0
        while count < self.savedSettingsLabelTime:
            self.savedSettingsLabel.show()
            self.savedSettingsLabel.setText(self.savedSettingsLabelText)
            QtTest.QTest.qWait(500)
            self.savedSettingsLabel.setText("")
            QtTest.QTest.qWait(500)
            count+=1

    def saveSettings(self):
        self.settingsToSave = {"emailNotify":self.emailNotifyCheckBox.isChecked(), "emailList":"", "owmApiKey":self.owmAPIKeyLineEdit.text(),"WaterSensorLocation":self.waterSensorLocationLineEdit.text(),"ResetSwitchPin":self.resetSwitchPinLineEdit.text(),"ResetLEDPin":self.resetLEDLineEdit.text(),"owmLocation":self.owmLocationLineEdit.text(),"tempUnit":self.tempUnitComboBox.currentIndex()}
        for key, value in self.settingsToSave.items():
            print(key)
            if (value == self.obscuredText):
                pass
            else:
                print(value)
                self.settingsConfig.writeConfig(key=key, value=value)
        self.savedLabellTimer()

    def restoreSettings(self):
        # User Settings
        WaterSensorLocation = self.settingsConfig.getConfig()["WaterSensorLocation"]
        ResetSwitchPin = str(self.settingsConfig.getConfig()["ResetSwitchPin"])
        ResetLEDPin = str(self.settingsConfig.getConfig()["ResetLEDPin"])
        EmailNotify = bool(self.settingsConfig.getConfig()["emailNotify"])
        OWM_API_Key = str(self.settingsConfig.getConfig()["owmApiKey"])
        omwLocation = str(self.settingsConfig.getConfig()["owmLocation"])
        tempUnit = self.settingsConfig.getConfig()["tempUnit"]
        # QuackyOS Account Page
        self.usernameLineEdit.setText(self.username)
        self.userEmailLineEdit.setText("")
        self.roleLineEdit.setText("")
        # Device Page
        self.resetSwitchPinLineEdit.setText(ResetSwitchPin)
        self.resetLEDLineEdit.setText(ResetLEDPin)
        self.waterSensorLocationLineEdit.setText(WaterSensorLocation)
        self.emailNotifyCheckBox.setChecked(EmailNotify)
        self.tempUnitComboBox.setCurrentIndex(tempUnit)
        self.owmLocationLineEdit.setText(omwLocation)
        self.unlockSecrets(lockOveride=True)