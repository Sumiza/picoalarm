# VERSION 0.01
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
        <br> <label for="">Wifi led: </label><br><input name="wifiled" type="number" placeholder="" value={ifnone(localdata.WIFILED)}>
        <br> <label for="">Wifi timeout: </label><br><input name="wifitimeout" type="number" placeholder="" value="{ifnone(localdata.WIFITIMEOUT)}">

        <h4>Sensor Settings:</h4>
        """
    for sen in localdata.SENSORS.items():
        res += f'<br> <label for="">Sensor {sen[0]}: </label><input name="sensor{sen[0]}" type="text" placeholder="Where is the sensor" value="{ifnone(sen[1])}">\n'
    
    numberofusers = len(localdata.USERS)
    res += '<h4>User Settings:</h4>'
    for count in range(numberofusers+5):
        try:
            user = localdata.USERS[count]
        except:
            user = {}
        def isadmin(admin):
            if admin:
                return 'checked'
            return ''
        res += f'''
        <label for="">Name: </label><input name="username_{count}" type="text" placeholder="User Name" value="{ifnone(user.get('name'))}">
        <label for="">Pin: </label><input name="userkey_{count}" type="text" placeholder="1234" value="{ifnone(user.get('pin'))}">
        <label for="">Phone Number: </label><input name="userphone_{count}" type="text" placeholder="+19055555555" value="{ifnone(user.get('phonenr'))}">
        <label for="">Admin</label> <input type="checkbox" name="useradmin_{count}" value="admin" {isadmin(user.get('admin'))}> <br>
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
            <br> <label for="">Wifi LED: </label><br><input name="wifiled" type="number" placeholder="16" value={ifnone(localdata.WIFILED)}>

        <br><br>
        <br> <label for="">PIN: </label><input name="keypin" type="text" placeholder="1234" required><br><br>
        <input type="submit" value="Submit"><br><br>
        </form></center></body></html>
        '''
    return res

def checkpin(pin):
    for userdata in localdata.USERS:
        if pin == userdata['pin'] and userdata['admin'] is True:
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
    print(request.form)
    def tonone(data):
        if data == '':
            return None
        return data
    
    if checkpin(request.form.get('keypin')) is False:
        return "Wrong pin data not saved", 200, {'Content-Type': 'text/html'}

    savejson = {'users':[],'sensors':{}}

    for k,v in request.form.items():
        k:str
        if k.startswith('user'):
            if k.startswith('username_'):
                name = tonone(v[0])
                if name is None:
                    continue
                usercount = k.split('_')[1]
                def admin(admin):
                    if admin: return True
                    return admin
                user = {'pin': request.form.get('userkey_'+usercount), 
                        'name': name, 
                        'phonenr': tonone(request.form.get('userphone_'+usercount)), 
                        'admin': admin(request.form.get('useradmin_'+usercount,False))}
                savejson['users'] = savejson['users'] + [user]
        elif k.startswith('sensor'):
            savejson['sensors'][k] = tonone(v[0])
        elif k == 'keypin':
            pass
        else:
            savejson[k] = tonone(tonumber(v[0]))
    print(savejson)
    with open('output.json','w') as file:
        file.write(json.dumps(savejson,indent=6))

    return 'Rebooting', 200, {'Content-Type': 'text/html'}

@app.route('/shutdown')
async def shutdown(request:Request):
    request.app.shutdown()
    return 'The server is shutting down...'

def run(port=80,debug=True):
    app.run(debug=debug,port=port)

if __name__ == '__main__':
    app.run(debug=False, port=80)
