import time
from threading import Thread
from time import sleep
import sys
import os.path
from datetime import date, datetime
import RPi.GPIO as GPIO


lastPerfCounter = 0.0


SENSOR = 22      #BCM pin 22 is WiringPi pin3. Use gpio readall for ascii digram of all pins



GPIO.setmode(GPIO.BCM)  
GPIO.setup(SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
#GPIO.add_event_detect(SENSOR, GPIO.BOTH, callback=logMe)  



# wait_for_edge() doen't block the Raspi, but it blocks this program, so 
#  may not be suitable for production code
try:  
    while True:
        GPIO.wait_for_edge(SENSOR, GPIO.BOTH)

        now = time.perf_counter()
        pulseDuration = (now - lastPerfCounter) * 1000 * 1000   # microSeconds

        if pulseDuration < 200:
            print(pulseDuration, "uS")

        lastPerfCounter = time.perf_counter()   #refetch the time to account for the long time it takes serial print to work        

    
except KeyboardInterrupt:  
    GPIO.cleanup()       # clean up GPIO on CTRL+C exit  

