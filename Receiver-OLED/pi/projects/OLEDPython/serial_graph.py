#IFIc Version 2.4 corresponding to IFIb Version 2.3  3/8/16 - cmf
#changed oofthreshold =  16, and scalefactor = 31.
#log now collects the IFIb float value scaled by scalefactor

#IFIc Version 2.3 corresponding to IFIb Version 2.3  3/1/16 - cmf
#changed oofthreshold =  16, and scalefactor = 32
import serial
from serial import SerialException #to be able to use Except SerialException:
from subprocess import Popen, PIPE
from os import path
from time import sleep
from datetime import datetime
from datetime import timedelta

##############################################################################

# Imports the necessary software for graphing
import gaugette.ssd1306
import sys
from math import sin      #imported sin for Foale function

#Imports necessary setup for GPIO input/output
import RPi.GPIO as GPIO

start_time = datetime.now()
def millis():
	dt =  datetime.now()-start_time
	ms = (dt.days * 24 *60 *60 +dt.seconds)*1000 + dt.microseconds/1000.0
	return ms

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
    p = Popen('rfcomm show /dev/rfcomm0',shell=True,stdout=PIPE,stderr=PIPE)
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
	#print('rfcommlisten: sleeping 60 sec after hangup')
	sleep(2)
	

	#open the port on channel 22 and wait
	rflisten()
	
	#put some text on the display as to what we are doing
	led.clear_display()
	text = 'Waiting for connect..'
	led.draw_text2(0,0,text,1)
	text2 = 'Press Pb1+Pb2 to Exit'
	led.draw_text2(0,16,text2,1)
	led.display()
	#print('finished rflisten')
	#now wait for a connection

	while True:
		start_count = start_count +1
		#print('while loop begun')
		if start_count > timeout:
			print('Listen for connection timed out. Hanging up')
			rfhangup()
			return False
		sleep(1)  #wait a second, so we dont use up too much cpu
		if GPIO.input(Pb1) == False:  #see if button pushed to Exit 
			if GPIO.input(Pb2) == False:
				print('Pb1 & Pb2 pressed!')
			led.clear_display()
			text = 'Pb1 & Pb2 pressed!'
			led.draw_text2(0,0,text,1)
			text2 = 'Powercycle to restart'
			led.draw_text2(0,16,text2,1)
			led.display()
			exit()
		#print('starting rfshow')
		if rfshow():
			print('We are connected')
			break    #we are connected

	#see if the /dev/rfcomm0 path exists to prove we are connected
	#print('past rfshow')
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

def command(bOn):   # function for sending a command back to data-recorder Pi upon button push - ICF
	print('Send Command1')   # Temporary command response for testing - ICF
	ser.write('CMD1\n')		#an acknowledgement is always terminated with \n	
	#log the event
	timems = millis()
	logfile.write(str(timems) + ' ' + '9999' + '\n')
	#put some text on the display as to what we are doing
	led.clear_display()
	text = 'Saving recent history..'
	led.draw_text2(0,0,text,1)
	text2 = 'Push button 2 for IFI incorporation'
	led.draw_text2(0,16,text2,1)
	led.display()
	#reconfigure the LED
	if bOn:	#this means the LED should be on already
		GPIO.output(LED_out, False)  #bOn ==True means we were out of family, so turn off the LED
		return
	GPIO.output(LED_out, True)  #bOn==False means we are in family, just want to send a command
	sleep(0.2)
	GPIO.output(LED_out, False)
	return
	
def command2(bOn):   # function for sending a command back to data-recorder Pi upon button push(new command will be update command) - ICF-cmf
	print('Send Command3')   # tells IFIb to pause sending, and only continues when it receives another pause command
	ser.write('CMD3\n')		#an acknowledgement is always terminated with \n
	#put some text on the display as to what we are doing
	led.clear_display()
	text = 'IFI Paused..'
	led.draw_text2(0,0,text,1)
	text2 = 'Press Pb1 IFI Update'
	led.draw_text2(0,16,text2,1)
	led.display()
	sleep(1)
	while True: #wait for either pb1 or pb2
		sleep(.1)
		try:
			nbytes = ser.inWaiting()
			if nbytes > 0:
				singleread = ser.readline()
				#now see what we got..it should always be a float number of one sort or another
				fnum = float(singleread)
				print('command2 got ' + str(singleread))
				ser.write('\n')		#an acknowledgement of any bytes received must be made
				if fnum == 8881.0:
					print('CMD3 pause terminated by IFI ')
					timems = millis()
					logfile.write(str(timems) + ' ' + '8881' + '\n')
					return
			if GPIO.input(Pb1) == False: # this is confirmation we want IFI Update
				print('Send Command3')   # tells IFIb to unpause sending, and only continues when it receives another pause command
				ser.write('CMD3\n')		#an acknowledgement is always terminated with \n
				text2 = 'Pb1 pressed...          '
				led.draw_text2(0,16,text2,1)
				led.display()
				sleep(2)  #time to release pb1 or else the shutdown routine will execute
				break
			if GPIO.input(Pb2) == False:
				print('Send Command3')   # tells IFIb to unpause sending, and only continues when it receives another pause command
				ser.write('CMD3\n')		#an acknowledgement is always terminated with \n
				return
					
		except IOError:
			print("IO error in command2()")
			return
	
	#first see if we are trying to do a regular shutdown using pb1 as well
	
	if GPIO.input(Pb1) == False:
		logfile.close()
		led.clear_display()
		text = 'Both pbs pressed..'
		led.draw_text2(0,0,text,1)
		text2 = 'IFI Closed'
		led.draw_text2(0,16,text2,1)
		led.display()
		exit()
	print('Send Command2')   # Temporary command response for testing - ICF
	ser.write('CMD2\n')		#an acknowledgement is always terminated with \n
	#log the event	
	timems = millis()
	logfile.write(str(timems) + ' ' + '8888' + '\n')
	#put some text on the display as to what we are doing
	led.clear_display()
	text = 'Updating IFI... '
	led.draw_text2(0,0,text,1)
	text2 = 'Please wait > 2 mins'
	led.draw_text2(0,16,text2,1)
	led.display()
	#reconfigure the LED
	if bOn:	#this means the LED should be on already
		GPIO.output(LED_out, False)  #bOn ==True means we were out of family, so turn off the LED
	GPIO.output(LED_out, True)  #bOn==False means we are in family, just want to send a command
	sleep(0.2)
	GPIO.output(LED_out, False)
	#now wait for a response. It is possible another number will be received, that was sent by IFI
	#before it received the CMD2 command, so we need to handle that
	sleep(2) #should be enough for any present to be received
	print("Command2 done waiting for bytes")
	while True:
		sleep(0.1)
		try:
			nbytes = ser.inWaiting()
			if nbytes > 0:
				singleread = ser.readline()
				ser.write('\n')		#an acknowledgement of any bytes received must be made
				#now see what we got..it should always be a float number of one sort or another
				fnum = float(singleread)
				print('command2 got ' + str(singleread))
				if fnum == 8888.0:
					print('CMD2 is complete')
					timems = millis()
					logfile.write(str(timems) + ' ' + '8888' + '\n')
					break
				
		except IOError:
			print("IO error in command2()")
			return
	return
	
	
### function added to draw vertical lines by CMF
def line(i,j,k,bLed):  #draw a line from (i,j) to (i+1,k)
	m = (j+k)/2		#this is the mid point in height between the start y and end y
	if k > j:		#going up 
		for l in range(j,m+1):	#starting at j, above i, go up to m
			led.draw_pixel(i,l, bLed)	#draw the pixels up half way
		for l in range(m+1,k+1):
			led.draw_pixel(i+1,l, bLed)	#draw the remaining pixes on step over in i
		return
	if k < j:		#going down
		for l in range(j, m, -1):	#starting at j, decrease down to m
			led.draw_pixel(i,l, bLed)
		for l in range(m, k-1, -1):	#starting half way down, decrease down to k, one i over
			led.draw_pixel(i+1,l, bLed)
		return
	if j==k:		#just draw pixels horizontally next to each other
		led.draw_pixel(i,j, bLed)
		led.draw_pixel(i+1, k, bLed)
	return
	
def testline(): #test the line function
	led.clear_display()
	lh = 21
	history = range(0,31,3)+range(31,-1,-3)
	for i in range(0,lh):
		line(i,history[i],history[i+1], True)
	sleep(1)
	for i in range(0,lh):
		line(i,history[i],history[i+1], False)
	#check the OLED has no lines :-)  - CMF
	led.clear_display()
	return

########################END OF FUNCTION DEFINITIONS##################################

print('start')
# Sets up our pins and creates variables for the size of the display. If using other size display you can easily change them.
#get the next log file number
lognumberfile = open('/home/pi/projects/OLEDPython/lognumber.txt','r')
lognumberstr = lognumberfile.readline()
#increment the  next log file number
nextlognumber = int(lognumberstr) +1
#write the next lognumber to the file
lognumberfile.close()
lognumberfile = open('/home/pi/projects/OLEDPython/lognumber.txt','w')
lognumberfile.write(str(nextlognumber)+'\n')
lognumberfile.close()
#setup the logfile name
logfilename = '/home/pi/projects/OLEDPython/ifilog' + str(int(lognumberstr)) + '.txt' 
print('Using log file ' + logfilename)
logfile = open(logfilename,'w')

RESET_PIN = 15
DC_PIN    = 16
width = 128
height = 32

led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
led.clear_display()

GPIO.setmode(GPIO.BCM)
Pb1 = 24    #CMF switched pb's 2/11/16        #GPIO pin 23 is the input from button 1 for restarting program upon disconnect, or sending 'save data for IFI' command back to data recorder - ICF
Pb2 = 23    #CMF switched pb's       #GPIO pin 24 is input from button 2 for reboot command to reboot data recorder - ICF
LED_out = 18
GPIO.setup(Pb2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Pb1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_out, GPIO.OUT)      #GPIO pin 18 is the output to the LED

#RUN = True #Variable that keeps program running until final exception

for x in range(width):

	#print(x)
	fx = float(x)
	y = (16 * sin((fx/128)*6.28) +16)
	iy = int(y)
	#print(iy)
	
	led.draw_pixel(x,iy, True)
	
led.display()
print('Display initialized')
#initialize LED on count down timer to be 0, so the light will not be on
ledoncountdowntimer = 0; 
#initialize the out of family threshold compared to max scale of 32
oofthreshold = 16 # 3/1/16 -cmf v 2.3
GPIO.output(LED_out, False)   #make sure the LED is off

while True:
	rfinit()
	#Listen for connection
	bool_result, ser = rfcommListen(3600)
	if bool_result == False:
		print('nobody connected before timeout')
		print('releasing rfcomm0')
		rfhangup()
		exit()
	
	led.clear_display()
	timeout = 300  #roughly 25s delay
	startcount = 0
	history = [] #array for datapoints to go on graph, for 128 pixels wide
	scalefactor = 31.0 #multiplies received normalized datapoints for display - height is 31
	for i in range(width):
		history.append(31)  #fills the history array with max values, which is a line at the bottom of the display
#initialization is done, now get data
	while True:
		sleep(0.1)
		startcount = startcount + 1
		if startcount > timeout:
			ser.close()
			print('Timeout exceeded - closing')
			break
		led.display()
		try:
			nbytes = ser.inWaiting()
			if nbytes > 0:
				singleread = ser.readline()
				print(singleread)
				timems = millis()
				fnum = scalefactor * float(singleread)
				logfile.write(str(timems) + ' ' + str(fnum) + '\n') #Version 2.4 - 3/8/16 -cmf
				inum =31 - int(fnum)
				
				if inum > 31 :
					inum = 31
					
				if inum < 0:
					inum = 0
					
				oof = (31 - inum)               # Out Of Family scaled 0 - 31
				print(str(fnum)+' ' + str(oof)) #our debug output
				for i in range(width-1):
					line(i,history[i],history[i+1],False) #undraw the old pixels
					
				history.pop(0) #remove the oldest value
				history.append(inum) #add the new value to history
				
				for i in range(width-1):
					#led.draw_pixel(i,history[i], True) #draw the new value as a pixel
					line(i,history[i],history[i+1],True)
					
				# This is the sending acknowledgement
				bOn = (oof > oofthreshold)  # this is our Out of Family threshhold
				if oof > oofthreshold:
					GPIO.output(LED_out, True)	#we are Out of Family - turn the light on
					ledoncountdowntimer = 120; #for the time the data is on the display we will stay on before resetting, to attract attention to display
				if oof < oofthreshold and ledoncountdowntimer > 0:	#see if we should reset the LED
					ledoncountdowntimer = ledoncountdowntimer-1;
					if ledoncountdowntimer == 0:	#the data has scrolled off the display, so reset
						GPIO.output(LED_out, False)
				if GPIO.input(Pb1) == False:
					command(bOn)
					#wait for a response from sender the command is complete - TBD
					sleep(1)	#this has to be very short so that sender does not wait too long for a response, then hangsup
					led.clear_display() #prepare the display for normal graph
				if GPIO.input(Pb2) == False:
					command2(bOn)
					print("command2 done.  Back in the main loop..")
					#wait for a response from sender the command is complete - TBD
					sleep(1)	#this has to be very short so that sender does not wait too long for a response, then hangsup
					led.clear_display() #prepare the display for normal graph
				else:	#we either send a \n on its own, or preceded as a command (see above)
					ser.write('\n')
					
				startcount = 0
		except IOError:
			print('connection was dropped')
			#close the log file
			logfile.close()
			#put some text on the display as to what we are doing
			led.clear_display()
			text = 'Connection was dropped'
			led.draw_text2(0,0,text,1)
			text2 = 'Push Pb1 to restart'
			led.draw_text2(0,16,text2,1)
			led.display()
			while True:
				if GPIO.input(Pb1) == False:  #see if button pushed to reboot
					exit()
					
					#Popen('sudo reboot', shell=True)
			
			
			ser.close()
			break  
			

print('releasing rfcomm0')
rfhangup()
print(history)


