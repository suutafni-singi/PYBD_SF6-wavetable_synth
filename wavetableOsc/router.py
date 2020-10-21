import numpy as np
generators = np.zeros((12,22))


def main():
    reset_generators()

    arg = 0xF07D0AC5FFFF0000000A0000000000000007FFFF0000000A0000000000000007
    parse_message(arg)

def reset_generators():
    generators = np.zeros((12,22))

    for x in range(12):
        generators[x][1] = x

# Array struct
# 0 - MIDI channel
# 1 - Waveform generator
# 2 - on/off
# 3 - oscillator type
#    0: envelope
#    1: sine
#    2: sawtooth
#    3: triangle
#    4: square
#    5: noise
# 4 - Max amplitude source
#    0: constant
#    1: MIDI
#    2: formula
# 5 - Max frequency source
#    0: constant
#    1: MIDI
#    2: formula

# Amplitude
# 6 - amplitude gen1
# 7 - gen2
# 8 - gen3
# 9 - op1
# 10 - op2
# 11 - mult1
# 12 - mult2
# 13 - mult3

# Frequency
# 14 - gen1
# 15 - gen2
# 16 - gen3
# 17 - op1
# 18 - op2
# 19 - mult1
# 20 - mult2
# 21 - mult3


def parse_message(arg):
    gen_index = 0

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

    # max amp
    amp = ((arg >> 224) & 0xC) >> 2 #Shift 28 bytes, bit_mask hi 2 bits
    generators[gen_index][4] = amp

    # freq source
    freq = ((arg >> 224) & 0x3) #Shift 28 bytes, bit_mask low 2 bits
    generators[gen_index][5] = freq

    # Amplitude - Next 14 bytes
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

    # Frequency - Next 14 bytes
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

    # handle list of amplitude points (2-4 byte floats - (time_i,val_i))
    print(generators[gen_index])

main()
