from pool_buddy import DEFAULT
from scripts import Web
from pool_buddy.CustomTerminal import PrintColor
import json, random, string, os
class ConfigDriver():
    def __init__(self, jsonFile):
        self.jsonFile = DEFAULT.root_dir+jsonFile
        self.dbConnector = Web
        pass

    def getConfig(self):
        try:
            # Open JSON file
            f = open(self.jsonFile)
            data = json.load(f)
            
            return data
        except Exception as e:
            PrintColor.red(str(e))
            return False
        
    def writeConfig(self, key, value):
        with open(self.jsonFile) as f:
            data = json.load(f)
            if key in data:
                del data[key]
                cacheDict = dict(data)
                cacheDict.update({key:value})
                with open(self.jsonFile, 'w') as f:
                    json.dump(cacheDict, f, indent=4)

    def createFile(self, filename):
        if not os.path.isfile(filename):
            with open(filename, 'w') as file:
                PrintColor.green(f"{file} Has Been Created!")
                file.close()

    def generateSerielNum(self,username,password):
        # Create Seriel Number File
        self.createFile(filename=self.jsonFile)
        try:
            retrivedSerielNum=self.getConfig()["deviceInfo"][0]["serielNum"]
        except TypeError:
            retrivedSerielNum=""
        if (retrivedSerielNum == ""):
            PrintColor.yellow('Making Seriel Number...')
            with open(self.jsonFile, 'w') as outfile:
                def randStr(chars = string.ascii_uppercase + string.digits, N=30):
                    return ''.join(random.choice(chars) for _ in range(N))
                serielNum = randStr()
                print(serielNum)

                # Send Seriel Number
                self.dbConnector.dbUpdate().info(url='https://www.quackyos.com/PoolBuddyWeb/scripts/createSerielNumEntry.php', pload={'pyUser':username, 'pyPass':password, 'serielNum':serielNum})

                # Output Seriel Number To File
                data = {
                    'deviceInfo' : [
                        {
                            'serielNum' : serielNum
                        }
                    ]
                }
                json.dump(data, outfile)
                PrintColor.green('Seriel Number Created!')