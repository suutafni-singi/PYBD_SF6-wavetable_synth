-- PYBD_SF6-wavetable_synth

Currently, a collection of functions that would be pretty inefficient if they were done, files lifted off of other people's repositories (thanks all!) and just generally a public embarassment.
Eventually intended to be a wavetable synthesizer capable of producing 12 simultaneous independent signals which will/should be sent to an offboard 12-channel DAC.
We'll see!

# What we need:

# 1.)
A structure that allows for the storage of all (e.g.) Amplitude functions
for all waveform generators in a single place in a fashion that allows them to
easily include one another when calculating their output
something like class Multibuffer:
DATA: 12 buffers with 4096 slots that can hold information about the Amplitude
at that sample_count for each waveform generator
METHODS:   -Amplitude(gen_number,samp_ct): should return the value stored at
            DATA[gen_number][samp_ct] (would be a lot easier if we could import
            numpy, more below)
           -Interpret(sysMes): should be able to parse out the sysex message
            (detailed below) and use that information to set the Amplitude
            function for the given generator as specified
           -LinearInterp([(time1,val1),...,(timeN,valN)]): should be able to
            connect the values in a list of points on a time(from t = 0 to timeN)
            vs Value(from a = 0. to 1.) graph with straight lines. Pretty googlable
            or I can find one (one is already sort of written for a diff purpose in
            utils.py. only needs to figure it out for each of the 4096 sample values,
            and should ultimately just load those amplitude values into the appropriate
            buffer)
          -Maybe others?

# 2.)
an overall interpreter/router for the sysex message received from max:
this should accept the following byte code which will be in the form of either
a micropython bytearray or a numpy array if we can get the numpy compiler integrated.
(key: the space between each [] represents one byte (8 bits);
      a | symbol between 2 [] delineates different pieces of data;
      a key for the values of each term is given below)
[MIDI channel(0-15)|waveform generator #(0-12)]
--MIDI channel will always be zero (just using it to round out bytes and for
 future improvement
[on/off(0-1)|Oscillator Type (0-5)|Maximum Amplitude Source|Frequency Source]
-- Oscillator Type can be, in ascending order: envelope, sine, triangle, saw,
-- square, noise
-- Max Amplitude Source and Frequency source can both take the values:
-- Constant, MIDI, Formula

-- next 8 bytes are to get parameters in for the amplitude formula;
-- formula = mult1 x DATA[gen1] (op1) mult2 x DATA[gen2] (op2) mult3 * DATA[gen3]
-- where:
--   mult_i is a 16 bit value which can multiply the values of gen_i
--   gen_i can be whatever waveform generator the user selects, it will be a
--     number from 0 to 11 which should serve as code to reference the
--     corresponding buffer.
--   op_i is one of {+,*,/} (- can be implemented using negative values for mult)
--     {+ = 0, * = 1, / = 2}
--   if Max Amplitude Source isn't set to Formula this can be ignored entirely;
--   in that case I'll send a bit of 8 0's from max so you can use that as a
--   sentinel to skip it.
[gen1|gen2] [gen3|op1|op2] [mult1[15:8]] [mult1[7:0]] ... [mult3[15:8]][mult3[7:0]]

-- next eight are the exact same thing but for the frequency function(s), which
-- will be the same type of function as amplitude and will do the same things

[gen1|gen2] [gen3|op1|op2] ... [mult3[15:8]] [mult3[7:0]]

-- finally a list of amplitude points which correspond to the envelope the user
-- draws. these will be arranged as pairs of 16 bit floats (time_i,val_i) as
-- described in the section on linearInterp. A sentinel bit of 0xF7 will designate
-- the end of the list and the end of the whole message

[t1[15:8]] [v1[7:0]] ... [tN[15:8]][vN[7:0]] [11110111]

-- since this isn't real MIDI (midi would send most of these as 7-bit values with
-- a 0 as the first bit in each byte) and the only MIDI messages we're accepting
-- are note_on, note_off, MIDI note number and Velocity (amplitude) I'm gonna
-- completely gut the MIDI interpreter so we have as little to deal with as
-- possible. I'm hopeful we can it set up so the pyboard will be recognized as a
-- MIDI device, otherwise we'll use serial messages.

-- Update: for all the mult values, time values, etc we'll probably use 32 bits
-- because that gels better with single precision float... don't wanna rewrite all
-- that right now

summing it all up:
[MIDI channel(0-15)|waveform generator #(0-12)]
[on/off(0-1)|Oscillator Type (0-5)|Maximum Amplitude Source|Frequency Source]
[gen1|gen2] [gen3|op1|op2] [mult1[15:8]] [mult1[7:0]] ... [mult3[15:8]][mult3[7:0]]
[gen1|gen2] [gen3|op1|op2] ... [mult3[15:8]] [mult3[7:0]]
[t1[15:8]] [v1[7:0]] ... [tN[15:8]][vN[7:0]] [11110111]


# 3.)
better phase Oscillator (working on it)
# 4.) 
better wavetable program
wow man I gotta go. I will work on defining this better tomorrow
(vague promise made on 10/18/20)
