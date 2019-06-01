



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
