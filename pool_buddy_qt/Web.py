from pool_buddy.CustomTerminal import PrintColor
import requests

class dbCredentials:
    def __init__(self,username,password):
        self.username = username
        self.password = password

class dbConnector(dbCredentials):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    def __init__(self, login:dbCredentials):
        super().__init__(login.username, login.password)

    def get(self, index, serielNum):
        try:
            r = requests.post('https://www.quackyos.com/PoolBuddyWeb/scripts/getTemps.php', headers=self.headers, data={'pyUser':self.username, 'pyPass':self.password, 'serielNum': serielNum})
            jsonResponse = r.json()
            return jsonResponse[index]
        except Exception as e:
            PrintColor.red('Get DB Info Failed: ' + str(e))
            pass

    def update(self, url, pload:dict):
        try:
            pload['pyUser']=self.username
            pload['pyPass']=self.password
            r = requests.post(url, data=pload, headers=self.headers)
            return r.text
        except Exception as e:
            PrintColor.red('Update DB Info Failed: ' + str(e))
            pass

class Email:
    def send(self,message,emailNotifyList):
        if (emailNotifyList):
            for emailAddress in emailNotifyList:
                self.updateDBInfo(url='https://www.quackyos.com/PoolBuddyWeb/scripts/sendmail.php', pload={'address': emailAddress,'message':message})
                print(emailAddress)