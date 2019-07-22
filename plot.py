# import numpy as np      # requires: sudo apt-get install libatlas-base-dev
# import matplotlib.pyplot as plt
import apsw     # Another Python SQLite Wrapper
from datetime import date, datetime



def getAllData
    # check the db to get date range and number of samples for ALL data
    # does a cached file exist for that date range and samples count? (filename /data/fromDate-ToDate-NumberOfSamples.js)

    # if not, generate it
    allDataJson = createAllDataJson()

    # save it to /data folder (pref gzipped)

    # stream (if poss) the data from the /data/20190101-20190630-12233.js as the response
    
    # save it, gzipped


    # return the data. (We pref need to stream this directly as the response rather than poss it around in memory)
    #   maybe that bit is done in app.py
    return allDataJson



# TODO: it would be better to stream this straight to the file system (pref as gzipped file)
# try   https://realpython.com/read-write-files-python/
def createAllDataJson():
    output = []

    # up to 7 (exclusive)
    for carid in range(1,7):

        with apsw.Connection("carid-pulses-sqlite.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""select round(pulseWidth * 1000000, 0) from pulses 
                                where pulseWidth < 1 and carId = """ + str(carid))
            plotData = cursor.fetchall()

            # tuple keyword ensures we iterate through the zip object, and [0] prevents a tuple inside a tuple
            if (len(plotData) > 0):
                d = {
                        'carid': carid,
                        'data': tuple(zip(*plotData))[0]
                    }
                output.append(d)
    return output


'''
def generate():
    # generate png here, save it to temp folder, then pass the name of the png to the template

    colors = ['red', 'blue', 'yellow', 'green', 'orange', 'grey']

    #set up the shared bins for all plots
    #  Now we know the range of values, we hardcode the plot size to make reading it easier
    # with apsw.Connection("carid-pulses-sqlite.db") as conn:
    #        cursor = conn.cursor()
    #        cursor.execute("""select min(pulseWidth) * 1000000, max(pulsewidth) * 1000000 from pulses 
    #                          where pulseWidth < 1""")
    #        minPulseWidth, maxPulseWidth = cursor.fetchall()[0]
    minPulseWidth = 100
    maxPulseWidth = 500
    print(minPulseWidth)
    print(maxPulseWidth)
    
    # pixels / dpi
    imgWidth = 1200 / 96    
    imgHeight = 800 / 96

    # Set figure width to 12 and height to 9
    plt.rcParams["figure.figsize"] = [imgWidth, imgHeight]

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
    '''

