import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

switch_pin = 23

GPIO.setup(18, GPIO.OUT)  #18 is output pin to LED
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


GPIO.output(18, True)

while True:
    if GPIO.input(switch_pin) == False:
        GPIO.output(18, False)
        time.sleep(0.2)
        
