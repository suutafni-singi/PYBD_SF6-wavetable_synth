-- PYBD_SF6-wavetable_synth

Currently, a collection of functions that would be pretty inefficient if they were done, files lifted off of other people's repositories (thanks all!) and just generally a public embarassment.\n
Eventually intended to be a wavetable synthesizer capable of producing 12 simultaneous independent signals which will/should be sent to an offboard 12-channel DAC.\n
We'll see!

# What we need:\n

# 1.)\n
A structure that allows for the storage of all (e.g.) Amplitude functions
for all waveform generators in a single place in a fashion that allows them to
easily include one another when calculating their output\n
something like \n
\n
\n
class Multibuffer:\n
\n
DATA: 12 buffers with 4096 slots that can hold information about the Amplitude\n
at that sample_count for each waveform generator\n
\n
METHODS:   -Amplitude(gen_number,samp_ct): should return the value stored at\n
            DATA[gen_number][samp_ct] (would be a lot easier if we could import\n
            numpy, more below). This should have
           -Interpret(sysMes): should be able to parse out the "sysex" message\n
            (detailed below) and use that information to set the Amplitude\n
            function for the given generator as specified\n
           -LinearInterp([(time1,val1),...,(timeN,valN)]): should be able to\n
            connect the values in a list of points on a time(from t = 0 to timeN)\n
            vs Value(from a = 0. to 1.) graph with straight lines. Pretty googlable\n
            or I can find one (one is already sort of written for a diff purpose in\n
            utils.py. only needs to figure it out for each of the 4096 sample values,\n
            and should ultimately just load those amplitude values into the appropriate\n
            buffer)\n
           -Maybe others?\n
\n
# 2.)
an overall interpreter/router for the sysex message received from max:\n
this should accept the following byte code which will be in the form of either\n
a micropython bytearray or a numpy array if we can get the numpy compiler integrated.\n
(key: the space between each "[...]" represents one byte (8 bits);\n
      a "|"" symbol between "[" and "]" delineates different pieces of data;\n
      a key for the values of each term is given below)\n\n
[MIDI channel(0-15)|waveform generator #(0-12)]\n
-- MIDI channel will always be zero (just using it to round out bytes and for\n
   future improvement\n\n
[on/off(0-1)|Oscillator Type (0-5)|Maximum Amplitude Source|Frequency Source]\n
-- Oscillator Type can be, in ascending order: Envelope, sine, triangle, saw,\n
   square, noise\n
      Envelopes only have amplitude data (because they're DC) so their frequency
      functions can be zero.
-- Max Amplitude Source and Frequency source can both take the values:\n
   Constant, MIDI, Formula\n\n

-- next 14 bytes are to get parameters in for the amplitude formula:\n
   formula = mult1 x DATA[gen1] (op1) mult2 x DATA[gen2] (op2) mult3 * DATA[gen3]\n
-- where:\n
--   mult_i is a 32 bit float which can multiply the values of gen_i\n
--   gen_i can be whatever waveform generator the user selects, it will be a\n
       number from 0 to 11 which should serve as code to reference the\n
       corresponding buffer.\n
--   op_i is one of {+,*,/} (- can be implemented using negative values for mult)\n
         mapping to integers: {+ = 0, * = 1, / = 2}\n
-- if Max Amplitude Source isn't set to Formula this can be ignored entirely;\n
      in that case I'll send a bit of 8 0's from max so you can use that as a\n
      sentinel to skip it.\n
[gen1|gen2] [gen3|op1|op2] [mult1[31:24]] [mult1[23:16]] [mult1[15:8]] [mult1[7:0]]\n
[mult2[31:24]] ... [mult3[15:8]] [mult3[7:0]]\n\n

-- next 14 bytes are the exact same thing but for the frequency function(s), which\n
   will be the same type of function as Amplitude and will do the same things\n

[gen1|gen2] [gen3|op1|op2] ... [mult3[15:8]] [mult3[7:0]]\n\n

-- finally a list of amplitude points which correspond to the envelope the user\n
   draws. these will be arranged as pairs of 16 bit floats (time_i,val_i) as\n
   described in the section on linearInterp. A sentinel bit of 0xF7 will designate\n
   the end of the list and the end of the whole message\n

[t1[31:24]][t1[23:16]][t1[15:8]][t1[7:0]] [v1[31:24]][v1[23:16]][v1[15:8]][v1[7:0]]\n
...\n
[tN[31:24]][tN[23:16]] ... [vN[15:8]][vN[7:0]]\n
[11110111]\n\n

-- since this isn't real MIDI (midi would send most of these as 7-bit values with\n
   a 0 as the first bit in each byte) and the only MIDI messages we're accepting\n
   are note_on, note_off, MIDI note number and Velocity (amplitude) I'm gonna\n
   completely gut the MIDI interpreter so we have as little to deal with as\n
   possible. I'm hopeful we can it set up so the pyboard will be recognized as a\n
   MIDI device, otherwise we'll use serial messages.\n




# 3.)
better phase Oscillator (working on it)
# 4.)
better wavetable program
wow man I gotta go. I will work on defining this better tomorrow
(vague promise made on 10/18/20)
