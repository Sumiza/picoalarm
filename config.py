# VERSION 0.14
# URL https://raw.githubusercontent.com/Sumiza/picoalarm/main/config.py

from microdot import Microdot, Request
import json
app = Microdot()

login = f'''
<!DOCTYPE html>
<html><head>
  <title>Alarm Login</title>
</head><body><center>
<h3>Login with pin</h3>
<form action="/" method="post">
  <input name="keypin" type="text" placeholder="1234" required> <br> <br> 
  <input type="submit" value="Submit">
</form></center></body></html>
'''
def tonumber(data:str) -> str|int:
    if data.isdigit():
        return int(data)
    return data

class Localsettings():
    def __init__(self) -> None:
        with open('settings.json','r') as file:
            jfile = json.loads(file.read())
            jfile:dict
            self.SSID = jfile.get('wifissid')
            self.PASSWORD = jfile.get('wifipass')
            self.HOSTNAME = jfile.get('wifihostname')
            self.WIFILED = jfile.get('wifiled')
            self.WIFITIMEOUT = jfile.get('wifitimeout')

            self.SENSORS = jfile.get('sensors')
            self.GREENLED = jfile.get('greenled')
            self.REDLED = jfile.get('redled')
            self.BEEPPIN = jfile.get('beeppin')
            self.HORNPIN = jfile.get('hornpin')
            self.PINTIME = jfile.get('pintime')
            self.DOORDING = jfile.get('doording')
            self.USERS = jfile.get('users')

            self.TELNYXFROMNUMBER = jfile.get('telyxfromnumber')
            self.TELNYXCALLID = jfile.get('telnyxcallid')
            self.ALARMAUDIO = jfile.get('telnyxalarmaudio')
            self.TELNYXPOSTURL = jfile.get('telnyxposturl')
            self.TELNYXTOKEN = jfile.get('telnyxbearer')
            self.TELNYXGETURL = jfile.get('telnyxgeturl')

localdata = Localsettings()

def makehtml():
    def ifnone(data):
        if data is None:
            data = ''
        return data
    res = f"""
        <!DOCTYPE html>
        <html><head>
        <title>Alarm Settings</title>
        </head><body><center>
        <h3>Change settings the system will restart after submission</h3>
        <form action="/settings" method="post">
            
        <h4>WIFI Settings:</h4>
        <label for="">Wifi ssid: </label><br><input name="wifissid" type="text" placeholder="wifi name" value="{ifnone(localdata.SSID)}">
        <br> <label for="">Wifi password: </label><br><input name="wifipass" type="text" placeholder="wifi password" value="{ifnone(localdata.PASSWORD)}">
        <br> <label for="">Hostname: </label><br><input name="wifihostname" type="text" placeholder="hostname for alarm" value="{ifnone(localdata.HOSTNAME)}">
        <br> <label for="">Wifi led: </label><br><input name="wifiled" type="text" placeholder="LED" value={ifnone(localdata.WIFILED)}>
        <br> <label for="">Wifi timeout: </label><br><input name="wifitimeout" type="number" placeholder="20" value="{ifnone(localdata.WIFITIMEOUT)}">

        <h4>Sensor Settings:</h4>
        <br> <label for="">Sensor 16: </label><input name="sensor16" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['16'])}">
        <br> <label for="">Sensor 17: </label><input name="sensor17" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['17'])}">
        <br> <label for="">Sensor 18: </label><input name="sensor18" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['18'])}">
        <br> <label for="">Sensor 19: </label><input name="sensor19" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['19'])}">
        <br> <label for="">Sensor 20: </label><input name="sensor20" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['20'])}">
        <br> <label for="">Sensor 21: </label><input name="sensor21" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['21'])}">
        <br> <label for="">Sensor 22: </label><input name="sensor22" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['22'])}">
        <br> <label for="">Sensor 26: </label><input name="sensor26" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['26'])}">
        <br> <label for="">Sensor 27: </label><input name="sensor27" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['27'])}">
        <br> <label for="">Sensor 28: </label><input name="sensor28" type="text" placeholder="Where is the sensor" value="{ifnone(localdata.SENSORS['28'])}">
        """

    res += '<h4>User Settings:</h4>'
    for key, value in localdata.USERS.items():

        def isadmin(admin):
            if admin:
                return 'checked'
            return ''
        res += f'''
        <label for="">Name: </label><input name="user_{key}" type="text" placeholder="User Name" value="{ifnone(value.get('name'))}">
        <label for="">Pin: </label><input name="user_{key}" type="text" placeholder="1234" value="{ifnone(key)}">
        <label for="">Phone Number: </label><input name="user_{key}" type="text" placeholder="+19055555555" value="{ifnone(value.get('phonenr'))}">
        <label for="">Admin</label> <input type="checkbox" name="user_{key}" value="admin" {isadmin(value.get('admin'))}> <br>
        '''
    for i in range(5):
        res += f'''
        <label for="">Name: </label><input name="user_blank{i}" type="text" placeholder="User Name" value="">
        <label for="">Pin: </label><input name="user_blank{i}" type="text" placeholder="1234" value="">
        <label for="">Phone Number: </label><input name="user_blank{i}" type="text" placeholder="+19055555555" value="">
        <label for="">Admin</label> <input type="checkbox" name="user_blank{i}" value="admin"> <br>
        '''
    res += f'''
        <h4>Telnyx Settings:</h4>
        <label for="">Token: </label><br><input name="telnyxbearer" type="text" placeholder="Bearer KEY018E...." value="{ifnone(localdata.TELNYXTOKEN)}">
        <br> <label for="">Webhookbin: </label><br><input name="telnyxgeturl" type="text" placeholder="https://webhookbin.net/v1/bin/1852..." value={ifnone(localdata.TELNYXGETURL)}>
        <br> <label for="">Telnyx Alarm : </label><br><input name="telnyxalarmaudio" type="text" placeholder="https://test.com/alarm.mp3" value={ifnone(localdata.ALARMAUDIO)}>
        <br> <label for="">Telnyx Call ID: </label><br><input name="telnyxcallid" type="text" placeholder="941776456655464.." value={ifnone(localdata.TELNYXCALLID)}>
        <br> <label for="">Telnyx Call From: </label><br><input name="telyxfromnumber" type="text" placeholder="+19055555555" value={ifnone(localdata.TELNYXFROMNUMBER)}>
            
        <h4>Other Settings:</h4>
            <label for="">Arming Time (seconds): </label><br><input name="pintime" type="number" placeholder="30" value={ifnone(localdata.PINTIME)}>
            <br> <label for="">Door Ding Sensor: </label><br><input name="doording" type="number" placeholder="16" value={ifnone(localdata.DOORDING)}>
            <br> <label for="">Red LED: </label><br><input name="redled" type="number" placeholder="16" value={ifnone(localdata.REDLED)}>
            <br> <label for="">Green LED: </label><br><input name="greenled" type="number" placeholder="16" value={ifnone(localdata.GREENLED)}>
            <br> <label for="">Horn Pin: </label><br><input name="hornpin" type="number" placeholder="16" value={ifnone(localdata.HORNPIN)}>
            <br> <label for="">Beep Pin: </label><br><input name="beeppin" type="number" placeholder="16" value={ifnone(localdata.BEEPPIN)}>

        <br><br>
        <br> <label for="">PIN: </label><input name="keypin" type="text" placeholder="1234" required><br><br>
        <input type="submit" value="Submit"><br><br>
        </form></center></body></html>
        '''
    return res

def checkpin(pin):
    if pin in localdata.USERS:
        if localdata.USERS[pin]['admin'] is True:
            return True
    return False

@app.route('/',methods=['GET','POST'])
async def index(request:Request):
    if request.method == 'POST' and request.form:
        if checkpin(request.form.get('keypin')):
            return makehtml(), 200, {'Content-Type': 'text/html'}
    return login, 200, {'Content-Type': 'text/html'}

@app.route('/settings',methods=['POST'])
async def settings(request:Request):
    # print(request.form)
    def tonone(data):
        if data == '':
            return None
        return data
    
    if checkpin(request.form.get('keypin')) is False:
        return "Wrong pin data not saved", 200, {'Content-Type': 'text/html'}

    savejson = {'users':{},'sensors':{}}

    for k,v in request.form.items():
        k:str
        if k.startswith('user'):
            if v[0] == '' or v[1] == '':
                continue
            admin = False
            if len(v) == 4: # has admin checked
                admin = True  
            savejson['users'][v[1]] = {"name": v[0],"phonenr": tonone(v[2]),"admin": admin}
        
        elif k.startswith('sensor'):
            savejson['sensors'][k.replace('sensor','')] = tonone(v[0])
        elif k == 'keypin':
            pass
        else:
            savejson[k] = tonone(tonumber(v[0]))

    savejson['telnyxposturl'] = localdata.TELNYXPOSTURL

    with open('settings.json','w') as file:
        file.write(json.dumps(savejson))
    request.app.shutdown()
    return 'Rebooting', 200, {'Content-Type': 'text/html'}

@app.route('/shutdown')
async def shutdown(request:Request):
    request.app.shutdown()
    return 'The server is shutting down...'

def run(port=80,debug=True):
    app.run(debug=debug,port=port)

if __name__ == '__main__':
    app.run(debug=False, port=80)
