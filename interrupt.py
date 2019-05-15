import time
from threading import Thread
from time import sleep
import sys
import os.path
from datetime import date, datetime
import wiringpi


lastPerfCounter = 0.0


SENSOR = 3      #WiringPi pin3. Use gpio readall for ascii digram of all pins


SHORTPULSEMIN = 0.000030  # 30ms or 0.00003s or 30000ns
LONGPULSEMAX =  0.000500


def logMe():
    global lastPerfCounter
    

    now = time.perf_counter()
    pulseDuration = now - lastPerfCounter

    if pulseDuration < LONGPULSEMAX and pulseDuration > SHORTPULSEMIN:
        # alert when we see a short pulse
        if pulseDuration < 0.000100:
            print("short pulse: ", pulseDuration)

    lastPerfCounter = now






# setup interrupt handler
wiringpi.wiringPiSetup()
# wiringpi.pullUpDnControl(SENSOR, wiringpi.PUD_UP) ;
wiringpi.wiringPiISR(SENSOR, wiringpi.INT_EDGE_SETUP, logMe)



# Keep the program running. Not sure if this is the correct way!

while True:
    time.sleep(1)     # relinquish control to other threads
