import time
from threading import Thread
from time import sleep
from flask import Flask, render_template, request
import sys
import os.path
import apsw     # Another Python SQLite Wrapper
from datetime import date, datetime
import wiringpi
import numpy as np      # requires: sudo apt-get install libatlas-base-dev
import matplotlib.pyplot as plt


app = Flask(__name__)


# global variables
settings = {
    "record" : True,
    "carId" : 1,
    "chip" : "G", 
    "firmware" : "icp40"
}

logSize = 7000
myLog = []
logCounter = 0


SENSOR = 3      #WiringPi pin3. Use gpio readall for ascii digram of all pins

lastPerfCounter = 0.0

SHORTPULSEMIN = 0.000030  # 30ms or 0.00003s or 30000ns
SHORTPULSEMAX = 0.000070
LONGPULSEMIN =  0.000100
LONGPULSEMAX =  0.000500
RECORDINGDURATION = 1          # no pulses after X seconds, write pulses to log file

shortPulseCount = 0
shortPulseTotal = 0

longPulseCount = 0
longPulseTotal = 0
longPulseMinValue = LONGPULSEMAX
longPulseMaxValue = LONGPULSEMIN

saveAfterTimestamp = 0
IDLE_BEFORE_SAVE = 3        # 3 seconds when testing with a pushbutton. Needs to be < 1 second when testing carIds, and much shorter if this code is ever used for lapcounting etc.



@app.route("/")
def main():
    # Pass the settings data into the template main.html and return it to the user
    return render_template('cariddecoder_main.html', **settings)

      
@app.route("/record/on")
def recordOn():
    global settings
    settings["record"] = True
    print(settings["record"])
    return "OK"


@app.route("/record/off")
def recordOff():
    global settings
    settings["record"] = False
    print(settings["record"])
    return "OK"


@app.route("/carid/<carId>")
def setCarId(carId):
    global settings
    settings["carId"] = carId
    print(settings["carId"])
    return "OK"


@app.route("/chip/<chip>")
def setChip(chip):
    global settings
    settings["chip"] = chip
    print(settings["chip"])
    return "OK"


@app.route("/firmware/<firmware>")
def setFirmware(firmware):
    global settings
    settings["firmware"] = firmware
    print(settings["firmware"])
    return "OK"


@app.route("/plot")
def showGraph():
    # generate png here, save it to temp folder, then pass the name of the png to the template

    # Simple SQL to group the pulseWidths into bins:
    #   select round(pulseWidth, 2), count(*) from pulses
    #   group by round(pulseWidth, 2);

    n, bins, patches = plt.hist(x=myLog, bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
    # plt.grid(axis='y', alpha=0.75)
    # plt.xlabel('Value')
    # plt.ylabel('Frequency')
    # plt.title('My Very Own Histogram')
    # plt.text(23, 45, r'$\mu=15, b=3$')
    # maxfreq = n.max()

    # Set a clean upper y-axis limit.
    # plt.ylim(top=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)            

    plt.savefig("myplot.png")
    # , dpi=None, facecolor='w', edgecolor='w',
    #         orientation='portrait', papertype=None, format=None,
    #         transparent=False, bbox_inches=None, pad_inches=0.1,
    #         frameon=None)
    plt.show()
    plt.close()

    plotdata = {"ploturl" : "myplot.png"}
    return render_template('plot.html', **plotdata)

def logMe():
    global logCounter
    global myLog
    global lastPerfCounter

    # thread.stop()
    now = time.perf_counter()
    pulseDuration = now - lastPerfCounter
    pulseLogic = wiringpi.digitalRead(SENSOR)

    print("pulse detected", pulseLogic)

    # if pulse < LONGPULSEMAX and pulse > SHORTPULSEMIN:
    if logCounter <= logSize and lastPerfCounter > 0:
        myLog.append((pulseDuration, pulseLogic))

    lastPerfCounter = now
    logCounter += 1
    
    # every time a pulse is detected, set the saveAfterTimestamp to now + x seconds
    #   this ensures that the lengthy save process is idle until capturing has been 
    #   stopped for x seconds
    global saveAfterTimestamp 
    saveAfterTimestamp = time.perf_counter() + IDLE_BEFORE_SAVE


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
                print("INSERT finished")
                 
            else:
                myLog.clear()
                print("No insert, Recording is OFF")
        
# Flask
@app.before_first_request
def do_something_only_once():
    pass



# setup interrupt handler
wiringpi.wiringPiSetup()
wiringpi.pullUpDnControl(SENSOR, wiringpi.PUD_UP) ;
wiringpi.wiringPiISR(SENSOR, wiringpi.INT_EDGE_BOTH, logMe)



if __name__ == "__main__":
    # make sure flask doesn't run this code again
    thread = Thread(target = saveData, args = ())
    thread.start()

    print("main thread READY!")

    # run Flask webserver
    app.run(host='0.0.0.0', port=8081, debug=False)     # debug=False prevents code firing twice (problematic for the saveData thread)
