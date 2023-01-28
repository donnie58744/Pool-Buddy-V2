import platform, subprocess
import string
import random
machineOs = platform.system()
if (machineOs == 'Linux'):
    subprocess.check_call(["sudo", "apt", "install", "python3-pyqt5"])
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTextEdit, QPushButton
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSlot, QObject, pyqtSignal
from PyQt5 import QtTest

import os, sys, pyowm, glob, requests, datetime, json
try:
    import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(17, GPIO.OUT)
except ImportError as e:
    print(e)
globalUsername = ''
globalPassword = ''
dir_path = os.path.dirname(os.path.realpath(__file__))

class configDriver():
    def getConfig(self, filename):
        try:
            # Open JSON file
            f = open(filename)
            data = json.load(f)
            
            return data
        except:
            return False

    def createFile(self, filename):
        if not os.path.isfile(filename):
            with open(filename, 'w') as file:
                self.prGreen(f"{file} Has Been Created!")
                file.close()

    def prRed(self, skk): print("\033[91m{}\033[00m" .format(skk))
    def prGreen(self, skk): print("\033[92m{}\033[00m" .format(skk))
    def prYellow(self, skk): print("\033[93m{}\033[00m" .format(skk))

    def generateSerielNum(self,username,password):
        serielNumFile = dir_path+'/serielNum.json'
        # Create Seriel Number File
        self.createFile(filename=serielNumFile)
        try:
            retrivedSerielNum=self.getConfig(filename=serielNumFile)["deviceInfo"][0]["serielNum"]
        except TypeError:
            retrivedSerielNum=""
        if (retrivedSerielNum == ""):
            configDriver().prYellow('Making Seriel Number...')
            with open(serielNumFile, 'w') as outfile:
                def randStr(chars = string.ascii_uppercase + string.digits, N=30):
                    return ''.join(random.choice(chars) for _ in range(N))
                serielNum = randStr()
                print(serielNum)

                # Send Seriel Number
                dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/createSerielNumEntry.php', pload={'pyUser':username, 'pyPass':password, 'serielNum':serielNum})

                # Output Seriel Number To File
                data = {
                    'deviceInfo' : [
                        {
                            'serielNum' : serielNum
                        }
                    ]
                }
                json.dump(data, outfile)
                configDriver().prGreen('Seriel Number Created!')

class WaterProbeDriver():
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_path = glob.glob(base_dir + '28-030e979422c2')[0] #get file path of sensor
    except IndexError:
        configDriver().prRed('Cant Find Water Probe')
        device_path = ''
        pass

    def read_temp_raw(self):
        try:
            with open(self.device_path + '/w1_slave', 'r') as f:
                valid, temp = f.readlines()
            return valid, temp
        except Exception as e:
            configDriver().prYellow('Water Probe Error: ' + str(e))
            pass

    def read_temp(self):
        try:
            valid, temp = self.read_temp_raw()

            while 'YES' not in valid:
                valid, temp = self.read_temp_raw()

            pos = temp.index('t=')
            if pos != -1:
                # read the temperature .
                temp_string = temp[pos + 2:]
                temp_c = float(temp_string) / 1000.0
                temp_f = temp_c * (9.0 / 5.0) + 32.0
                return temp_c, temp_f + 3.5
        except Exception as e:
            configDriver().prYellow('Water Probe Error: ' + str(e))
            pass

class GetDateAndTimeThreaded(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit

    @pyqtSlot()
    def executeThread( self ):
        while True:
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

class dbConnector():
    def getDBInfo(self, index):
        global globalUsername
        global globalPassword
        serielNum = str(configDriver().getConfig(filename=dir_path+'/serielNum.json')["deviceInfo"][0]["serielNum"])
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
            }
            r = requests.post('https://www.quackyos.com/PoolBuddyWeb/scripts/getTemps.php', headers=headers, data={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum': serielNum})
            jsonResponse = r.json()
            return jsonResponse[index]
        except Exception as e:
            configDriver().prRed('Get DB Info Failed: ' + str(e))
            pass

    def updateDBInfo(self, url, pload):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
            }
            r = requests.post(url, data=pload, headers=headers)
            print(r.text)
            return r.text
        except Exception as e:
            configDriver().prRed('Update DB Info Failed: ' + str(e))
            pass

    def sendEmail(self,message):
        for x in configDriver().getConfig(filename=dir_path+'/config.json')["emailList"]:
            dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/sendmail.php', pload={'address': x,'message':message})
            print(x)

class CheckTempsThreaded(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit

    @pyqtSlot()
    def executeThread( self ):
        self.signal_to_emit.emit('maxTempTxtBox', '...')
        self.signal_to_emit.emit('statusLabel', '...')
        while True:
            self.signal_to_emit.emit('outsideTempLabel', str(self.getOutsideTemp()))
            QtTest.QTest.qWait(2000)
            self.waterTemp()
            # GET MAX TEMP AND SET TEXT BOX
            self.signal_to_emit.emit('maxTempTxtBox', str(dbConnector().getDBInfo(index=3)))
            self.signal_to_emit.emit('statusLabel', str(dbConnector().getDBInfo(index=2)))
            QtTest.QTest.qWait(100000)

    def getOutsideTemp(self):
        global globalUsername
        global globalPassword
        serielNum = str(configDriver().getConfig(filename=dir_path+'/serielNum.json')["deviceInfo"][0]["serielNum"])
        apiKey=configDriver().getConfig(filename=dir_path+'/config.json')["owmApiKey"]
        try:
            owm = pyowm.OWM(apiKey) # TODO: Replace <api_key> with your API key
            owmMgr = owm.weather_manager()

            arizona = owmMgr.weather_at_place('Tucson, US')
            getWeather = arizona.weather
            outsideRaw = getWeather.temperature('fahrenheit')
            outside = round(float(outsideRaw['temp']), 1)

            now = datetime.datetime.now()
            lastUpdated = now.strftime("%H:%M:%S")
            print('Outside Last Updated...' + str(lastUpdated))
            dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum': serielNum, 'loc':'outside','temp':str(outside)})
            return outside
        except Exception as e:
            configDriver().prRed("Get Outside Error: " + str(e))
            pass

    def waterTemp(self):
        global globalUsername
        global globalPassword
        serielNum = str(configDriver().getConfig(filename=dir_path+'/serielNum.json')["deviceInfo"][0]["serielNum"])

        try:
            c, f = WaterProbeDriver().read_temp()

            water = f

            if (dbConnector().getDBInfo(index=2) == 'ACTIVE'):
                switch = True
            else:
                switch = False

            if water > float(dbConnector().getDBInfo(index=3)) and switch == True:
                msg = "Take off the damn pool cover the water temperature is " + str(round(water,1)) + "F" + " The outside temperature is " + str(self.getOutsideTemp()) + "F"
                dbConnector().sendEmail(msg)
                self.signal_to_emit.emit('statusLabel', 'DISABLED')
                dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum': serielNum, 'switch':'DISABLED'})

            waterTemp = round(water, 1)

            now = datetime.datetime.now()
            # GET TIME AND SET LABEL
            waterTempLastUpdated = now.strftime("%H:%M:%S %P")
            print('Water Last Updated...' + str(waterTempLastUpdated) + " " + str(waterTemp))

            self.signal_to_emit.emit('waterTempLabel', str(waterTemp))
            dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateTemp.php', pload={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum': serielNum, 'loc':'water','temp':str(waterTemp)})
        except Exception as e:
            configDriver().prRed('Get Water Temp Error: ' + str(e))
            pass

class hardwareDriverThreaded(QObject):
    def __init__(self, signal_to_emit, parent=None):
        super().__init__(parent)
        self.signal_to_emit = signal_to_emit

    @pyqtSlot()
    def executeThread(self):
        while True:
            try:
                self.switch()
            except Exception as e:
                print('Hardware Error: ' + str(e))

    def switch(self):
        global globalUsername
        global globalPassword
        serielNum = str(configDriver().getConfig(filename=dir_path+'/serielNum.json')["deviceInfo"][0]["serielNum"])
        try:
            button = GPIO.input(27)

            if button == False:
                led = GPIO.output(17, GPIO.HIGH)
                QtTest.QTest.qWait(3000)
                led = GPIO.output(17, GPIO.LOW)
                self.signal_to_emit.emit('statusLabel', 'ACTIVE')
                dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateSwitch.php', pload={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum': serielNum, 'switch':'ACTIVE'})
        except Exception as e:
            QtTest.QTest.qWait(1000)
            configDriver().prRed("Switch ERROR: " + str(e))
            pass

class poolbuddyOS(QMainWindow):
    # Signal for checking water/outside temp from CheckTempsThreaded
    tempThreadSig = pyqtSignal(str,str)
    def __init__(self, parent=None):
        global globalUsername
        global globalPassword
        super().__init__()
        self.w = None  # No external window yet.
        uic.loadUi(dir_path+'/PoolBuddyV2.ui', self)
        # Start CheckTempsThreaded
        self.tempsThreaded = CheckTempsThreaded(self.tempThreadSig)
        thread = QThread(self) 
        self.tempsThreaded.moveToThread(thread)
        thread.start()
        # Start date time thread
        self.dateTimeUpdate = GetDateAndTimeThreaded(self.tempThreadSig)
        dateTimeThread = QThread(self)
        self.dateTimeUpdate.moveToThread(dateTimeThread)
        dateTimeThread.start()
        # Start Hardware Thread
        self.hardwareUpdate = hardwareDriverThreaded(self.tempThreadSig)
        hardwareThread = QThread(self)
        self.hardwareUpdate.moveToThread(hardwareThread)
        hardwareThread.start()
        serielNum = str(configDriver().getConfig(filename=dir_path+'/serielNum.json')["deviceInfo"][0]["serielNum"])
        self.serielNumLabel.setText('Seriel: ' + str(serielNum))
        self.startStopBtn.clicked.connect(self.tempsThreaded.executeThread)
        self.startStopBtn.clicked.connect(self.dateTimeUpdate.executeThread)
        self.startStopBtn.clicked.connect(self.hardwareUpdate.executeThread)
        self.setMaxTempBtn.clicked.connect(lambda: dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/updateMaxTemp.php', pload={'pyUser':globalUsername, 'pyPass':globalPassword, 'serielNum':serielNum, 'waterTempMax':str(self.maxTempTxtBox.text())}))
        self.tempThreadSig.connect(self.updateGUI)
    
    @pyqtSlot(str,str)
    def updateGUI(self, label, text):
        getattr(self,label).setText(text)

class loginPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        uic.loadUi(dir_path+'/loginPage.ui', self)
        self.loginBtn.clicked.connect(self.login)
    
    def login(self):
        global globalUsername
        global globalPassword
        username = self.usernameTxtBox.text()
        password = self.passwordTxtBox.text()
        if(dbConnector().updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/login.php', pload={'pyUser':username,'pyPass':password}) == 'true'):
            self.close()
            globalUsername = username
            globalPassword = password
            configDriver().generateSerielNum(username=username, password=password)
            self.openWindow(poolbuddyOS)

    def openWindow(self, window):
        if self.w is None:
            self.w = window()
            self.w.show()

app = QApplication(sys.argv)
w = loginPage()
w.show()
app.exec()