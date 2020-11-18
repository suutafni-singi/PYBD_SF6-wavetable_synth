from micropython import const
from ulab import log2, uint16, float

sampleRate = const(48000)      # in Hz
fNyquist = const(24000)
bitsInPhaseReg = const(24)
phaseRegMask = const(((1 << bitsInPhaseReg)-1)) # 0x00ffffff
bitsInMemAddr = const(12)      # top 12 bits used to index into wavetable, 2^12 = 4096
memTblLen = const((1 << bitsInMemAddr))  # 4096 data values in wavetable
wavTblBitRate = const(24)      #
bitsInAmpVal = const(24)       # 16 bit unsigned amplitude
=======
wavTblBitRate = const(16)      #
bitsInAmpVal = const(16)       # 16 bit unsigned amplitude
numTbls = const(8)
PI = const(3.141592654)


def Interp(phaseReg,freqReg):

    halfTheSamps = memTblLen >> 1
    fSampleIdx = halfTheSamps + phaseReg*halfTheSamps  # fractional sample index
    iSampleIdx = uint16(fSampleIdx)                       # integer sample index
    sampleInterp = fSampleIdx - iSampleIdx             # the difference

    flevel = 0.0 - log2((freqReg << 2))
    iTableIdx = uint16(flevel)
    tblInterp = flevel - iTableIdx

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
        tblInterp = 1.0-(freqReg/(1 << (numTbls+2))

    return lowval +(tblInterp*(highval-lowval))
