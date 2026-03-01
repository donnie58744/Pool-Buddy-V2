from pool_buddy import DEFAULT
from pool_buddy.CustomTerminal import PrintColor
from pool_buddy import ConfigDriver
from time import sleep

try:
    import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(17, GPIO.OUT)
except ImportError as e:
    print(e)
class HardwareDriver():
    def __init__(self):
        self.settingsConfig=ConfigDriver(jsonFile=DEFAULT.configFilePath)
        self.resetSwitchPin = self.settingsConfig.getConfig()["ResetSwitchPin"]
        self.resetLEDPin = self.settingsConfig.getConfig()["ResetLEDPin"]

    def switch(self):
        try:
            button = GPIO.input(self.resetSwitchPin)

            if button == False:
                resetLED = GPIO.output(self.resetLEDPin, GPIO.HIGH)
                sleep(3)
                resetLED = GPIO.output(self.resetLEDPin, GPIO.LOW)
                return True
            return False
        except Exception as e:
            PrintColor.red("Switch ERROR: " + str(e))
            pass