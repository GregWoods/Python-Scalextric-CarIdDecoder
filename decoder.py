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

    colors = ['red', 'blue', 'yellow', 'green', 'orange', 'grey']

    #set up the shared bins for all plots
    with apsw.Connection("carid-pulses-sqlite.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""select min(pulseWidth) * 1000000, max(pulsewidth) * 1000000 from pulses 
                              where pulseWidth < 1""")
            minPulseWidth, maxPulseWidth = cursor.fetchall()[0]
    print(minPulseWidth)
    print(maxPulseWidth)

    # Set figure width to 12 and height to 9
    plt.rcParams["figure.figsize"] = [15, 9]

    binWidth = 1       # 10uS (=0.000010S)
    bins = np.arange(minPulseWidth, maxPulseWidth + binWidth, binWidth)

    # up to 7 (exclusive)
    for carid in range(1,7):

        with apsw.Connection("carid-pulses-sqlite.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""select pulseWidth * 1000000 from pulses 
                                where pulseWidth < 1 and carId = """ + str(carid))
            plotData = cursor.fetchall()

            # tuple keyword ensures we iterate through the zip object, and [0] prevents a tuple inside a tuple
            if (len(plotData) > 0):
                xdata = tuple(zip(*plotData))[0]

                #  https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist.html
                plt.hist(x=xdata, bins=bins, rwidth=1, color=colors[carid-1])



    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    model = {
        "ploturl" : "static/plot-" + timestamp + ".png" 
    }



    plt.savefig(model["ploturl"])
    #  , dpi=None, facecolor='w', edgecolor='w',
    #          orientation='portrait', papertype=None, format=None,
    #          transparent=False, bbox_inches=None, pad_inches=0.1,
    #          frameon=None)
    #  plt.show()
    plt.close()

    return render_template('plot.html', **model)



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
        
# Flask
@app.before_first_request
def do_something_only_once():
    pass



# setup interrupt handler
wiringpi.wiringPiSetup()
wiringpi.pullUpDnControl(SENSOR, wiringpi.PUD_UP)
wiringpi.wiringPiISR(SENSOR, wiringpi.INT_EDGE_RISING, logMe)



if __name__ == "__main__":
    # make sure flask doesn't run this code again
    thread = Thread(target = saveData, args = ())
    thread.start()

    print("main thread READY!")

    # run Flask webserver
    app.run(host='0.0.0.0', port=8081, debug=False)     # debug=False prevents code firing twice (problematic for the saveData thread)
