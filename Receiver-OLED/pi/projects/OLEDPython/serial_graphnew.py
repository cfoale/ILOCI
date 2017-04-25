import serial
from serial import SerialException #to be able to use Except SerialException:
from subprocess import Popen, PIPE
from os import path
from time import sleep

##############################################################################

# Imports the necessary software for graphing
import gaugette.ssd1306
import sys
from math import sin      #imported sin for Foale funtion

#Imports necessary setup for GPIO input/output
import RPi.GPIO as GPIO



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
	text = 'Waiting for connection..'
	led.draw_text2(0,0,text,1)
	text2 = 'Press button to Quit'
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
		if GPIO.input(switch_pin) == False:  #see if button pushed to quit
			print('button pressed to quit!')
			led.clear_display()
			text = 'button pressed to quit!'
			led.draw_text2(0,0,text,1)
			text2 = 'Power cycle to restart!'
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
	print('Send Command')   # Temporary command response for testing - ICF
	ser.write('CMD1\n')		#an acknowledgement is always terminated with \n	
	#put some text on the display as to what we are doing
	led.clear_display()
	text = 'Saving recent history..'
	led.draw_text2(0,0,text,1)
	text2 = 'for IFI incorporation'
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

RESET_PIN = 15
DC_PIN    = 16
width = 128
height = 32

led = gaugette.ssd1306.SSD1306(reset_pin=RESET_PIN, dc_pin=DC_PIN)
led.begin()
led.clear_display()

GPIO.setmode(GPIO.BCM)
switch_pin = 23            #GPIO pin 23 is the input from the button
LED_out = 18
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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
	timeout = 36000
	startcount = 0
	history = [] #array for datapoints to go on graph, for 128 pixels wide
	scalefactor = 4.0 #multiplies datapoints to scale across 32 pixels of height
	for i in range(width):
		history.append(31)
	
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
				fnum = scalefactor * float(singleread)
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
				bOn = (oof > 5)  # this is our Out of Family threshhold
				if oof > 5:
					GPIO.output(LED_out, True)	#we are Out of Family - turn the light on
				if GPIO.input(switch_pin) == False:
					command(bOn)
					#wait for a response from sender the command is complete - TBD
					sleep(1)	#this has to be very short so that sender does not wait too long for a response, then hangsup
					led.clear_display() #prepare the display for normal graph
				else:
					ser.write('\n')
					
				startcount = 0
		except IOError:
			print('connection was dropped')
			#put some text on the display as to what we are doing
			led.clear_display()
			text = 'Connection was dropped'
			led.draw_text2(0,0,text,1)
			text2 = 'Push button to restart'
			led.draw_text2(0,16,text2,1)
			led.display()
			if GPIO.input(switch_pin) == False:  #see if button pushed to reboot
				Popen('sudo reboot', shell=True)
			
			
			#ser.close()
			break  
			

print('releasing rfcomm0')
rfhangup()
print(history)


