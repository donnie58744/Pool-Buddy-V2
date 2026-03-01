from pool_buddy.CustomTerminal import PrintColor
from time import sleep

try:
    import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(17, GPIO.OUT)
except ImportError as e:
    print(e)
class HardwareDriver():
    def __init__(self, reset_switch_pin, reset_led_pin):
        self.reset_switch_pin = reset_switch_pin
        self.reset_led_pin = reset_led_pin

    def switch(self):
        try:
            button = GPIO.input(self.reset_switch_pin)

            if button == False:
                resetLED = GPIO.output(self.reset_led_pin, GPIO.HIGH)
                sleep(3)
                resetLED = GPIO.output(self.reset_led_pin, GPIO.LOW)
                return True
            return False
        except Exception as e:
            PrintColor.red("Switch ERROR: " + str(e))
            pass