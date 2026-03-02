from pool_buddy_qt import DEFAULT
from pool_buddy_qt import ConfigDriver
from pool_buddy_qt.Web import dbCredentials,dbConnector
from pool_buddy_qt.ui_scripts.guiFunctions import guiFunctions
from pool_buddy_qt.ui_scripts.PoolbuddyOSui import PoolbuddyOSui
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


class LoginPageUI(QMainWindow):
    def __init__(self, root_dir):
        super().__init__()
        self.dir_path = root_dir
        self.w = None  # No external window yet.
        self.serielNumConfig = ConfigDriver(jsonFile=DEFAULT.serielNumFilePath)
        uic.loadUi(self.dir_path+'/ui/loginPage.ui', self)
        self.loginBtn.clicked.connect(self.login)
    
    def login(self):
        username = self.usernameTxtBox.text()
        password = self.passwordTxtBox.text()
        dbLogin = dbCredentials(username=username,password=password)
        db = dbConnector(dbLogin)
        checkLogin = db.update(url='https://www.quackyos.com/PoolBuddyWeb/scripts/login.php', pload={})
        if(checkLogin == 'true'):
            self.serielNumConfig.generateSerielNum(username=username, password=password)
            guiFunctions.openWindow(self, PoolbuddyOSui(dbLogin, root_dir=self.dir_path), True)