import wiringpi
import time
import curses
import csv
import os.path
from curses import wrapper
import numpy as np      # requires: sudo apt-get install libatlas-base-dev
import matplotlib.pyplot as plt
import http.server
import socketserver
import os


# DON'T FORGET
# TO FIRE UP THE VIRTUAL ENVIRONMENT
#   cd development/carid-venv
#   ./bin\activate

logSize = 7000
myLog = []
logCounter = 0

SENSOR = 3

CSVFILE = "gregtest.csv"

lastPerfCounter = 0.0

SHORTPULSEMIN = 0.000030  # 30ms or 0.00003s or 30000ns
SHORTPULSEMAX = 0.000070
LONGPULSEMIN =  0.000100
LONGPULSEMAX =  0.000500
RECORDINGDURATION = 3          # no pulses after X seconds, write pulses to log file

shortPulseCount = 0
shortPulseTotal = 0

longPulseCount = 0
longPulseTotal = 0
longPulseMinValue = LONGPULSEMAX
longPulseMaxValue = LONGPULSEMIN

recording = False


PORT = 8000


def logMe():
    # state = wiringpi.digitalRead(SENSOR)
    # print(state)

    global recording
    global logCounter
    global myLog
    global lastPerfCounter

    now = time.perf_counter()
    pulse = now - lastPerfCounter

    # statusWin.clear()
    # statusWin.addstr(0, 3, "SPACE starts a " + str(RECORDINGDURATION) + " second test")

    # if pulse < LONGPULSEMAX and pulse > SHORTPULSEMIN:
    if logCounter <= logSize and lastPerfCounter > 0:
        myLog.append(pulse)

    lastPerfCounter = now
    logCounter += 1
    recording = True



def updateHelpUi(logCarId, logChip, logFirmware, logLaneChange):
    global helpWin
    helpWin.clear()
    helpWin.addstr(1, 3, "Before each test, set the CarId, Hardware version, Firmware values")
    helpWin.addstr(3, 3, "CarId: 1-6: ")
    helpWin.addstr(3, 37, str(logCarId))
    helpWin.addstr(4, 3, "Chip revision, F, G, H: ")
    helpWin.addstr(4, 37, str(logChip))
    helpWin.addstr(5, 3, "Firmware: 7=std, 8=v3.30, 9=v4.0: ")
    helpWin.addstr(5, 37, str(logFirmware))
    helpWin.addstr(6, 3, "Lane Change: X")
    helpWin.addstr(6, 37, str(logLaneChange))
    helpWin.refresh()


def updateStatusRecording():
    global statusWin
    statusWin.clear()
    statusWin.addstr(0, 0, "======================================================")
    statusWin.addstr(1, 0, "=====                LOGGING                     =====")
    statusWin.addstr(2, 0, "======================================================")
    statusWin.refresh()


def updateStatusWaiting():
    global statusWin
    statusWin.clear()
    statusWin.addstr(0, 3, "SPACE starts a " + str(RECORDINGDURATION) + " second test")
    statusWin.refresh()

    
def updateStatusMsg(msg):
    global statusWin
    statusWin.clear()
    statusWin.addstr(0, 0, msg)
    statusWin.refresh()


# Setup
wiringpi.wiringPiSetup()
wiringpi.pullUpDnControl(SENSOR, wiringpi.PUD_UP) ;
wiringpi.wiringPiISR(SENSOR, wiringpi.INT_EDGE_BOTH, logMe)



def threaded_function(arg):
    for i in range(arg):
        print("running")
        sleep(1)


if __name__ == "__main__":
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    thread.join()
    print("thread finished...exiting")


def main(stdscr):
    # initscr() is called behind the scenes when we call main using wrapper()
    global helpWin
    global statusWin

    helpWin = curses.newwin(7, 80, 0, 0)
    statusWin = curses.newwin(3, 80, 10, 0)

    global recording
    global myLog

    stdscr.refresh()

    logCarId = 1
    logChip = "G"
    logFirmware = "std"
    logLaneChange = False

    updateHelpUi(logCarId, logChip, logFirmware, logLaneChange)


    # start web server
    web_dir = os.path.join(os.path.dirname(__file__), 'web')
    os.chdir(web_dir)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    updateStatusMsg("serving at port: " + str(PORT))
    httpd.serve_forever()


    # Loop
    #  handles keypesses when not actively recording pulses,
    #  and writes to the csv once the recording has finished.
    while True:

        if recording == False:
            updateStatusWaiting()

            kb = stdscr.getkey()

            intkb = -1
            if kb.isdigit():
                intkb = int(kb)

            if intkb >= 1 and intkb <= 6:
                logCarId = kb
            elif intkb == 7:
                logFirmware = "std"
            elif intkb == 8:
                logFirmware = "3.3"
            elif intkb == 9:
                logFirmware = "4.0"
            elif kb == "f":
                logChip = "F"
            elif kb == "g":
                logChip = "G"
            elif kb == "h":
                logChip = "H"
            elif kb == "x":
                logLaneChange = not logLaneChange
            elif kb ==  " ":
                recording = True
                recordingTime = time.perf_counter()
                updateStatusRecording()

            updateHelpUi(logCarId, logChip, logFirmware, logLaneChange)
            
        else:
            #For an active recording, we do nothing here, so the ISR gets use of the processor

            if time.perf_counter() > recordingTime + RECORDINGDURATION:
                # The recording has just finished. Save it to CSV and visualise it
                with open(CSVFILE, 'a', newline='') as csvfile:
                    fieldnames = ['CarId', 'Firmware', 'LaneChange', 'PulseWidth']
                    logwriter = csv.DictWriter(csvfile, fieldnames)
                    if not os.path.exists(CSVFILE):
                        logwriter.writeheader()

                    for pulseWidth in myLog:
                        pulsedata = {
                            'CarId': logCarId,
                            'Firmware': logFirmware,
                            'LaneChange': logLaneChange,
                            'PulseWidth': pulseWidth
                        }
                        logwriter.writerow(pulsedata)
                
                updateStatusMsg("Creating Histogram")

                #Now create a histogram so we can plot a distribution
                #  https://realpython.com/python-histograms/#histograms-in-pure-python
                # hist, bin_edges = np.histogram(myLog)

                

                # An "interface" to matplotlib.axes.Axes.hist() method
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

                recording = False
                # return

        time.sleep(.05)




wrapper(main)