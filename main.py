import sys
sys.path.append("PYBD_SF6-wavetable_synth/wavetableOsc/")
from wavetable_osc import *
# ------------------
import math
import pyb
import time
import io
# ------------------
# Define variables
sample_rate = 44100 # Audio sample rate

# Variable deciding which waveform to test
# 0 - PWM
# 1 - Three Osc
# 2 - Saw Sweep
test = 0

# clk_id for System-wide real-time clock
clk_id1 = time.CLOCK_REALTIME

# Sound file variables
num_secs = 20.0 # Length of sound file to generate
gain_mult = 0.5 # Some control over gain of the sound file

# Oscillator variables
base_frequency = 20 # Starting frequency of first table
over_samp = 2 # Oversampling factor (positive integer)
constantRatioLimit = 99999 # set to a large number (>= length of lowest octave table)
# for constant table size; set to 0 for a constant oversampling ratio (each higher ocatave
# table reduced by half); set somewhere between (64, for instance) for constant
# oversampling but with a minimum limit

# main.py -- put your code here!
def main():
    if(test == 0):
        testPWM()
    elif(test == 1):
        testThreeOSC()
    elif(test == 2):
        testSawSweep()

def testThreeOsc():
    # Initialize oscillator with wavetables
    osc_1 = WaveTableOsc()
    osc_2 = WaveTableOsc()
    osc_3 = WaveTableOsc()
    set_sawtooth_osc(osc_1, base_frequency)
    set_sawtooth_osc(osc_2, base_frequency)
    set_sawtooth_osc(osc_3, base_frequency)

    # Get current clock time
    start = time.clock_gettime(clk_id1)

    # Run the Oscillator
    num_samples = sample_rate * num_secs
    sound_buffer = np.zeros(num_samples)

    osc_1.set_frequency((111.0 * 0.5) / sample_rate)
    osc_2.set_frequency((112.0 * 0.5) / sample_rate)
    osc_3.set_frequency(55.0 / sample_rate)

    i = 0
    while(i < num_samples):
        # square wave from sawtooth
        sound_buffer[i] = (osc_1.getOutput() + osc_2.getOutput() + osc_3.getOutput()) * 0.5 * gainMult
        osc_1.updatePhase()
        osc_2.updatePhase()
        osc_3.updatePhase()
        i = i + 1

    finish = time.clock_gettime(clk_id1)
    # elapsed_time = (finish - start)/(double(CLOCKS_PER_SEC))

    # Q&D fade to avoid tick at end
    count = sample_rate * 0.05
    while(count >= 0):
        sound_buffer[num_samples - count] = sound_buffer[num_samples - count] * (count / (sample_rate * 0.05))
        count = count - 1

    # Write float sound
    # Deallocate sound buffer

def testPWM():
    # Initialize oscillator with wavetables
    osc = WaveTableOsc()
    set_sawtooth_osc(osc, base_frequency)

    # pwm
    mod = WaveTableOsc()
    set_sawtooth_osc(osc, base_frequency)

    sine_table_length = 2048
    sin_table = np.zeros(sine_table_length)

    i = 0
    while(i < sine_table_length):
        sine_table[i] = math.sin(float(i) / (sine_table_length * math.pi * 2))
        i = i + 1

    mod.addWaveTable(sine_table_length, sine_Table, 1.0)
    mod.set_frequency(0.3 / sample_rate)

    osc.set_frequency(110.0 / sample_rate)

    # Get current clock time
    start = time.clock_gettime(clk_id1)

    # Run the Oscillator
    num_samples = sample_rate * num_secs
    sound_buffer = np.zeros(num_samples)

    i = 0
    while(i < numSamples):
        osc.set_phase_offset((mod.getOutput() * 0.95 + 1.0) * 0.5)
        sound_buffer[i] = osc.getOutputMinusOffset() * gain_mult
        mod.update_phase()
        osc.update_phase()
        i = i + 1

    finish = time.clock_gettime(clk_id1)
    # elapsed_time = (finish - start)/(double(CLOCKS_PER_SEC))

    # Q&D fade to avoid tick at end
    count = sample_rate * 0.05
    while(count >= 0):
        sound_buffer[num_samples - count] = sound_buffer[num_samples - count] * (count / (sample_rate * 0.05))
        count = count - 1

    # Write float sound
    # Deallocate sound buffer


def testSawSweep():
    # Initialize oscillator with wavetables
    osc = WaveTableOsc()
    set_sawtooth_osc(osc, base_frequency)

    # Get current clock time
    start = time.clock_gettime(clk_id1)

    # Run the Oscillator
    num_samples = sample_rate * num_secs
    sound_buffer = np.zeros(num_samples)

    freq_val = 20.0 / sample_rate
    freq_mult = 1.0 + (math.log(20000.0 / sample_rate) - math.log(freq_val)) / num_samples

    i = 0
    while(i < numSamples):
        osc.set_frequency(freq_val)
        sound_buffer[i] = osc.getOutput() * gain_mult
        osc.update_phase()
        freq_val = freq_val * freq_mult # exponential frequency sweep
        i = i + 1

    finish = time.clock_gettime(clk_id1)
    # elapsed_time = (finish - start)/(double(CLOCKS_PER_SEC))

    # Q&D fade to avoid tick at end
    count = sample_rate * 0.05
    while(count >= 0):
        sound_buffer[num_samples - count] = sound_buffer[num_samples - count] * (count / (sample_rate * 0.05))
        count = count - 1

    # Write float sound
    # Deallocate sound buffer

def weirdLED():
    for i in range(1 << 6):
        par = i % 2
        pyb.LED(par+1).toggle()
        pyb.delay(i+1)
        for j in range(i):
            pyb.LED(par+2).toggle()
            pyb.delay(j+1)
            pyb.LED(par+1).toggle()
            pyb.delay(int(((i+j+1)/(i*j+1))/2))

    for k in range(4):
        pyb.LED(1+k).off()
    return

# define code to write the driver

weirdLED()
