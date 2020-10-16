import pyb
#from Frequency import Frequency
#from Amplitude import Amplitude
import constants
import waveTables

wavTbls = makeTables()

phaseReg = 0
freqReg = 0
ampReg = 0
for sampleCt in range(memTblLen):
    freqReg = Frequency(sampleCt)
    ampReg = Amplitude(sampleCt)
    phaseReg += 2*freqReg
    phaseReg = phaseReg & phaseRegMask
    if (phaseReg >= 1.0):
        phaseReg -= 2.0
    elif (phaseReg < -1.0):
        phaseReg = -1.0

    value = Interp(sampleCt,sampleInterp,iTblIdx,tblInterp)
