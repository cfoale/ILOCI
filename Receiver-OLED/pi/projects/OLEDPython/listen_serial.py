import serial
from serial import SerialException #to be able to use Except SerialException:
from subprocess import Popen, PIPE
from os import path
from time import sleep

#declare rfcomm functions to manage the system rf comm device
def rfinit():
    #see if channel 22 has been added
    p=Popen('sdptool browse local', shell=True, stdout=PIPE)
    result = p.communicate()[0] #check to see if 'Serial Port' is present
    position = result.find('Channel: 22')
    if position > -1:
        print("Serial Port is already present")
    else:
        #this initializes bluetooth to be discoverable and adds serial channel 22
        Popen('sudo hciconfig hci0 piscan',shell=True)
        Popen('sudo sdptool add --channel=22 SP',shell=True)
        print("Serial Port channel 22 was added")
    return

def rfhangup():
    #this releases the comm port, if it exists, and returns
    Popen('sudo rfcomm release /dev/rfcomm0',shell=True,stdout=PIPE)
    return

def rflisten():
    #this opens a comm port on rfcomm0 channel 22, which is left running,
    p = Popen('sudo rfcomm listen /dev/rfcomm0 22 &',shell=True,stdout=PIPE)
    return

def rfshow():
    #this checks to see if a connection on rfcomm0 has been made
    #it returns a bool, True or False
    p = Popen('rfcomm show /dev/rfcomm0',shell=True,stdout=PIPE)
    result = p.communicate()[0]  #check the 1st tuple for the string returned
    position= result.find('connect') #does it contain connect?
    bool_connected = False
    if position > -1:
        bool_connected = True
    return bool_connected

def rfcommListen(timeout):
    start_count = 0  #counter to see if we have waited too long
    goodQ = False  # we return the value of this, True means we got connected
    #first hangup any connection
    rfhangup()
    #give the system and the remote a chance to do stuff
    sleep(1)

    #open the port on channel 22 and wait
    rflisten()

    #now wait for a connection

    while True:
        start_count = start_count +1
        if start_count > timeout:
            print('Listen for connection timed out. Hanging up')
            rfhangup()
            return False
        sleep(1)  #wait a second, so we dont use up too much cpu
        if rfshow():
            print('We are connected')
            break    #we are connected
    
    #see if the /dev/rfcomm0 path exists to prove we are connected
    bool_path_exists = path.exists('/dev/rfcomm0')
    print('rfcomm0 path is '+str(bool_path_exists))
    if bool_path_exists :
        ser = serial.Serial('/dev/rfcomm0', 9600)
    else :
        print('rfcomm0 was not created as expected')
        rfhangup()
        return False
        
    #rfcomm exists so open the serial port
    ser.open()
    #send an acknowlegement
    ser.write('Ready for data\n')
    #read the response - it will wait forever
    singleread = ser.readline()
    if singleread.find('data follows') > -1 :
        print(singleread)
        goodQ = True
    
    nbytes = ser.inWaiting()
    #print("inWaiting "+ str(nbytes))
    return (goodQ, ser)

##########################################################

rfinit()
bool_result, ser = rfcommListen(60)
if bool_result == False:
    print('nobody connected before timeout')
    print('releasing rfcomm0')
    rfhangup()
    exit()
    
timeout = 600
startcount = 0
while True:
    sleep(0.1)
    startcount = startcount + 1
    if startcount > timeout:
        ser.close()
        print('Timeout exceeded - closing')
        break
    try:
        nbytes = ser.inWaiting()
        if nbytes > 0:
            singleread = ser.readline()
            fnum = float(singleread)
            print(str(fnum))
            ser.write('\n')
            startcount = 0
    except IOError:
        print('connection was dropped')
        break
        
print('releasing rfcomm0')
rfhangup()


