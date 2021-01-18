from micropython import const
from .createWavetables import Wavetable

class BaseOscillator(object):
    def __init__(self, sampleRate: int = 0):
        self.sampleRate = const(sampleRate)


class PhaseOsc(BaseOscillator):
    def __init__(self, number: int, wavTbl: Wavetable, wav: int, numTbls: int = 8, addrBits: int = 12, sampleRate: int = 44100) -> None:
        super().__init__(sampleRate)
        self._num = const(number)
        self.phReg = 0.
        self.fReg = 0.
        self.aReg = 0.
        self.wavTbl = wavTbl
        self.waveform = self.wavTbl.getWaveform(wav)
        self.numTbls = numTbls
        #self._shape = self._wavTbl.shape
        #self._numTbls = self._shape[0]

    def upd8Waveform(self, wav: int) -> None:
        self.wavfrm = self.wavTbl.getWaveform(wav)

    def upd8Freq(self, f: float = 440.0) -> None:
        #self.fReg = self.fReg | pack('f',f/self._sampleRate)
        self.fReg = f/self.sampleRate

    def upd8Amp(self, a: float = 0.5) -> float:
        self.aReg = a

    def upd8Phase(self):
        self.phReg += self.fReg/2.
        if (self.phReg >= 1.0):
            self.phReg -= 2.0
        elif (self.phReg < -1.0):
            self.phReg = -1.0

    def getSamp(self, f: float, a: float):
        self.upd8Freq(f)
        self.upd8Amp(a)
        self.upd8Phase()
        yield int(self.wavTbl.blinterp(self.waveform,self.numTbls,self.phReg,self.fReg)*self.aReg)

    def getNSamps(self, f: float, a: float, N: int) -> list([int]):
        n = 0
        ret = []
        while n < N:
            ret += [s for s in self.getSamp(f,a)]
            n += 1
        return ret

    def clearRegs(self) -> None:
        self.fReg = self.aReg = self.phReg = 0.0
