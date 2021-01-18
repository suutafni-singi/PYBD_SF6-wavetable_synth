from micropython import const
from gc import collect,threshold,mem_free,mem_alloc
#from ulab import array,zeros,ones
#from ulab import uint16
from ulab import numpy as np
#from ulab import np.float as mufloat
from math import sin,cos,pi,log2,modf,trunc


class Wavetable(object):

    def __init__(self, numTables: int, addrBits: int, amplBits: int, phi: np.float = 0., a: np.float = pi/2) -> None:
        self._numTbls = const(numTables)
        #self._addrBits = const(addrBits)      # top 12 bits used to index into wavetable, 2^12 = 4096
        self._tblLen = const(1 << addrBits)  # 4096 data values in wavetable
        #self.amplBits = amplBits       # 12 bit unsigned amplitude
        self._maxAmp = const((1 << amplBits)-1)

        def _getTri(k: int, a: np.float = pi/2.) -> tuple([int,np.float]):
            return tuple([k+1, (2./(a*(pi-a)))*sin((k+1)*a)/((k+1)**2)])

        def _getSqr(k: int, a: np.float = 0.) -> tuple([int,np.float]):
            return tuple([2*k+1, 4/(pi*(2*k+1))])

        def _getSaw(k: int, a: np.float = 0.) -> tuple([int,np.float]):
            return tuple([k+1, 1./(k+1)])

        collect()
        threshold(mem_free() // 4 + mem_alloc())

        def _makeTables(phi: np.float, a: np.float, coefs: tuple([int,np.float])) -> np.array:
            _tbl = np.zeros((self._numTbls,self._tblLen+1),dtype=np.float)    # np.float array to maintain calculation precision
            res = np.zeros((self._numTbls,self._tblLen+1),dtype=np.int16)    # int16 for return result
            vtrunc = np.vectorize(trunc)
            newvec = np.array([0]*(self._tblLen+1),dtype=np.int16)

            for i in range(self._tblLen):
              _tbl[0,i] = sin((2*pi*i/self._tblLen)-phi)
            _tbl[0,self._tblLen] = _tbl[0,0]    # "safety bit" for use in linear interpolation

            for i in range(1,self._numTbls,1):
                collect()
                threshold(mem_free() // 4 + mem_alloc())
                numPartials = 1 << i    # double the number of partials as frequency decreases by an octave
                kGibbs = (pi/(2*numPartials))   # smooths gibbs phenomena at sawtooth peaks
                for k in range(numPartials):
                    n,coef = coefs(k,a)
                    sineIdx = 0
                    ampl = ((cos(k*kGibbs))**2)*coef
                    for j in range(self._tblLen):
                        _tbl[i,j] = _tbl[i,j] + ampl * _tbl[0,sineIdx]
                        sineIdx = (sineIdx+n) % self._tblLen
                _tbl[i,self._tblLen] = _tbl[i,0]

            for i in range(self._numTbls):  # normalize/discretize to ints between 0 & self._maxAmp
                collect()
                threshold(mem_free() // 4 + mem_alloc())
                a = np.max(_tbl[i,:])
                b = np.min(_tbl[i,:])
                _tbl[i,:] = (_tbl[i,:] - b )/(a - b)
                newvec = np.array(vtrunc(self._maxAmp*_tbl[i,:]),dtype=np.int16)
                res[i,:] = res[i,:] + newvec
            return res


        self.sawTbls = _makeTables(phi,a,_getSaw)
        collect()
        threshold(mem_free() // 4 + mem_alloc())

        self.sqrTbls = _makeTables(phi,a,_getSqr)
        collect()
        threshold(mem_free() // 4 + mem_alloc())

        self.triTbls = _makeTables(phi,a,_getTri)
        collect()
        threshold(mem_free() // 4 + mem_alloc())


    def _linterp(self, wavTbl: array, tIdx: int, sIdx: int, sInterp: np.float) -> np.float:
      sIdx %= self._tblLen
      l = wavTbl[tIdx,sIdx]
      r = wavTbl[tIdx,sIdx+1]
      return l + sInterp*(r-l)


    def getWaveform(self, wav: int) -> array:
        if wav == 0:
            return self.sawTbls[0,:].reshape((1,self._tblLen+1))
        elif wav == 1:
            return self.sawTbls
        elif wav == 2:
            return self.sqrTbls
        elif wav == 3:
            return self.triTbls


    def blinterp(self, wavTbl: array, numTbls: int, phReg: np.float, fReg: np.float) -> np.float:
        sInterp,sIdx = modf((self._tblLen/2.0)*(1.0+phReg)) # get fractional (sInterp) and integer (sIdx) sample indices
        sIdx = int(sIdx)

        flevel = -log2(fReg*(numTbls/2.)) # indicator which determines the proper table for a given pitch
        tInterp,tIdx = modf(flevel)       # get fractional and integer table indices
        tIdx = int(tIdx)

        LV = HV = 0
        if (flevel < 0.0):                                  # negative flevel indicates frequency > sampleRate/2 (highest frequencies)
            HV = self._linterp(wavTbl,0,sIdx,sInterp)
        elif (flevel < numTbls-1):                          # freq in normal range
            LV = self._linterp(wavTbl,tIdx,sIdx,sInterp)
            HV = self._linterp(wavTbl,tIdx+1,sIdx,sInterp)
        else:
            oct_cor = tIdx-numTbls+1
            LV = self._linterp(wavTbl,numTbls-1,(sIdx << oct_cor),sInterp)
            HV = self._linterp(wavTbl,numTbls-1,(sIdx << (oct_cor+1)),sInterp)
                              # for the lowest frequencies interpolate with base phasor
        return LV + tInterp*(HV-LV)
