

class algconsecutivematches:
    # constructor here
    carId = 0
    lastCarId = 0
    matches = 0
    CONSECUTIVE_MATCHES = 3
    #define pulse boundary widths here. use some sort of dispatcher???
    pulsewidths = {
        '1': () 

    }


    def calc_pulse_widths():
        pass
        # look at the database and calc pulse widths based on the sample data I currently have

        # or have a 

    def next(pulseWidth):
        

        if lastCarId > 0:
            lastCarId = carId

        carId = getCarId(pulseWidth)
        if carId == lastCarId:
            matches += 1

        if matches >= CONSECUTIVE_MATCHES:
            return carId    #confirmed carid
        else:
            return 0


    def getCarId(pulseWidth):
        pass



    '''
    overview
    --------
    sql query get list of samples
    iterate through them. each sample has a known CarId, so we want to see if we can reliably match it
    the algorithm will loop through each pulse in the sample, and feed the pulses one by one into the algorithm
      until it comes up with a match

    Then we compare the match to the recorded carId, and record the result in the database

    We can test all algorithms in the same loop. Results stored in DB. We use separate code to tabulate the results.
    
    pseudocode
    ----------

    loop samples
        test3inARow(listOfPulsesForOneSample)
        testAverageAll(listOfPulsesForOneSample)

    def test3inARow
        for pulses
            3inARowAlg(pulse)

    #must behave in a serial way (like an iterator)
    #Can a python function persist variables across calls????
    # no. use a class
    def 3inARowAlg(pulse)
        if new
            matches = 0
            lastcarid = empty
            carid = findcarid(pulse)
        elif
            lastcarid = carid
            carid = findcarid(pulse)
            
    #https://www.csestack.org/python-check-if-all-elements-in-list-are-same/

    '''
 

