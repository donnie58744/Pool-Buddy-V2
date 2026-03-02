import sys
import os
from pool_buddy_qt import DEFAULT
from pool_buddy_qt.ui_scripts import *
from pool_buddy.CustomTerminal import PrintColor

import platform, subprocess
machineOs = platform.system()
if (machineOs == 'Linux'):
    subprocess.check_call(["sudo", "apt", "install", "python3-pyqt5"])
    try:
        import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(17, GPIO.OUT)
    except ImportError as e:
        PrintColor.red(str(e))
from PyQt5.QtWidgets import QApplication
# Need this for pyQT resources
from pool_buddy_qt import resources

dir_path = os.path.dirname(os.path.realpath(__file__))
DEFAULT.root_dir=dir_path

app = QApplication(sys.argv)
w = LoginPageUI(root_dir=dir_path)
w.show()
sys.exit(app.exec_())