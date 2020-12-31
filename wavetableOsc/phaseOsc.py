from micropython import const
from createWavetables import Wavetable

class BaseOscillator(object):
    def __init__(self, sampleRate: int = 0):
        self._sampleRate = sampleRate

class Oscillator(BaseOscillator):
    def __init__(self, number: int, wavTbl: Wavetable, wav: int, addrBits: int = 12, sampleRate: int = 44100) -> None:
        super().__init__(sampleRate)
        self._num = const(number)
        self._phReg = 0.
        self._fReg = 0.
        self._aReg = 0.
        self._wavTbl = wavTbl.getWavfrm(wav)
        self._numTbls = self._wavTbl.shape()[0]


    def Frequency(self, f: float = 440.0) -> float:
        dFreq = f/self._sampleRate
        return dFreq


    def Amplitude(self, a: float = 0.5) -> float:
        dAmp = a
        return dAmp


    def getNSamps(self, f: float, a: float, wavTbl: Wavetable, N: int) -> np.uint16:
        n = 0
        while n < N:
          self._fReg = self.Frequency(f)
          self._aReg = self.Amplitude(a)
          self._phReg += 2*self._fReg
          #phaseReg = phaseReg & phaseRegMask
          if (self._phReg >= 1.0):
              self._phReg -= 2.0
          elif (self._phReg < -1.0):
              self._phReg = -1.0

          yield int(wavTbl.blinterp(self._wavTbl,self._numTbls,self._phReg,self._fReg)*self._aReg)
          n += 1
        return


    def clearRegs(self) -> None:
        self._fReg = self._aReg = self._phReg = 0.0
