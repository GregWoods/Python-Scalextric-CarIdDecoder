



def tests():
    print("start 3 in a row test")
    model = {}
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
 

