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

# Wave generator class
#
# Contains arrays containing information to form waveforms

def Generator:
    #Initialize generator array to store update settings
    generators = np.zeros((12,22))

    # The number of points defined by the user-drawn envelope
    point_amount = np.zeros(12)

    # Array of point values to interpolate... (time, amplitude)
    point_array = np.array([],[],[],[],[],[],[],[],[],[],[],[])

    # init method or constructor
    def __init__(self):
        reset_generators()

    # Function header
    def update_generator(arg):
        gen_index = 0 # Index of generator to update
        amp_formula_check = 0 # Checks if amplitude formula is set in struct before reading amplitude values
        freq_formula_check = 0 # Checks if frequency formula is set in struct before reading amplitude values

        # arg is an array of 30-byte array, 240 bits

        # 0xF0 is the MIDI indicating the start of a sysex message
        # 0x7D will be set to "non-commercial/educational use"

        # First byte handles MIDI channel and waveform generator
        # MIDI channel will always be set to zero (hi-bytes)

        # low 4-bits set waveform generator
        gen_index = (arg >> 232) & 0xF #Shift 29 bytes, then bit_mask to get low_4 bytes
        generators[gen_index][1] = gen_index

        # oscillator on/off
        osc = ((arg >> 228) & 0x8) >> 3 #Shift 28.5 bytes, bit_mask top bit, then shift into lowest bit
        generators[gen_index][2] = osc

        # oscillator type
        osc_type = ((arg >> 228) & 0x7) #Shift 28.5 bytes, bit_mask low 3 bits
        generators[gen_index][3] = osc_type

        # If 0, or 1... can bypass formula reading
        # If 2, trigger formula
        if(osc_type == 2):
            # max amp
            amp = ((arg >> 224) & 0xC) >> 2 #Shift 28 bytes, bit_mask hi 2 bits
            if(amp == 2):
                amp_formula_check = 1
            generators[gen_index][4] = amp

            # freq source
            freq = ((arg >> 224) & 0x3) #Shift 28 bytes, bit_mask low 2 bits

            if(freq == 2):
                freq_formula_check = 1
            generators[gen_index][5] = freq

            # Amplitude - Next 14 bytes
            if(amp_formula_check):
                # gen1
                amp_gen1 = ((arg >> 216) & 0xF0) >> 4 #Shift 27 bytes, bit_mask hi 4 bits
                generators[gen_index][6] = amp_gen1

                # gen2
                amp_gen2 = ((arg >> 216) & 0x0F) #Shift 27 bytes, bit_mask lo 4 bits
                generators[gen_index][7] = amp_gen2

                # gen3
                amp_gen3 = ((arg >> 208) & 0xF0) >> 4 #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][8] = amp_gen3

                # op1
                amp_op1 = ((arg >> 208) & 0xC) >> 2 #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][9] = amp_op1

                # op2
                amp_op2 = ((arg >> 208) & 0x3) #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][10] = amp_op2

                # mult1
                amp_mult1 = ((arg >> 176) & 0xFFFFFFFF) #Shift 22 bytes, bit_mask 4 bytes
                generators[gen_index][11] = amp_mult1

                # mult2
                amp_mult2 = ((arg >> 144) & 0xFFFFFFFF) #Shift 18 bytes, bit_mask 4 bytes
                generators[gen_index][12] = amp_mult2

                # mult3
                amp_mult3 = ((arg >> 112) & 0xFFFFFFFF) #Shift 14 bytes, bit_mask 4 bytes
                generators[gen_index][13] = amp_mult3

                # Set waveform amplitudes based off formula
                set_waveforms[gen_index]


            # Frequency - Next 14 bytes
            if(freq_formula_check):
                # gen1
                freq_gen1 = ((arg >> 216) & 0xF0) >> 4 #Shift 27 bytes, bit_mask hi 4 bits
                generators[gen_index][14] = freq_gen1

                # gen2
                freq_gen2 = ((arg >> 216) & 0x0F) #Shift 27 bytes, bit_mask lo 4 bits
                generators[gen_index][15] = freq_gen2

                # gen3
                freq_gen3 = ((arg >> 208) & 0xF0) >> 4 #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][16] = freq_gen3

                # op1
                freq_op1 = ((arg >> 208) & 0xC) >> 2 #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][17] = freq_op1

                # op2
                freq_op2 = ((arg >> 208) & 0x3) #Shift 26 bytes, bit_mask hi 4 bits
                generators[gen_index][18] = freq_op2

                # mult1
                freq_mult1 = ((arg >> 176) & 0xFFFFFFFF) #Shift 22 bytes, bit_mask 4 bytes
                generators[gen_index][19] = freq_mult1

                # mult2
                freq_mult2 = ((arg >> 144) & 0xFFFFFFFF) #Shift 18 bytes, bit_mask 4 bytes
                generators[gen_index][20] = freq_mult2

                # mult3
                freq_mult3 = ((arg >> 112) & 0xFFFFFFFF) #Shift 14 bytes, bit_mask 4 bytes
                generators[gen_index][21] = freq_mult3

        # Calculate formulas
        # set_amplitude_formula(generators, gen_index, amp_gen1, amp_gen2, amp_gen3, amp_op1, amp_op2, amp_mult1, amp_mult2, amp_mult3)
        # set_freq_formula(generators, gen_index, freq_gen1, freq_gen2, freq_gen3, freq_op1, freq_op2, freq_mult1, freq_mult2, freq_mult3)

        # handle list of amplitude points (2-4 byte floats - (time_i,val_i)), if necessary
        if(amp_source):
            amp_source = 0
            # done
            # should set the 44100sample waveforms of amplitudes, using linear interpolation

        # test generator
        # print(generators[gen_index])

    def reset_generators():
        # reset generator formulas
        generators = np.zeros((12,22))

        # Set index calue for each generator
        for x in range(12):
            generators[x][1] = np.float(x)

    def parse_array_bytes(gen_index,num,arg):
        # Appends to point_array from the first point to the final one
        for i in range(num):
             shift_value = (num - i - 1) # If num = 3, cycles through shifts of 2,1,0
             point_array[gen_index].append(((arg >> (64 * shift_value) + 32)) & 0xFFFFFFFF) # Get time value
             point_array[gen_index].append((arg >> (64 * shift_value)) & 0xFFFFFFFF) # Get amplitude value


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
    def addWaveTable(L, waveTableIn, top_freq):
        if(numWaveTables < numWaveTableSlots):
            # Create new WaveTable in next slot of wavetable array
            wavetables[numWaveTables] = np.zeros(L)
            wave_topfreq = top_freq
            wave_length = len
            numWaveTables = numWaveTables + 1

            # Fill in new wave table
            for i in range(L):
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

        temp = float(phasor * wave_length[curr_index])
        integer_part = uint16(temp)
        frac_part = float(temp - integer_part)
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

        # TODO
        # Write Floate sound
        # deallocate sound_buffer

    return

#
#set_sawtooth_osc(osc,base_freq)
#
# Makes set of wavetables for sawtooth Oscillator
#
def set_sawtooth_osc(osc,base_freq):
    # Calculate number of harmonics where the highest harmonic base_freq
    # and lowest alias an octave higher would meet
    max_harms = int(sampleRate / (3.0 * base_freq) + 0.5)

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

#
# makeWaveTable(osc, length, ar, ai, scale, top_freq)
#
# if scale is 0, auto-scales
# returns scaling factor (0.0 if failure) and wavetable in ai Array
#
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

#
# define_sawtooth(len, numHarms, ar, ai)
#
# Prepares sawtooth harmonics for ifft
#
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
