# VERSION 0.54
# URL https://raw.githubusercontent.com/Sumiza/picoalarm/main/main.py

from machine import Pin, reset
import json

class LocalSettings():
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
            self.TELNYXPOSTHEADER = {'Authorization': self.TELNYXTOKEN}
            self.TELNYXGETURL = jfile.get('telnyxgeturl')

localdata = LocalSettings()

dipswitch = dict()

for switch, pin in enumerate([11,12,13,14]):
    dipswitch[switch+1] = Pin(pin,Pin.IN,Pin.PULL_UP)

forceconfig = False
try:
    with open('forceconfig','r') as file:
        forceconfig = True
    from os import remove
    remove('forceconfig')
except: pass

if dipswitch[1].value() == 0:
    from wifi import Wifi
    wifi = Wifi(localdata.SSID,
                localdata.PASSWORD,
                localdata.HOSTNAME,
                localdata.WIFILED,
                localdata.WIFITIMEOUT)
    wifi.connect()

    if wifi.isconnected():
        try:
            import settime
            settime.settime(retry = 5, backup = True)
        except: pass # dont need time

    if dipswitch[2].value() == 0 and wifi.isconnected():
        import update
        update.updateall()

    if (dipswitch[3].value() == 0 and wifi.isconnected()) or forceconfig:
        import config
        config.run()
        reset()

elif dipswitch[1].value() == 1:
    import network
    wifi = network.WLAN(network.AP_IF)
    wifi.config(hostname="PicoAlarm",key='AlarmPico1234')
    wifi.active(True)

    while wifi.active is False:
        pass

    if (dipswitch[3].value() == 0 and wifi.isconnected()) or forceconfig:
        import config
        config.run()
        reset()

if dipswitch[4].value() == 0:
    import time
    import asyncio
    import aiourlrequest
    from matrixkeypad import MatrixKeypad

    level = 1
    def logger(data):
        if level is None or level == 0:
            return
        elif level == 1:
            print(data)

    class Alarm():
        def __init__(self,keytype) -> None:
            self.armed = None
            self.last = None
            self.keypad = MatrixKeypad(keytype)
            self.arming = False

            #set pins
            # self.sensorpins = {sensor:Pin(sensor,Pin.IN,Pin.PULL_UP) for sensor,name in localdata.SENSORS.items()}
            self.sensorpins = dict()
            for sensor,name in localdata.SENSORS.items():
                sensor = int(sensor)
                if name is not None:
                    self.sensorpins[sensor] = (Pin(sensor,Pin.IN,Pin.PULL_UP))
            self.greenled = Pin(localdata.GREENLED,Pin.OUT,value=0)
            self.redled = Pin(localdata.REDLED,Pin.OUT,value=0)
            self.beeppin = Pin(localdata.BEEPPIN,Pin.OUT,value=0)
            self.hornpin = Pin(localdata.HORNPIN,Pin.OUT,value=0)

        def ledgreen(self, toggle):
            logger(f"ledgreen {toggle}")
            if toggle is True:
                self.ledred(False)
                self.greenled.value(1)
            elif toggle is False:
                self.greenled.value(0)

        def ledred(self,toggle):
            logger(f"ledred {toggle}")
            if toggle is True:
                self.ledgreen(False)
                self.redled.value(1)
            elif toggle is False:
                self.redled.value(0)
                
        def beep(self,toggle):
            logger(f"beep {toggle}")
            if toggle is True:
                self.beeppin.value(1)
            elif toggle is False:
                self.beeppin.value(0)
    
        async def arm(self,keypass,armtype):
            logger(f'arm {keypass} {armtype}')
            await asyncio.sleep(0.2) # wait for keypad to finish
            self.arming = True
            for _ in range(localdata.PINTIME):
                if self.armed is False and self.arming is True:
                    self.beep(True)
                    self.ledgreen(True)
                    await asyncio.sleep(0.5)
                    self.beep(False)
                    self.ledgreen(False)
                    await asyncio.sleep(0.5)
                else:
                    self.arming = False
                    break #stopped arming
            else:
                self.arming = False
                self.armed = True
                self.ledred(True)
                self.writestate('Armed',keypass,armtype)
                await self.notifyadmins()
                # Arming Done
        
        async def disarm(self,keypass,armtype):
            logger(f'disarm {keypass} {armtype}')
            self.arming = False
            self.armed = False
            self.ledgreen(True)
            self.beep(False)
            self.writestate('Disarmed',keypass,armtype)
            await self.notifyadmins()
            # Disarm Done
        
        def writestate(self,arm,keypass,armtype):
            now = time.localtime()
            humantime =  f'{now[3]:02d}:{now[4]:02d} {now[1]:02d}/{now[2]:02d}/{now[0]}'
            self.last = f'Alarm {arm} by {localdata.USERS[keypass]['name']} at {humantime} via {armtype}'
            logger(f'writestate {self.last}')
            with open('last','w') as file:
                file.write(self.last)

        async def notifyadmins(self):
            for values in localdata.USERS.values():
                if values['admin'] is True:
                    await self.sendmessage(self.last,values['phonenr'])

        async def trigger(self,whichpin):
            logger(f'trigger {whichpin}')
            self.beep(True)
            for _ in range(localdata.PINTIME):
                if self.armed is True:
                    await asyncio.sleep(1)
                else:
                    return # disarmed

            sendevery = 5*60 # every 5 minute
            sendcount = 0
            while self.armed is True:
                self.hornpin.value(1)
                sendcount -= 1
                if sendcount <= 0:
                    asyncio.create_task(self.sendalarm(whichpin))
                    sendcount = sendevery
                await asyncio.sleep(1)
            self.hornpin.value(0)
        
        async def sendalarm(self,whichpin):
            for values in localdata.USERS.values():
                if values['admin'] is True:
                    logger(f'sendalarm to {values['phonenr']}')
                    await self.sendmessage(f"Alarm trigged on {localdata.SENSORS[whichpin]}",values['phonenr'])
                    await self.call(values['phonenr'])
        
        async def sendmessage(self,message,number):
            logger(f'trigger sendmessage {message} {number}')
            message = {
                'from':localdata.TELNYXFROMNUMBER,
                'to':number,
                'text':message
            }
            try:
                res = await aiourlrequest.post(
                    localdata.TELNYXPOSTURL+'messages',
                    json=message,
                    headers=localdata.TELNYXPOSTHEADER,
                    readlimit=50)
                logger(res.text)
            except Exception as e:
                logger(e)

        async def call(self,number):
            logger(f'trigger call {number}')
            message = {
                'from':localdata.TELNYXFROMNUMBER,
                'to':number,
                'connection_id':str(localdata.TELNYXCALLID),
                'time_limit_secs': 30,
                'audio_url': localdata.ALARMAUDIO
            }
            try:
                res = await aiourlrequest.post(
                    localdata.TELNYXPOSTURL+'calls',
                    json=message,
                    headers=localdata.TELNYXPOSTHEADER,
                    readlimit=50)
                logger(res.text)
            except Exception as e:
                logger(e)
        
        async def scansensors(self) -> None|int:
            for pin, pinvalue in self.sensorpins.items():
                if pinvalue.value() == 1:
                    return pin
                await asyncio.sleep(0) #TODO test blocking
            return None
        
        async def doording(self):
            doortoggle = False
            logger('Starting doording')
            while True:
                if self.armed is False:
                    if self.sensorpins[localdata.DOORDING].value() == 1 and doortoggle is False:
                        logger(f'door opened {self.sensorpins[localdata.DOORDING].value()} {doortoggle}')
                        doortoggle = True
                        for _ in range(4):
                            self.beep(True)
                            await asyncio.sleep(0.1)
                            self.beep(False)
                            await asyncio.sleep(0.1)
                    elif self.sensorpins[localdata.DOORDING].value() == 0 and doortoggle is True:
                        logger(f'door closed {self.sensorpins[localdata.DOORDING].value()} {doortoggle}')
                        doortoggle = False
                await asyncio.sleep(0.1)

        async def checksensors(self):
            logger('Starting checksensor')
            while True:
                if self.armed is True:
                    respin = await self.scansensors()
                    if respin is not None and self.armed is True:
                        await self.trigger(respin)
                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(1)

        async def poolkeypad(self):
            curpass = '!!!!'
            while True:
                pushedkey = self.keypad.scan()
                if pushedkey is not None:
                    self.beep(True)
                    curpass += str(pushedkey)
                    await asyncio.sleep(0.3)
                    if pushedkey == '*':
                        self.checkconfigkey(curpass)
                    keypass = self.checkkey(curpass)
                    logger(f'pushed key {pushedkey} - curpass: {curpass}, checkkey {keypass}')
                    if keypass:
                        if self.armed is True or self.arming is True:
                            asyncio.create_task(self.disarm(keypass,'keypad'))
                        elif self.armed is False:
                            asyncio.create_task(self.arm(keypass,'keypad'))
                        curpass = '!!!!'
                    self.beep(False)
                await asyncio.sleep(0.01)
        
        def checkconfigkey(self,checkkey:str):
            for keypass in localdata.USERS.keys():
                keypass = ''.join([p+'*' for p in keypass])
                if keypass == checkkey[-len(keypass):]:
                    self.configreboot()
                    
        def configreboot(self):
            with open('forceconfig','w') as file:
                file.write('config')
                reset()

        def checkkey(self,checkkey:str):
            for keypass in localdata.USERS.keys():
                if keypass == checkkey[-len(keypass):]:
                    return keypass
        
        async def getsms(self):

            def parsesms(message:str) -> dict:
                try:
                    if message['data']['event_type'] != 'message.received':
                        return None
                    parseresponse = dict() 
                    parseresponse['fromnr'] = message['data']['payload']['from']['phone_number']
                    text = message['data']['payload']['text']
                    splitmess = text.split()
                    parseresponse['action'] = splitmess.pop(0).lower()
                    parseresponse['passkey'] = splitmess.pop(0)
                    return parseresponse
                except: return None

            def checkuser(parsed:dict) -> bool:
                if self.checkkey(parsed['passkey']) is None:
                    logger('failed key')
                    return False
                if localdata.USERS[parsed['passkey']]['admin'] is not True:
                    logger('failed admin')
                    return False
                if localdata.USERS[parsed['passkey']]['phonenr'] != parsed['fromnr']:
                    logger('failed from nr')
                    return False
                return True

            await asyncio.sleep(localdata.PINTIME/2) # trigger before pin trigger
            while True:
                checksleep = 30
                try:
                    res = await aiourlrequest.aiourlrequest(localdata.TELNYXGETURL)
                    res = res.json()
                    res = res.get('content',None)
                    logger(res)
                    if res is None:
                        continue
                    checksleep = 1
                    parsed = parsesms(res)
                    if parsed is None:
                        continue
                    logger(parsed)
                    if checkuser(parsed) is False:
                        continue

                    if parsed['action'] == 'disarm':
                        if self.armed is True:
                            asyncio.create_task(self.disarm(parsed['passkey'],'SMS'))
                            logger('disarming')
                        else:
                            await self.sendmessage(self.last,parsed['fromnr'])
                    elif parsed['action'] == 'arm':
                        if self.armed is False:
                            asyncio.create_task(self.arm(parsed['passkey'],'SMS'))
                            logger('arming')
                        else:
                            await self.sendmessage(self.last,parsed['fromnr'])
                    elif parsed['action'] == 'status':
                        await self.sendmessage(self.last,parsed['fromnr'])
                        logger('status')
                    else:
                        await self.sendmessage('Message not understood',parsed['fromnr'])
                        logger('other')

                except Exception as e:
                    logger(e) # connection and json issues
                    pass
                finally:
                    await asyncio.sleep(checksleep)
                        
        async def main(self):
            try:
                with open('last','r') as file:
                    self.last = file.read().strip()
                    laststatus = self.last.split()[1]
                    if laststatus == 'Armed':
                        self.armed = True
                        self.ledred(True)
                    elif laststatus == 'Disarmed':
                        self.armed = False
                        self.ledgreen(True)
            except: 
                self.armed = False # first run with no last file
                self.ledgreen(True)
                self.last = 'No last status found'

            logger(f"Starting {self.armed}")

            running = list()
            running.append(asyncio.create_task(self.getsms()))
            running.append(asyncio.create_task(self.poolkeypad()))
            running.append(asyncio.create_task(self.checksensors()))
            if localdata.DOORDING is not None:
                running.append(asyncio.create_task(self.doording()))
            
            while True:
                for task in running:
                    if task.done():
                        logger(f'{task} reset needed')
                        reset() # something went very wrong
                await asyncio.sleep(5)

    alarm = Alarm('4x4')
    asyncio.run(alarm.main())
