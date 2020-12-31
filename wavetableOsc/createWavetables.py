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

        #self.sawTbls,self.sqrTbls,self.triTbls = self._makeTables(phi,a,[getSaw,getSqr,getTri])
        self.sawTbls = self._makeTables(phi,a,_getSaw)
        collect()
        mem_info()
        self.sqrTbls = self._makeTables(phi,a,_getSqr)
        self.triTbls = self._makeTables(phi,a,_getTri)


    #def _makeTables(self, phi: float, a: float, fList) -> tuple([array,array,array]):
    #def _memReportMakeTables(self, : float, a: float):

    def _makeTables(self, phi: float, a: float, f) -> array:

        allTbls = []
        #allTbls.append(np.array(vector.floor((self._maxAmp/2.)*(tbl[0,:]+np.ones(self._tblLen+1))),dtype=np.uint16).reshape((1,1025)))
        #for f in fList:
            tbl = zeros((self._numTbls,self._tblLen+1))
            for i in range(self._tblLen):
              tbl[0,i] = sin((2*pi*i/self._tblLen)-phi)
            tbl[0,self._tblLen] = tbl[0,0]
            sineTbl = tbl[0,:]
            for i in range(1,self._numTbls,1):
                numPartials = 1 << i    # double the number of partials as frequency decreases by an octave
                kGibbs = (pi/(2*numPartials))   # smooths gibbs phenomena at sawtooth peaks
                for k in range(numPartials):
                    sineIdx = 0
                    n = k+1
                    ampl = ((cos(k*kGibbs))**2)*f(n,a)
                    for j in range(self._tblLen):
                        tbl[i,j] = tbl[i,j] + ampl * sineTbl[sineIdx]
                        sineIdx += n
                        if (sineIdx > self._tblLen):
                            sineIdx -= (self._tblLen)

                tbl[i,self._tblLen] = tbl[i,0]
        #    allTbls.append(array(vector.floor((self._maxAmp/2.)*((tbl+ones((self._numTbls,self._tblLen+1))))),dtype=uint16))
        #return tuple(allTbls)
        return array(vector.floor(self._maxAmp*((tbl+ones((self._numTbls,self._tblLen+1))))),dtype=uint16)


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
      l = wavTbl[tIdx,sIdx]
      r = wavTbl[tIdx,sIdx+1]
      return l + sInterp*(r-l)


    def blinterp(self, wavTbl: array, numTbls: int, phReg: float, fReg: float) -> float:
        sInterp,sIdx = modf((self._tblLen/2.0)*(1.0+phReg))
        sIdx = int(sIdx)

        flevel = -log2((4*fReg))
        tInterp,tIdx = modf(flevel)
        tIdx = int(min(tIdx,numTbls-1))

        LV = HV = 0
        if (flevel < 0.0):  #
            HV = self._linterp(wavTbl,0,sIdx,sInterp)
        elif (flevel < numTbls-1):
            LV = self._linterp(wavTbl,tIdx,sIdx,sInterp)
            HV = self._linterp(wavTbl,min(tIdx+1,numTbls-1),sIdx,sInterp)
        else:
            LV = self._linterp(wavTbl,numTbls-1,sIdx,sInterp)
            HV = int(self._maxAmp*(1.0+phReg))
            tInterp = 1.0-(fReg/(1 << (numTbls+2)))

        return LV + tInterp*(HV-LV)
