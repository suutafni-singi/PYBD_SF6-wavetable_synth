// uses 32-bit ints as registers to implement a phase oscillator
// our actual function will be in python and will have to change which
// wavetable it uses depending on the value of the frequency, which is what
// the "interp" function does in the other wavetable... im on windows right now
// but i found the file that includes the "interp" function used in the other
// phase oscillator, and its purpose is to interpolate between values
// in different wavetables to get one that won't alias no matter the frequency.
// gonna work on the wavetables and phase oscillator this weekend
#include "wavetable.c" // just pretend it's a thing
const int sampleRate = 44800; // sample rate of our DAC
const int bitsInPhaseRegister = 24; //number of bits used for phase register
const int phaseRegMask = ((1 << bitsInPhaseRegister)-1); // = 0x00FFFFFF
const int bitsInMemoryAddress = 12; // top 12 bits used to index into wavetable
const int memoryTableLength = (1 << bitsInMemoryAddress); // 4096 samples in wavetable
const int bitsInMemoryData = 16; // using 16
const int maxAmplitude = (1 << (bitsInMemoryData-1)) - 1;
// ^^ one less than the maximum value that can be represented with 24 bit data, assuming
// that the data is signed (hence bitsInMemoryData-1)
const int bitsInAmplValue = 24; // 24 bit unsigned maxAmplitude
const int numSamps = 500; // number of samples to calculate;
 // this is actually gonna be determined by the total time of each generator multiplied by
 // the sample rate (seconds * bits/second = number of bits)


int Frequency(int sampCount, double freq)
{
  // this will actually take the markers defined in wave_buffer, whatever arguments we need
  // sorry for sucking currently, way too much
  double dFreq = freq/sampleRate;
  return int( (dFreq) * (1 << bitsInPhaseRegister) );
}

int Amplitude(int sampCount, double amp) // again, whatever arguments we need, sry sry
{
  double dAmp = amp/sampleRate;
  return int( (dAmp) * (1 << bitsInAmplValue) );
}
 int make_samples(int argc, _TCHAR* argv[])
 {
   int phaseReg = 0; // will index into our wavetable to get appropriate sample
   int freqReg = 0;
   // added to phaseReg each sample count, determines how quickly we move through samples
   int ampReg = 0; // the amplitude
   for (int sampCount = 0; sampCount < numSamps; ++sampCount)
   {
     // get new values for frequency and ampitude; both will actually be
     // time varying functions in our version
     freqReg = Frequency(sampleCount);
     ampReg = Amplitude(sampleCount);

     //update phase
     phaseReg += freqReg;

     // wrap phase to 24 bits
     phaseReg = (phaseReg & phaseRegMask);

     //get memory address from top 12 bits of phase register
     int memAddr = phaseReg >> (bitsInPhaseRegister - bitsInMemoryAddress);

     // get sample from wavetable memory
     // our version will actually have multiple wavetables for a given
     // range of frequencies and will interpolate between wavetables
     int sample = waveTable[memAddr];

     // multiply sample by amplitude
     // needs to shift result after the multiple, because we are representing
     // an amplitude between 0 and 1
     sample = (sample*ampReg) >> bitsInAmplValue;

     // output result to FIFO queue which goes to our DAC
     // not shown lol
   }
 }
