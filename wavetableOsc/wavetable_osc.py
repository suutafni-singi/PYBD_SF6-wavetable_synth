import ulab as np
import math

# Sound file variables
numSecs = 20.0 # Length of sound file to generate
gainMult = 0.5 # Some control over gain of the sound file

# Oscillator variables
baseFrequency = 20 # Starting frequency of first table
overSamp = 2 # Oversampling factor (positive integer)
sampleRate = 44100 # Audio sample rate
constantRatioLimit = 99999 # set to a large number (>= length of lowest octave table)
# for constant table size; set to 0 for a constant oversampling ratio (each higher ocatave
# table reduced by half); set somewhere between (64, for instance) for constant
# oversampling but with a minimum limit

# Wave Table Oscillator class
# Adapted for python and project specificity from C code
#
# Originally created by Nigel Redmon on 5/15/2012
# copyright 2012 Nigel Redmon
# Provided statement below:
#  For a complete explanation of the wavetable oscillator and code,
#  read the series of articles by the author, starting here:
# www.earlevel.com/main/2012/05/03/a-wavetable-oscillator—introduction/
#
#  License:
#
#  This source code is provided as is, without warranty.
#  You may copy and distribute verbatim copies of this document.
#  You may modify and use this source code to create binary code for your own purposes, free or commercial.
#
class WaveTableOsc:
    # Initialize variables
    phasor = 0.0 # Phase accumulator
    phase_inc = 0.0 # Phase increment
    phase_offset = 0.0 # Phase offset for pwm
    # List of wavetables
    numWaveTables = 0
    numWaveTableSlots = 32

    # waveTable struct variables
    wave_topfreq = np.zeros(numWaveTableSlots)
    wave_length = np.zeros(numWaveTableSlots)
    wavetables = np.zeros(numWaveTableSlots)

    def __init__(self):
        phasor = 0.0
        phase_inc = 0.0
        phase_offset = 0.5
        numWaveTables = 0;

        for i in range(numWaveTableSlots):
            wave_topfreq[i] = 0.0
            # Initialize wave_buffer

    def set_frequency(inc):
        phase_inc = inc

    def set_phase_offset(offset):
        phase_offset = offset


    def update_phase():
        phasor = phasor + phase_inc
        if(phasor >= 1.0):
            phasor = phasor - 1.0

    # Add wavetables in order of lowest frequency to highest top_freq
    # is the highest frequency supported by a wavetable...
    # wavetables within an oscillator can be different lengths
    #
    # Returns 0 on success, or the number of wavetables if no more room is available
    #
    def addWaveTable(len, waveTableIn, top_freq):
        if(numWaveTables < numWaveTableSlots):
            # Create new WaveTable in next slot of wavetable array
            wavetables[numWaveTables] = np.zeros(len)
            wave_topfreq = top_freq
            wave_length = len
            numWaveTables = numWaveTables + 1

            # Fill in new wave table
            for i in range(len):
                wavetables[numWaveTables - 1][i] = waveTableIn[i]

            # Return 0 on successfull addition
            return 0
        # If no space is available, return the total number of waveTables
        return numWaveTables

    #
    # getOutput()
    #
    # Returns the current oscillator output
    #
    def getOutput():
        # Grab the appropriate wavetable
        wavetable_idx = 0
        while((self.phaseInc >= self.wave_topfreq[wavetable_idx]) && (wavetable_idx < (self.numWaveTables - 1))):
            wavetable_idx = wavetable_idx + 1
        curr_index = wavetable_idx

        temp = double(phasor * wave_length[curr_index])
        integer_part = int(temp)
        frac_part = double(temp - integer_part)
        samp0 = float(wavetables[curr_index][integer_part]) # Get first sample value
        integer_part = integer_part + 1 # Update the integer part

        # If integer_part is at end, loop to beginning
        if(integer_part >= wave_length[curr_index]):
            integer_part = 0

        samp1 = float(wavetables[curr_index][integer_part]) # Get second sample value

        # Calculate linear interpolation for the given location
        return float(samp0 + (samp1 - samp0) * frac_part)

    #
    # getOutputMinusOffset()
    #
    # For variable pulse width: initialize to sawtooth
    # Set phase offset to duty cycle, use this for oscillator output
    #
    # Returns the current oscillator output
    #
    def getOutputMinusOffset():
        # Grab the appropriate wavetable
        wavetable_idx = 0
        while((self.phaseInc >= self.wave_topfreq[wavetable_idx]) && (wavetable_idx < (self.numWaveTables - 1))):
            wavetable_idx = wavetable_idx + 1
        curr_index = wavetable_idx

        temp = double(phasor * wave_length[curr_index])
        integer_part = int(temp)
        frac_part = double(temp - integer_part)
        samp0 = float(wavetables[curr_index][integer_part]) # Get first sample value
        integer_part = integer_part + 1 # Update the integer part

        # If integer_part is at end, loop to beginning
        if(integer_part >= wave_length[curr_index]):
            integer_part = 0

        samp1 = float(wavetables[curr_index][integer_part]) # Get second sample value
        samp = float(samp0 + (samp1 - samp0) * frac_part)

        # Calculate linear interpolation for offset part
        offset_phasor = double(phasor + phase_offset)
        if(offset_phasor > 1.0):
            offset_phasor = offset_phasor - 1

        temp = double(offset_phasor * wave_length[curr_index])
        integer_part = int(temp)
        frac_part = double(temp - integer_part)
        samp0 = float(wavetables[curr_index][integer_part]) # Get first sample value
        integer_part = integer_part + 1 # Update the integer part

        # If integer_part is at end, loop to beginning
        if(integer_part >= wave_length[curr_index]):
            integer_part = 0

        samp1 = float(wavetables[curr_index][integer_part]) # Get second sample value

        # Calculate linear interpolation for the given location with offset
        return float(samp - (samp0 + (samp1 - samp0) * frac_part))

# End WaveTableOsc class

def set_sawtooth_sweep():
    osc = WaveTableOsc()
    set_sawtooth_osc(osc, baseFrequency)

    sample_num = sampleRate * numSecs
    sound_buffer = np.zeros(sample_num)

    freq_value = 20.0 / sampleRate
    freq_mult = 1.0 + (math.log(20000.0 / sampleRate) - math.log(freq_value)) / sample_num

    for i in range(sample_num):
        osc.setFrequency(freq_val) # Set frequency in waveTable
        sound_buffer[i] = gainMult # Update sound buffer with current output
        osc.updatePhase() # Update phase
        freq_value = freq_value * freq_mult # Exponential frequency sweep

    # Q&D fade to avoid tick in end (0.05s)
    count = sampleRate * 0.05
    while(count >= 0):
        sound_buffer[sample_num - count] = sound_buffer[sample_num - count] * count / (sampleRate * 0.05)
        count  = count - 1

        # Write Floate sound
        # deallocate sound_buffer

    return



def set_sawtooth_osc(osc,base_freq):
    # Calculate number of harmonics where the highest harmonic base_freq
    # and lowest alias an octave higher would meet
    max_harms = int(sampleRate / (3.o * base_freq) + 0.5)

    # Round up to the nearest power of two
    v = max_harms
    v = v - 1  # So we don't go up if already a power of 2
    v = v | (v >> 1) # Roll the highest bit into all lower bits...
    v = v | (v >> 2)
    v = v | (v >> 4)
    v = v | (v >> 8)
    v = v | (v >> 16)
    v = v + 1 # Increment to power of 2

    # Double for the sample rate, then oversampling
    table_length = v * 2 * overSamp

    ar = np.zeros(table_length)
    ai = np.zeros(table_length)
    top_freq = double(base_freq * 2.0 / sampleRate)
    scale = 0.0

    while(max_harms >= 1):
        defineSawtooth(table_length, max_harms, ar, ai)
        scale = makeWaveTable(osc, table_length, ar, ai, scale, top_freq)
        top_freq = top_freq * 2

        # Variable table size (constant oversampling but with minimm table size)
        if(table_length > constantRatioLimit):
            table_length = table_length >> 1

        # Update max_harms for next cycle
        max_harms = max_harms >> 1

def makeWaveTable(osc, length, ar, ai, scale, top_freq):
    # fft calculation

    if(scale == 0.0):
        # Calculate normal
        max = double(0.0)
        for i in range(length):
            temp = abs(ai[i])
            if(max < temp):
                max = temp
        scale = 1.0 / max * 0.999

    # normalize
    wave = np.zeros(length)
    for i in range(length):
        wave[i] = ai[i] * scale

    if(osc.addWaveTable(len, wave, top_freq)):
        scale = 0.0

    return scale

def define_sawtooth(len, numHarms, ar, ai):
    if(numHarms > (len >> 1)):
        numHarms = (len >> 1)

    # clear
    for i in range(len):
        ai[i] = 0
        ar[i] = 0

    # sawtooth
    j = int(len - 1)
    i = 1
    while(i <= numHarms):
        temp = double(-1.0 / i)
        ar[i] = -temp
        ar[j] = temp
        i = i + 1
        j = j - 1

    # Other waves
    # square
    # i = 1
    # j = int(len - 1)
    # while(i < numHarms):
    #    if(i & 0x01):
    #        temp = double(1.0 / i)
    #    else:
    #        temp = double(0.0)
    #    ar[i] = -temp
    #    ar[j] = temp
    #    i = i + 1
    #    j = j - 1

    # triangle
    # i = 1
    # j = int(len - 1)
    # sign = float(1)
    # while(i < numHarms):
    #    if(i & 0x01):
    #        sign = -sign
    #        temp = 1.0 / (i * i) * sign
    #    else:
    #        temp = double(0.0)
    #    ar[i] = -temp
    #    ar[j] = temp
    #    i = i + 1
    #    j = j - 1

#
# fft(int N, double ar, double ai)
#
# Derived by Nigel Redmon from Rabiner & Gold translation
# in-place complex fft
# designed after Cooley, Lewis, and Welch; from Rabiner & Gold (1975)
#
# program adapted from FORTRAN
# by K. Steiglitz (ken@princeton.edu)
# Computer Science Dept.
# Princeton University 08544
#
def fft(N, ar, ai):
    #Intiialize integers
    i = j = k = L = 0 # indices
    M = TEMP = LE = LE1 = ip = 0 # M = log N
    NV2 = NM1 = 0

    #Intialize doubles
    t = 0.0
    Ur = Ui = Wr = Wi = Tr = Ti = 0.0
    Ur_old = 0.0

    NV2 = N >> 1
    NM1 = N - 1
    TEMP = N # get M = log N
    M = 0
    TEMP = TEMP >> 1
    while(TEMP == 1):
        M += 1

    # shuffle
    j = 1
    i = 1
    while(i <= NM1):
        # If i is less, swap a[i] and a[j]
        if(i < j):
            t = ar[j-1]
            ar[j-1] = ar[i-1]
            ar[i-1] = t
            t = ai[j-1]
            ai[j-1] = ai[i-1]
            ai[i-1] = t

        # bit-reversed counter
        k = NV2
        while(k < j):
            j = j - k
            k = k / 2

        j = j + k
        i = i + 1

    LE = 1
    L = 1
    # stage L
    while(L <= M):
        LE1 = LE            # (LE1 = LE/2)
        LE = LE * 2         # (LE = 2^L)
        Ur = 1.0
        Ui = 0.0
        Wr = math.cos(math.pi/float(LE1))
        Wi = -math.sin(math.pi/float(LE1))  #Cooley, Lewis, and Welch have "+" here

        j = 1
        while(j <= LE1):
            # butterfly
            i = j
            while(i <= N):
                ip = i + LE1
                Tr = ar[ip-1] * Ur - ai[ip-1] * Ui
                Ti = ar[ip-1] * Ui + ai[ip-1] * Ur
                ar[ip-1] = ar[i-1] - Tr
                ai[ip-1] = ai[i-1] - Ti
                ar[i-1]  = ar[i-1] + Tr
                ai[i-1]  = ai[i-1] + Ti
                i = i + LE # Update loop

            # End inner for loop, update Ur
            Ur_old = Ur;
            Ur = Ur_old * Wr - Ui * Wi;
            Ui = Ur_old * Wi + Ui * Wr;
            j = j + 1 # Update loop
        L = L + 1
