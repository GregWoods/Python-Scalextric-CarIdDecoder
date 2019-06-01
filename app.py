from flask import Flask, render_template, request
from threading import Thread
import glob
import os

from decoder import settings
import decoder
import tests


app = Flask(__name__)



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


@app.route("/tests")
def tests():
    print("run tests")
    return render_template('test1.html', **model)


@app.route("/plot/latest")
def showGraph():
    plotPngs = glob.glob('./static/plot-*.png')
    latestPlot = max(plotPngs, key=os.path.getctime)
    print(latestPlot)

    model = {
        "ploturl" : latestPlot 
    }   
    # TODO: add "Refresh" button to plot.html
    return render_template('plot.html', **model)


@app.route("/plot/refresh")
def newPlot:
    pass



# Flask
@app.before_first_request
def do_something_only_once():
    pass




if __name__ == "__main__":
    thread = Thread(target = decoder.saveData, args = ())
    thread.start()

    print("main thread READY!")

    # run Flask webserver
    #   debug=False prevents code firing twice (problematic for the saveData thread)
    app.run(host='0.0.0.0', port=8081, debug=False)     
