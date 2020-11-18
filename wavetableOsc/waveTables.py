import pyb
#from Frequency import Frequency
#from Amplitude import Amplitude
import '/utils.py'
from numpy import array
from numpy import zeros
from numpy import sin
from numpy import cos

def makeTables():
    tblSize = memTblLen+1 # extra bit is a guard bit for interpolation
    allTbls = zeros((numTbls,tblSize),dtype='double')
    sineTbl = allTbls[0]

    for i in range(memTblLen):
        sineTbl[i] = sin( ((((double)j)/(double)tblSize*PI*2))-PI )

    sineTbl[memTblLen] = sineTbl[0]

    for i in range(1,numTbls,1):
        tbl = allTbls[i]
        numPartials = 1 << i
        kGibbs = double((PI/(2*numPartials)))
        for k in range(numPartials):
            sineIdx = 0
            partial = k+1
            temp = double(cos(k*kGibbs))
            raisedCos = temp * temp
            ampl = ((double(raisedCos)/partial) # 1/n for i in range(N) is the formula for a sawtooth (fourier)
            for j in range(memTblLen):
                tbl[j] += ampl * sineTbl[sineIdx]
                sineIdx += partial
                if (sineIdx >= tblSize):
                    sineIdx -= tblSize

        tbl[memTblLen] = tbl[0]

    return allTbls
