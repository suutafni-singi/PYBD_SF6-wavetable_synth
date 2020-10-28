import numpy as np

class wave_buffer:
    #Initialize generator array to store update settings
    generators = np.zeros((12,22))

    #Initialize array of sample points
    wave_forms = np.zeros(12, 4096)

    # The number of points defined by the user-drawn envelope
    point_amount = np.zeros(12)

    # Array of point values to interpolate... (time, amplitude)
    point_array = np.array([],[],[],[],[],[],[],[],[],[],[],[])

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
        else if(osc_type == 1):
            # Handle case where wave is defined by user_input

        #Calculate formulas
        # set_amplitude_formula(generators, gen_index, amp_gen1, amp_gen2, amp_gen3, amp_op1, amp_op2, amp_mult1, amp_mult2, amp_mult3)
        # set_freq_formula(generators, gen_index, freq_gen1, freq_gen2, freq_gen3, freq_op1, freq_op2, freq_mult1, freq_mult2, freq_mult3)

        # handle list of amplitude points (2-4 byte floats - (time_i,val_i))
        # test generator
        print(generators[gen_index])

        update_wave(gen_index)

    def set_waveforms():
        # Set wave_generators from functions
        return 0

    def update_wave(index):
        # Updates wave_generator when generator is updated
        return 0

    def parse_array_bytes(gen_index,num, arg):
        # Appends to point_array from the first point to the final one
        for i in range(num):
             shift_value = (num - i - 1) # If num = 3, cycles through shifts of 2,1,0
             point_array[gen_index].append(((arg >> (64 * shift_value) + 32)) & 0xFFFFFFFF) # Get time value
             point_array[gen_index].append((arg >> (64 * shift_value)) & 0xFFFFFFFF) # Get amplitude value

    # set wave_generators from packet
    def lin_interpolation(index,list_array):
        # Initialize local variables
        buffer_points = 4096
        # get size of list_array and divide by two, the number of pairs
        # point_amount

        # Array of the slopes between each point
        slopes = np.zeros(point_amount[index] - 1)

        # list of indices
        indices = np.zeros(point_amount[index])

        # list of slopes (between each point)
        for x in range(point_amount[index] - 1):
            slopes[x] = (list_array[2(x+1) + 1] - list_array[2(x) + 1])/(list_array[2(x+1)] - list_array[2(x)])

        # Set the array value with locations in interpolated 4096-size buffer
        for x in range(point_amount[index]):
            if(x == point_amount[index] - 1):
                indices[point_amount] = buffer_points - 1
            else:
                indices[point_amount] = (buffer_points / (point_amount[index] - 1)) * x

        # Step through the entire array
        #There will always be at least two points in the array
        x_first = 0
        x_next = 0
        point_A = 0
        point_B = 0
        slope_index = 0

        # check which set of points value is between the indices
        for x in range(point_amount[index]):
            if(x == 0):
                x_next = point_amount[1]
                wave_forms
                for y in range(x_next):
                    if(y == 0):
                        wave_forms[index][0] = list_array[1]
                    else:
                        wave_forms[index][y] = wave_forms[index][y - 1] + y * slope[slope_index]
                slope_index += 1
            else:
                x_first = point_amount[x]
                x_next = point_amount[x+1]

                # Check if final index point
                if(x_next == (buffer_points - 1)):
                    for y in range(x_first,(x_next + 1)):
                        # Calculate points incrementally
                        wave_forms[index][y] = wave_forms[index][y - 1] + y * slope[slope_index]

                else:
                    for y in range(x_first,x_next):
                        # Calculate points incrementally
                        wave_forms[index][y] = wave_forms[index][y - 1] + y * slope[slope_index]
                    slope_index += 1

        # Find the diff between each x, they are the points in the buffer

        # Find the diff between each height and updte the total dif/points underneath to get the delta

        return 0


    def getAmplitude(gen_index,samp_num):
        return wave_forms[gen_index][samp_num]


    def reset_generators():
        generators = np.zeros((12,22))

        for x in range(12):
            generators[x][1] = x

        wave_forms = np.zeros(12,4096)
