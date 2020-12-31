import machine
from machine import I2C # Used to update controls
from machine import Pin
from machine import SPI
from pysm import StateMachine, State, Event
from math import log
import random
import serial

SAMPLE_RATE_IN_HZ = 44100

# serial_line = serial.Serial('USB address')

# Set specfic pins from pyboard
# I2C on bus 0
scl_X = Pin('PULL_SCL', Pin.OUT, value=1) # 59, enable 5.6kOhm X9/SCL pull-up
sda_X = Pin('PULL_SDA', Pin.OUT, value=1) # 55, enable 5.6kOhm X10/SDA pull-up
# I2C on bus 1
scl_Y = Pin('Y9', Pin.OUT, Pin.PULL_UP, value=1) # 12, enable 5.6kOhm Y9/SCL pull-up
sda_Y = Pin('Y10', Pin.OUT, Pin.PULL_UP, value=1) # 10, enable 5.6kOhm Y10/SDA pull-up

i2c_X = I2C('X') # Use default pins
i2c_Y = I2C('Y')

# Frequencies for the 8 possible output signals
frequency = [0,0,0,0,0,0,0,0]
cycles = [0,0,0,0,0,0,0,0]
env_time = [0,0,0,0,0,0,0,0]
amplitude = [0,0,0,0,0,0,0,0]
nn = [0,0,0,0,0,0,0,0]
phase_update = [0,0,0,0,0,0,0,0]
curr_sample = [0,0,0,0,0,0,0,0]
midi_check = [0,0,0,0,0,0,0,0]

# intialize I2C bus
i2c_X.init(I2C.MASTER, baudrate=400000)
i2c_Y.init(I2C.MASTER, baudrate=400000)

# Scan for slaves, returning a list of 7-bit addresses
devices_x = i2c_X.scan()
devices_y = i2c_Y.scan()

# Signal to send through SPI
data = [[],[],[],[],[],[],[],[]]

routing_data = bytearray()

# Initialize all output sound buffers to 0
for x in range(8):
    data[x] = wave_forms.zeros_table

# Global variable to update generators with new information
generator = 0

# Global variable to update matrix with new information
matrix = 0
run_program = 1

# Intialize MIDI information
midi_signal = 0
midi_input = 0
sysex_message = 0

# SPI Variables
# Referenced from https://github.com/SpotlightKid/micropython-stm-lib/blob/master/spimaster/spimaster.py

cs_1 = Pin('X5', Pin.OUT) # Connected to CS line of DAC, to pin 9 on the MAX537
cs_2 = Pin('Y5', Pin.OUT) # Connected to CS line of DAC, to pin 9 on the MAX537
cs_1.high()
cs_2.high()
spi_1 = SPI(1, SPI.MASTER, baudrate=400000, polarity=1, phase=0) # X Pins
spi_2 = SPI(2, SPI.MASTER, baudrate=400000, polarity=1, phase=0) # Y Pins

# GPIO pins
reset = Pin('X1', Pin.OUT) # Use for RESETS... connect Pin 31 on pyboard to pin 31 for all ADGs
ldac = Pin('Y11', Pin.OUT) # Use for DAC loading, connect Pin 54 on pyboard to pin 7 on DAC

# Then go to device datasheet, to find the address the device exposes
# itself as, addressinput pins

# Serial data input pins
# Chip 1
# 8 - DAC1-4 Serial Data Input
# 7 - Active Low, Load DAC

# Chip 2
# 8 - DAC5-8 Serial Data Input
# 7 - Active Low, Load DAC

# DAC Output pins
# Chip 1
# 2 - DAC1 (A)
# 1 - DAC2 (B)
# 16 - DAC3 (C)
# 15 - DAC4 (D)

# Chip 2
# 2 - DAC5 (A)
# 1 - DAC6 (B)
# 16 - DAC7 (C)
# 15 - DAC8 (D)

# I2C addresses (potentially), routing matrices are also indexed from 0x70-0x77
# 00 - 0x04 (1st Slave) - DAC
# 01 - 0x24 (2nd Slave) - Routing Matrix 1
# 10 - 0x44 (3rd Slave) - Routing Matrix 2
# 11 - 0x64 (4th Slave) - Routing Matrix 3

def main():
    spi_1.init(SPI.MASTER, baudrate=400000, polarity=1, phase=0, bits=16, firstbit=SPI.MSB, ti=False)
    spi_2.init(SPI.MASTER, baudrate=400000, polarity=1, phase=0, bits=16, firstbit=SPI.MSB, ti=False)

    # Initialize system to Idle State
    dac_machine.idle()

    while(run_program):
        if(midi_signal):
            handle_midi_msg(midi_input)
            dac_machine.play_audio()
            
        if([POLL FOR MIDI SERIAL]):
            midi_input = serial_line.read(3)
            handle_midi_msg(midi_input)
            dac_machine.play_audio()
            
        if(generator | [POLL FOR GENERATOR SYSEX]):
            generator = 0
            sysex_message = # get from generator sysex
            dac_machine.generator_press()
            dac_machine.play_audio()
            
        if(matrix | [POLL FOR ROUTING SYSEX]):
            matrix = 0
            sysex_message = # get from routing sysex
            dac_machine.routing_press()
            dac_machine.idle()

    # Return state machine to idle
    dac_machine.idle()

    # If stopping run-code, de-initialize I2C and SPI buses
    i2c_X.deinit()
    i2c_Y.deinit()
    spi_1.deinit()
    spi_2.deinit()

class RoutingState(StateMachine):
    def on_enter(self, state, event):
        reset.low()
        reset.high()

        # Get arg patch from MaxMSP
        self.arg = sysex_message
        self.num_switches = self.arg & 0xFF
        self.chip = (self.arg >> 8) & 0xFF
        self.send_first_block()

    def send_first_block(self):
        # Get values from pins and figure out the according hex
        # This is based on which ADG is called, will alter the slave value
        # 4 ADGs means 4 slaves from pyboard, it will probably be on ports 1-4, 0 goes to adau
        # Either: append
        # device_addr = device_addr + hex
        # Write value is 0
        # 0010 - x2 (First Slave, DAC)
        # 0100 - x4 (Second Slave, 1st Matrix)
        # 0110 - x6 (Third Slave, 2nd Matrix)
        # 1000 - x8 (Fourth Slave, 3rd  Matrix)
        routing_data.append(112 + self.chip)
        self.send_second_block()

    def send_second_block(self):
        x = (((self.arg >> (16 * self.num_switches) + 8)) & 0xFF) # Get x value
        y = ((self.arg >> (16 * self.num_switches)) & 0xFF) # Get y value

        # Write the get_hex(x,y,1) to the ADG
        routing_data.append(get_hex(x,y,1))
        self.send_third_block()

    def send_third_block(self):
        self.chip = self.chip + 112 # 0x70 -> 112
        self.num_switches -= 1
        # Check if more values to parse, (number of tuples remaining in MaxMSP patch)
        if(self.num_switches > 0):
            routing_data.append(0)
            i2c_X.start() # Master sends Start condition
            i2c_X.writeto(self.chip, routing_data, stop=True) # Write message to the SDA line, includes STOP at end
            self.send_first_block() # Return to start
        else:
            routing_data.append(1)
            i2c_X.start() # Master sends Start condition
            i2c_X.writeto(self.chip, routing_data, stop=True) # Write device_addr to the SDA line, includes STOP at end
        # Reset input information
        print(list(routing_date)) # Print output bytearray to REPL line
        routing_data = bytearray()
        sysex_message = 0
        
    def on_exit(self, state, event):
        print("Successful re-route")

    def register_handlers(self):
        self.handlers = {
            'enter': self.on_enter,
            'exit': self.on_exit,
        }

class GeneratorState(StateMachine):
    def on_enter(self, state, event):
        self.gen_buffer = bytearray()
        # Get arg patch from MaxMSP
        self.arg = sysex_message
        self.gen_index = self.arg & 0xF
        self.osc_type = (self.arg >> 4) & 0xF
        self.gen_buffer.append(self.gen_index)
        self.gen_buffer.append(self.osc_type)

        self.parse_max_arg()

    def parse_max_arg(self):
        # freq source
        self.freq_source = (self.arg >> 8) & 0x3
        
        self.gen_buffer.append(self.freq_source)

        # amp source
        self.amp_source = (self.arg >> 10) & 0x3
        env_time[self.gen_index] = (self.arg >> 12) & 0xFFFFFFFF
        
        self.gen_buffer.append(self.amp_source)
        self.gen_buffer.append(env_time[self.gen_index])

        if(self.freq_source):
            self.gen_1 = (self.arg >> 44) & 0xF
            self.gen_2 = (self.arg >> 48) & 0xF
            self.gen_3 = (self.arg >> 52) & 0xF
            self.op_1 = (self.arg >> 56) & 0x3
            self.op_2 = (self.arg >> 58) & 0x3
            self.mult_1 = (self.arg >> 60) & 0xFFFFFFFF
            self.mult_2 = (self.arg >> 92) & 0xFFFFFFFF
            self.mult_3 = (self.arg >> 124) & 0xFFFFFFFF
            
            self.gen_buffer.append(self.gen_1)
            self.gen_buffer.append(self.gen_2)
            self.gen_buffer.append(self.gen_3)
            self.gen_buffer.append(self.op_1)
            self.gen_buffer.append(self.op_2)
            self.gen_buffer.append(self.mult_1)
            self.gen_buffer.append(self.mult_2)
            self.gen_buffer.append(self.mult_3)

            # Calculate frequency
            if(not self.op_1 and not self.op_2):
                frequency[self.gen_index] = (self.mult_1 * frequency[self.gen_1]) + (self.mult_2 * frequency[self.gen_2]) + (self.mult_3 * frequency[self.gen_3])
            elif(not self.op_1 and self.op_2):
                frequency[self.gen_index] = (self.mult_1 * frequency[self.gen_1]) + (self.mult_2 * frequency[self.gen_2]) * (self.mult_3 * frequency[self.gen_3])
            elif(self.op_1 and not self.op_2):
                frequency[self.gen_index] = (self.mult_1 * frequency[self.gen_1]) * (self.mult_2 * frequency[self.gen_2]) + (self.mult_3 * frequency[self.gen_3])
            else:
                frequency[self.gen_index] = (self.mult_1 * frequency[self.gen_1]) * (self.mult_2 * frequency[self.gen_2]) * (self.mult_3 * frequency[self.gen_3])

            # Handle frequency bounds
            if(frequency[self.gen_index] > 20000):
                frequency[self.gen_index] = 20000
            elif(frequency[self.gen_index] < 0):
                frequency[self.gen_index] = 0

            phase_update[self.gen_index] = ((frequency[self.gen_index] / SAMPLE_RATE_IN_HZ) * 2.0) * 1024
            self.arg = self.arg >> 156
        elif(not self.freq_source):
            frequency[self.gen_index] = (self.arg >> 44) & 0xFFFFFFFF # Get frequency value

            phase_update[self.gen_index] = ((frequency[self.gen_index] / SAMPLE_RATE_IN_HZ) * 2.0) * 1024
            self.arg = self.arg >> 76

        self.gen_buffer.append(int(frequency[self.gen_index]))
        cycles[self.gen_index] = int(frequency[self.gen_index])

        if(self.amp_source):
            self.gen_1 = self.arg & 0xF
            self.gen_2 = (self.arg >> 4) & 0xF
            self.gen_3 = (self.arg >> 8) & 0xF
            self.op_1 = (self.arg >> 12) & 0x3
            self.op_2 = (self.arg >> 14) & 0x3
            self.mult_1 = (self.arg >> 48) & 0xFFFFFFFF
            self.mult_2 = (self.arg >> 80) & 0xFFFFFFFF
            self.mult_3 = (self.arg >> 112) & 0xFFFFFFFF
            
            self.gen_buffer.append(self.gen_1)
            self.gen_buffer.append(self.gen_2)
            self.gen_buffer.append(self.gen_3)
            self.gen_buffer.append(self.op_1)
            self.gen_buffer.append(self.op_2)
            self.gen_buffer.append(self.mult_1)
            self.gen_buffer.append(self.mult_2)
            self.gen_buffer.append(self.mult_3)
            
            # Calculate amplitude[self.gen_index] and set in thingy
            if(not self.op_1 and not self.op_2):
                amplitude[self.gen_index] = ((self.mult_1 * amplitude[self.gen_1]) + (self.mult_2 * amplitude[self.gen_2]) + (self.mult_3 * amplitude[self.gen_3]))/127
            elif(not self.op_1 and self.op_2):
                amplitude[self.gen_index] = ((self.mult_1 * amplitude[self.gen_1]) + (self.mult_2 * amplitude[self.gen_2]) * (self.mult_3 * amplitude[self.gen_3]))/127
            elif(self.op_1 and not self.op_2):
                amplitude[self.gen_index] = ((self.mult_1 * amplitude[self.gen_1]) * (self.mult_2 * amplitude[self.gen_2]) + (self.mult_3 * amplitude[self.gen_3]))/127
            else:
                amplitude[self.gen_index] = ((self.mult_1 * amplitude[self.gen_1]) * (self.mult_2 * amplitude[self.gen_2]) * (self.mult_3 * amplitude[self.gen_3]))/127
            # Handle amplitude bounds
            if(amplitude[self.gen_index] > 1):
                amplitude[self.gen_index] = 1
            elif(amplitude[self.gen_index] < 0):
                amplitude[self.gen_index] = 0
        elif(not self.amp_source):
            amp = self.arg & 0xFFFFFFFF # Get amplitude value
            # Handle ampltiude bounds
            if(amp > 127):
                amplitude[self.gen_index] = 1
            elif(amp < 0):
                amplitude[self.gen_index] = 0
            else:
                amplitude[self.gen_index] = amp/127
                
        self.gen_buffer.append(int(amplitude[self.gen_index]))
        print(list(self.gen_buffer))

        # Reset input information
        update_wave(self.gen_index, self.osc_type, frequency[self.gen_index])
        sysex_message = 0

    def on_exit(self, state, event):
        print("Successfully set generators")

    def register_handlers(self):
        self.handlers = {
            'enter': self.on_enter,
            'exit': self.on_exit,
        }

class PlayState(StateMachine):
    def on_enter(self, state, event):
        # Prepare sound buffer
        # Should probably get active wavetables as writing all active outputs
        self.no_interrupt = 1

    def loop_audio(self):
        # Trigger state that starts to pass information to the DAC from the wavetables
        # Run it on a loop
        while(self.no_interrupt):
            # Poll MIDI serial
                midi_input = # get from serial, perhaps serial_line.read(3)
                self.no_interrupt = 0
                midi_signal = 1
                break
            # Poll for Generator Interrupt, sysex
                self.no_interrupt = 0
                sysex_message = #[get from sysex]
                generator = 1
                break
            # Poll for Routing Interrupt, sysex
                self.no_interrupt = 0
                sysex_message = #[get from sysex]
                matrix = 1
                break

            # SPI signal to update all dacs
            # SPI 1
            cs_1.low()
            # 0x1[data] - DAC 1
            spi_1.write(int(data[0][int(curr_sample[0])] * amplitude[0]) + 4096) # Adds 0x1000 to data
            # 0x5[data] - DAC 2
            spi_1.write(int(data[1][int(curr_sample[1])] * amplitude[1]) + 20480) # Adds 0x5000 to data
            # 0x9[data] - DAC 3
            spi_1.write(int(data[2][int(curr_sample[2])] * amplitude[2]) + 36864) # Adds 0x9000 to data
            # 0xD[data] - DAC 4
            spi_1.write(int(data[3][int(curr_sample[3])] * amplitude[3]) + 53248) # Adds 0xD000 to data
            cs_1.high()

            # SPI 2
            cs_2.low()
            # 0x1[data] - DAC 4
            spi_2.write(int(data[4][int(curr_sample[4])] * amplitude[4]) + 4096) # Adds 0x1000 to data
            # 0x5[data] - DAC 5
            spi_2.write(int(data[5][int(curr_sample[5])] * amplitude[5]) + 20480) # Adds 0x5000 to data
            # 0x9[data] - DAC 6
            spi_2.write(int(data[6][int(curr_sample[6])] * amplitude[6]) + 36864) # Adds 0x9000 to data
            # 0xD[data] - DAC 7
            spi_2.write(int(data[7][int(curr_sample[7])] * amplitude[7]) + 53248) # Adds 0xD000 to data
            cs_2.high()

            # send signal to active low LDAC
            # should be connection on from master (43) to both slaves's (7)
            ldac.low()
            ldac.high()

            if((curr_sample[0] + phase_update[0]) > 2047):
                curr_sample[0] = (curr_sample[0] + phase_update[0]) % 2048
                cycles[0] -= 1
                if(cycles[0] <= 0):
                    cycles[0] = frequency[0]
                    env_time[0] -= 1
                    if(env_time[0] <= 0):
                        data[0] = wave_forms.zeros_table
                        midi_check[0] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[1] + phase_update[1]) > 2047):
                curr_sample[1] = (curr_sample[1] + phase_update[1]) % 2048
                cycles[1] -= 1
                if(cycles[1] <= 0):
                    cycles[1] = frequency[1]
                    env_time[1] -= 1
                    if(env_time[1] <= 0):
                        data[1] = wave_forms.zeros_table
                        midi_check[1] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[2] + phase_update[2]) > 2047):
                curr_sample[2] = (curr_sample[2] + phase_update[2]) % 2048
                cycles[2] -= 1
                if(cycles[2] <= 0):
                    cycles[2] = frequency[2]
                    env_time[2] -= 1
                    if(env_time[2] <= 0):
                        data[2] = wave_forms.zeros_table
                        midi_check[2] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[3] + phase_update[3]) > 2047):
                curr_sample[3] = (curr_sample[3] + phase_update[0]) % 2048
                cycles[3] -= 1
                if(cycles[3] <= 0):
                    cycles[3] = frequency[3]
                    env_time[3] -= 1
                    if(env_time[3] <= 0):
                        data[3] = wave_forms.zeros_table
                        midi_check[3] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[4] + phase_update[4]) > 2047):
                curr_sample[4] = (curr_sample[4] + phase_update[0]) % 2048
                cycles[4] -= 1
                if(cycles[4] <= 0):
                    cycles[4] = frequency[4]
                    env_time[4] -= 1
                    if(env_time[4] <= 0):
                        data[4] = wave_forms.zeros_table
                        midi_check[4] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[5] + phase_update[5]) > 2047):
                curr_sample[5] = (curr_sample[5] + phase_update[5]) % 2048
                cycles[5] -= 1
                if(cycles[5] <= 0):
                    cycles[5] = frequency[5]
                    env_time[5] -= 1
                    if(env_time[5] <= 0):
                        data[5] = wave_forms.zeros_table
                        midi_check[5] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[6] + phase_update[6]) > 2047):
                curr_sample[6] = (curr_sample[6] + phase_update[6]) % 2048
                cycles[6] -= 1
                if(cycles[6] <= 0):
                    cycles[6] = frequency[6]
                    env_time[6] -= 1
                    if(env_time[6] <= 0):
                        data[6] = wave_forms.zeros_table
                        midi_check[6] = 0 # Essentially, turn off midi port and prepare port for next signal

            if((curr_sample[7] + phase_update[7]) > 2047):
                curr_sample[7] = (curr_sample[7] + phase_update[7]) % 2048
                cycles[7] -= 1
                if(cycles[7] <= 0):
                    cycles[7] = frequency[7]
                    env_time[7] -= 1
                    if(env_time[7] <= 0):
                        data[7] = wave_forms.zeros_table
                        midi_check[7] = 0 # Essentially, turn off midi port and prepare port for next signal

            if(not midi_signal and not matrix and not generator):
                self.loop_audio()


    def on_exit(self, state, event):
        print("Stop Audio")

    def register_handlers(self):
        self.handlers = {
            'enter': self.on_enter,
            'exit': self.on_exit,
        }

class DAC(object):

    def __init__(self):
        self.sm = self._get_state_machine()

    def _get_state_machine(self):
        dac = StateMachine('DAC')
        routing_update = RoutingState('Routing')
        generator_update = GeneratorState('Generator')
        play_state = PlayState('Play')
        idle = State('Idle')

        dac.add_state(idle, initial=True)
        dac.add_state(play_state)
        dac.add_state(routing_update)
        dac.add_state(generator_update)

        dac.add_transition(idle, generator_update, events=['gen_update'])
        dac.add_transition(idle, routing_update, events=['route_update'])
        dac.add_transition(idle, play_state, events=['play_trigger'])

        dac.add_transition(play_state, generator_update, events=['gen_update'])
        dac.add_transition(play_state, routing_update, events=['route_update'])
        dac.add_transition(play_state, idle, events=['stop'])

        dac.add_transition(generator_update, idle, events=['idle'])
        dac.add_transition(routing_update, idle, events=['idle'])

        dac.initialize()
        return dac

    @property
    def state(self):
        return self.sm.leaf_state.name

    # Trigger if generator button is pressed in MaxMSP
    def generator_press(self):
        self.sm.dispatch(Event('gen_update'))

    # Trigger if routing button is pressed in Max MSP
    def routing_press(self):
        self.sm.dispatch(Event('route_update'))

    def idle(self):
        self.sm.dispatch(Event('idle'))

    # Trigger if play button is pressed
    def play_audio(self):
        self.sm.dispatch(Event('play_trigger'))

# Get hex value according to x and y values passed in of matrices I/O and whether to switch on/off
def get_hex(x,y,status):
    output = 0
    # If turning matrix on
    if(status):
        if(x == 0 or x == 1):
            output = 128
        elif(x == 2 or x == 3):
            output = 144
        elif(x == 4 or x == 5):
            output = 160
        elif(x == 6 or x == 7):
            output = 192
        elif(x == 8 or x == 9):
            output = 208
        elif(x == 10 or x == 11):
            output = 224
    else:
        if(x == 0 or x == 1):
            output = 0
        elif(x == 2 or x == 3):
            output = 16
        elif(x == 4 or x == 5):
            output = 32
        elif(x == 6 or x == 7):
            output = 64
        elif(x == 8 or x == 9):
            output = 80
        elif(x == 10 or x == 11):
            output = 96

    # If x is even
    if(x%2 == 0):
        if(y == 0):
            output = output + 0
        elif(y == 1):
            output = output + 1
        elif(y == 2):
            output = output + 2
        elif(y == 3):
            output = output + 3
        elif(y == 4):
            output = output + 4
        elif(y == 5):
            output = output + 5
        elif(y == 6):
            output = output + 6
        elif(y == 7):
            output = output + 7
    else:
        if(y == 0):
            output = output + 8
        elif(y == 1):
            output = output + 9
        elif(y == 2):
            output = output + 10
        elif(y == 3):
            output = output + 11
        elif(y == 4):
            output = output + 12
        elif(y == 5):
            output = output + 13
        elif(y == 6):
            output = output + 14
        elif(y == 7):
            output = output + 15

    return output

def handle_midi_msg(msg):
    midi_signal = 0
    midi_input = 0
    if(20 < ((msg >> 8) & 0xFF) < 109):
        for x in range (8):
            if(midi_check[7 - x] == 0):
                midi_check[7 - x] = 1
                amplitude[7 - x] = (msg & 0xFF)/127
                nn[7 - x] = (msg >> 8) & 0xFF
                env_time[7 - x] = 5 # Default play time of 5 seconds
                frequency[7 - x] = wave_forms.midi_frequency[nn[7-x] - 21]
                cycles[7 - x] = int(frequency[7 - x])
                phase_update[7 - x] = (2.0 * (frequency[7 - x] / SAMPLE_RATE_IN_HZ)) * 1024
                # call function with current midi index, random wave_form - excluding noise - and correlated frequency
                update_wave((7-x), int(random.random() * 4), frequency[7 - x])

def update_wave(index, wave_type, freq_input):
    if(wave_type == 0):
        data[index] = wave_forms.sine_table # Set as default array
    elif(wave_type == 1):
        data[index] = wave_forms.saw_table[(int(0 - log((4 * (freq_input / SAMPLE_RATE_IN_HZ)), 2)) - 1)]
    elif(wave_type == 2):
        data[index] = wave_forms.square_table
    elif(wave_type == 3):
        data[index] = wave_forms.triangle_table
    elif(wave_type == 4):
        data[index] = []
        for x in range(2048):
            data[index].append(int(random.random() * 4095))

# Run program
main()
