from micropython import const
sampleRate = const(44100.00)      # in Hz
fNyquist = const(22050.00)
bitsInPhaseReg = const(24)
phaseRegMask = const(((1 << bitsInPhaseReg)-1)) # 0x00ffffff
bitsInMemAddr = const(12)      # top 12 bits used to index into wavetable, 2^12 = 4096
memTblLen = const((1 << bitsInMemAddr))  # 4096 data values in wavetable
wavTblBitRate = const(16)      # wavetable uses single precision floating point (16 bit samples)
bitsInAmpVal = const(16)       # 16 bit unsigned amplitude
numTbls = const(8)
PI = const(double(3.141592654))

def Frequency(sampCt,f=440.0):
    dFreq = double(f)
    #return int( (dFreq/sampleRate)*(1 << bitsInPhaseReg) )
    return dFreq/sampleRate

def Amplitude(sampCt,a=0.5):
    dAmp = double(a)
    #return int( dAmp * (1 << bitsInAmpVal) )
    return dAmp

def Interp(sampleCt,sampleInterp,iTblIdx,tblInterp):

    halfTheSamps = float(memTblLen)/2
    fSampleIdx = halfTheSamps + phaseReg*halfTheSamps
    iSampleIdx = int(fSampleIdx)
    sampleInterp = fSampleIdx - iSampleIdx

    flevel = 0.0 - log2(2*freqReg)
    iTblIdx = int(flevel)
    tblInterp = flevel - iTableIndex

    lowval = highval = 0
    if (flevel < 0):
        l = wavTbls[0][sampleCt]
        r = wavTbls[0][sampleCt+1]
        highval = left + (sampleInterp*(r-l))
    elif (flevel < numTbls):
        l = wavTbls[iTblIdx][sampleCt]
        r = table[iTblIdx][sampleCt+1]
        lowval = l + (sampleInterp*(r-l))
        l = wavTbls[iTblIdx+1][sampleCt]
        r = wavTbls[iTblIdx+1][sampleCt+1]
        highval = l + (sampleInterp*(r-l))
    else:
        l = wavTbls[iTblIdx][sampleCt]
        r = wavTbls[iTblIdx][sampleCt+1]
        lowval = l + (sampleInterp*(r-l))
        highval = phaseReg
        tblInterp = 0.875 #### wrooooong

    return lowval +(tblInterp*(highval-lowval))

def establishContact(serial):
    while (!serial.isconnected()):
        serial.send(255,timeout=500)
