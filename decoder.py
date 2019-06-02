import time
from time import sleep
import sys
import os.path
import apsw     # Another Python SQLite Wrapper
from datetime import date, datetime
import wiringpi


# global variables
settings = {
    "record" : True,
    "carId" : 6,
    "chip" : "G", 
    "firmware" : "icp40"
}

logSize = 10000
myLog = []
logCounter = 0

SENSOR = 3      #WiringPi pin3. Use gpio readall for ascii digram of all pins

lastPerfCounter = 0.0

LONGPULSEMIN =  0.000100
LONGPULSEMAX =  0.000500

shortPulseCount = 0
shortPulseTotal = 0

longPulseCount = 0
longPulseTotal = 0

saveAfterTimestamp = time.time()      # tracks the future time when we expect a database write to occur. Uses Epoch time (1970)
IDLE_BEFORE_SAVE = 1        # no pulses after X seconds, write pulses to database



def logMe():
    global logCounter
    global myLog
    global lastPerfCounter

    # thread.stop()
    now = time.perf_counter()
    pulseDuration = now - lastPerfCounter

    # pulseLogic = wiringpi.digitalRead(SENSOR)     # too slow. Cannot detect ID 1,2 if this line is present
    pulseLogic = 99

    #if LONGPULSEMIN < pulseDuration < LONGPULSEMAX:
    if pulseDuration < LONGPULSEMAX:
        if logCounter <= logSize and lastPerfCounter > 0:
            myLog.append((pulseDuration, pulseLogic))
            logCounter += 1

            # every time a pulse is detected, set the saveAfterTimestamp to now + x seconds
            #   this ensures that the lengthy save process is idle until capturing has been 
            #   stopped for x seconds
            global saveAfterTimestamp 
            saveAfterTimestamp = now + IDLE_BEFORE_SAVE

    lastPerfCounter = now
    


# runs in a separate process. Make sure it is idle most of the time
def saveData():
    global saveAfterTimestamp 
    
    with apsw.Connection("carid-pulses-sqlite.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS pulses (
                           id INTEGER PRIMARY KEY,
                           sampleId INTEGER,
                           created DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                           carid INTEGER, 
                           chip TEXT,
                           firmware TEXT, 
                           pulseWidth REAL,
                           pulseLogic INTEGER
                           )""")
        cursor.execute("SELECT MAX(sampleId) FROM pulses")
        sampleId = cursor.fetchone()[0]
        if sampleId is None:
            sampleId = 0

    print("saveData thread READY!")
    print("Next sampleId: ")
    print (sampleId)

    while True:
        time.sleep(1)     # relinquish control to other threads
        print('condition1: ', time.perf_counter() > saveAfterTimestamp, '. len(myLog): ', len(myLog))
        if (time.perf_counter() > saveAfterTimestamp 
            and len(myLog) > 0):

            if settings["record"] == True:
                
                global logCounter

                sampleId += 1

                sqlintro = "INSERT INTO pulses (sampleId, carid, chip, firmware, pulseWidth, pulseLogic) values \n"
                sqlvalues = []

                carId = settings["carId"]
                chip = settings["chip"]
                firmware = settings["firmware"]
                
                for (pulseWidth, pulseLogic) in myLog:
                    sqlvalues.append("('{}', '{}', '{}', '{}', '{}', '{}')".format(sampleId, carId, chip, firmware, pulseWidth, pulseLogic))
        
                sql = sqlintro + "\n, ".join(sqlvalues)

                cursor.execute(sql)        

                myLog.clear()
                logCounter = 0
                print('INSERT finished. CarId: ', carId, '. Last PulseWidth: ', pulseWidth, '. SampleID: ', sampleId)
                 
            else:
                myLog.clear()
                logCounter = 0
                print("No insert, Recording is OFF")
        

# setup interrupt handler
wiringpi.wiringPiSetup()
wiringpi.pullUpDnControl(SENSOR, wiringpi.PUD_UP)
wiringpi.wiringPiISR(SENSOR, wiringpi.INT_EDGE_RISING, logMe)
