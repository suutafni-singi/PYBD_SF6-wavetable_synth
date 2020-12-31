from micropython import const,mem_info
from gc import collect,threshold,mem_free,mem_alloc
from ulab import array,zeros,ones,uint16
from ulab import vector
from math import sin,cos,pi,log2,modf



class Wavetable(object):

    def __init__(self, numTables: int, addrBits: int, amplBits: int, phi: float = 0., a: float = pi/2) -> None:
        self._numTbls = const(numTables)
        #self._addrBits = const(addrBits)      # top 12 bits used to index into wavetable, 2^12 = 4096
        self._tblLen = const(1 << addrBits)  # 4096 data values in wavetable
        #self.amplBits = const(amplBits)       # 12 bit unsigned amplitude
        self._maxAmp = const(1 << (amplBits-1))

        def _getTri(k: int, a: float = pi/2.) -> float:
            return (2./(a*(pi-a)))*sin(k*a)/(k**2)
        def _getSqr(k: int, a: float = 0.) -> float:
            if k % 2 == 0:
                return 0.
            return (4/(pi*k))
        def _getSaw(k: int, a: float = 0.) -> float:
            return 1./k

        collect()
        mem_info()
        print('----------------------------------------')
        print('Initial free: {} allocated: {}'.fornat(mem_free(),mem_alloc()))
        def _makeTables(self, phi: float, a: float, f) -> array:

            #allTbls.append(np.array(vector.floor((self._maxAmp/2.)*(_tbl[0,:]+np.ones(self._tblLen+1))),dtype=np.uint16).reshape((1,1025)))
            #for f in fList:
            _tbl = zeros((self._numTbls,self._tblLen+1))
            for i in range(self._tblLen):
              _tbl[0,i] = sin((2*pi*i/self._tblLen)-phi)
            _tbl[0,self._tblLen] = _tbl[0,0]
            sineTbl = _tbl[0,:]
            for i in range(1,self._numTbls,1):
                numPartials = 1 << i    # double the number of partials as frequency decreases by an octave
                kGibbs = (pi/(2*numPartials))   # smooths gibbs phenomena at sawtooth peaks
                for k in range(numPartials):
                    sineIdx = 0
                    n = k+1
                    ampl = ((cos(k*kGibbs))**2)*f(n,a)
                    for j in range(self._tblLen):
                        _tbl[i,j] = _tbl[i,j] + ampl * sineTbl[sineIdx]
                        sineIdx += n
                        if (sineIdx > self._tblLen):
                            sineIdx -= (self._tblLen)

                _tbl[i,self._tblLen] = _tbl[i,0]
            #    allTbls.append(array(vector.floor((self._maxAmp/2.)*((_tbl+ones((self._numTbls,self._tblLen+1))))),dtype=uint16))
            #return tuple(allTbls)
            return array(vector.floor(self._maxAmp*((_tbl+ones((self._numTbls,self._tblLen+1))))),dtype=uint16)
        collect()
        #threshold(gc.mem_free() // 4 + mem_alloc())
        print('_makeTables definition: {} allocated: {}'.format(mem_free(),mem_alloc()))

        self.sawTbls = self._makeTables(phi,a,_getSaw)
        print('_makeTables(sawTbls) free: {} allocated: {}'.format(mem_free(),mem_alloc()))
        collect()
        print('gc free: {} allocated: {}'.format(mem_free(),mem_alloc()))

        self.sqrTbls = self._makeTables(phi,a,_getSqr)
        print('_makeTables(sqrTbls) free: {} allocated: {}'.format(mem_free(),mem_alloc()))
        collect()
        print('gc free: {} allocated: {}'.format(mem_free(),mem_alloc()))

        self.triTbls = self._makeTables(phi,a,_getTri)
        print('_makeTables(triTbls) free: {} allocated: {}'.format(mem_free(),mem_alloc()))
        collect()
        print('gc free: {} allocated: {}'.format(mem_free(),mem_alloc()))
        print('----------------------------------------')
        mem_info(1)


    def getWavfrm(self, wav:int) -> array:
        if wav == 0:
            return self.sawTbls[0,:].reshape((1,self._tblLen+1))
        elif wav == 1:
            return self.sawTbls
        elif wav == 2:
            return self.sqrTbls
        elif wav == 3:
            return self.triTbls


    def _linterp(self, wavTbl: array, tIdx: int, sIdx: int, sInterp: float) -> float:
      _l = wavTbl[tIdx,sIdx]
      _r = wavTbl[tIdx,sIdx+1]
      return _l + sInterp*(_r-_l)


    def blinterp(self, wavTbl: array, numTbls: int, phReg: float, fReg: float) -> float:
        _sInterp,_sIdx = modf((self._tblLen >> 1)*(1.0+phReg))
        _sIdx = int(_sIdx)

        _flevel = -log2((4*fReg))
        _tInterp,_tIdx = modf(_flevel)
        _tIdx = int(min(_tIdx,numTbls-1))

        _LV = _HV = 0
        if (_flevel < 0.0):  #
            _HV = self._linterp(wavTbl,0,_sIdx,_sInterp)
        elif (_flevel < numTbls-1):
            _LV = self._linterp(wavTbl,_tIdx,_sIdx,_sInterp)
            _HV = self._linterp(wavTbl,min(_tIdx+1,numTbls-1),_sIdx,_sInterp)
        else:
            _LV = self._linterp(wavTbl,numTbls-1,_sIdx,_sInterp)
            _HV = int(self._maxAmp*(1.0+phReg))
            _tInterp = 1.0-(fReg/(1 << (numTbls+2)))

        return _LV + _tInterp*(_HV-_LV)
