from pool_buddy import DEFAULT
from pool_buddy import ConfigDriver
from pool_buddy.CustomTerminal import PrintColor
import glob
class WaterProbeDriver():
    def __init__(self):
        try:
            settingsConfig = ConfigDriver(jsonFile=DEFAULT.configFilePath)
            base_dir = '/sys/bus/w1/devices/'
            self.device_path = glob.glob(base_dir + settingsConfig.getConfig()["WaterSensorLocation"])[0] #get file path of sensor
        except IndexError:
            PrintColor.red('Cant Find Water Probe')
            self.device_path = ''
            pass

    def read_temp_raw(self):
        try:
            with open(self.device_path + '/w1_slave', 'r') as f:
                valid, temp = f.readlines()
            return valid, temp
        except Exception as e:
            PrintColor.yellow('Water Probe Error: ' + str(e))
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
            PrintColor.yellow('Water Probe Error: ' + str(e))
            pass