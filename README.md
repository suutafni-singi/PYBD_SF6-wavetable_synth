## PYBD_SF6-wavetable_synth

<p>Currently, a collection of functions that would be pretty inefficient if they were done, files lifted off of other people's repositories (thanks all!) and just generally a public embarassment.  
Eventually intended to be a wavetable synthesizer capable of producing 12 simultaneous independent signals which will/should be sent to an offboard 12-channel DAC.  
We'll see!</p>

#### What we need:
<ol>
<li>
<p>A structure that allows for the storage of all (e.g.) Amplitude functions<br>
for all waveform generators in a single place in a fashion that allows them to<br>
easily include one another when calculating their output<br>
something like</p><br>

        '''python
        class Multibuffer:
        '''  

<p>DATA: 12 buffers with 4096 slots that can hold information about the Amplitude  
at that sample_count for each waveform generator</p>

<p>METHODS:</p><br>
            <ul>
            <li>Amplitude(gen_number,samp_ct): should return the value stored at<br>
            DATA[gen_number][samp_ct] (would be a lot easier if we could import<br>
            numpy, more below).</li><br>
           <li>Interpret(sysMes): should be able to parse out the "sysex" message<br>
            (detailed below) and use that information to set the Amplitude<br>
            function for the given generator as specified</li><br>
           <li>LinearInterp([(time1,val1),...,(timeN,valN)]): should be able to<br>
            connect the values in a list of points on a time(from t = 0 to timeN)<br>
            vs Value(from a = 0. to 1.) graph with straight lines. Pretty googlable<br>
            or I can find one (one is already sort of written for a diff purpose in<br>
            utils.py. only needs to figure it out for each of the 4096 sample values,<br>
            and should ultimately just load those amplitude values into the appropriate<br>
            buffer)</li><br>
           <li>...Maybe others?</li><br>
           </ul>
           </li>

<li>
<p>an overall interpreter/router for the sysex message received from max:<br>
  this should accept the following byte code which will be in the form of either<br>
  a micropython bytearray or a numpy array if we can get the numpy compiler integrated.</p>

<p>(key: the space between each "[...]" represents one byte (8 bits);<br>
    a "|"" symbol between "[" and "]" delineates different pieces of data;<br>
    a key for the values of each term is given below)</p><br>


<p>[MIDI channel(0-15)|waveform generator #(0-12)]</p>

<ul>
<li>MIDI channel will always be zero (just using it to round out bytes and for<br>
    future improvement</li><br>
</ul>
<p>[on/off(0-1)|Oscillator Type (0-5)|Maximum Amplitude Source|Frequency Source]</p>
<ul>
<li>Oscillator Type can be, in ascending order: Envelope, sine, triangle, saw,<br>
   square, noise<br>
    Envelopes only have amplitude data (because they're DC) so their frequency<br>
    functions can be zero.</li><br>
<li>Max Amplitude Source and Frequency source can both take the values:<br>
    Constant, MIDI, Formula</li>
</ul>
<br>
<br>
<ul>
<li>next 14 bytes are to get parameters in for the amplitude formula:<br>
    formula = mult1 x DATA[gen1] (op1) mult2 x DATA[gen2] (op2) mult3 * DATA[gen3]<br>
    where:<br>
    <ul>
  <li>mult_i is a 32 bit float which can multiply the values of gen_i</li>
  <li>gen_i can be whatever waveform generator the user selects, it will be a<br>
       number from 0 to 11 which should serve as code to reference the<br>
       corresponding buffer.</li>
  <li>op_i is one of {+,*,/} (- can be implemented using negative values for mult)<br>
         mapping to integers: {+ = 0, * = 1, / = 2}</li>
    </ul>
<li>if Max Amplitude Source isn't set to Formula this can be ignored entirely;
      in that case I'll send a bit of 8 0's from max so you can use that as a
      sentinel to skip it.</li>
</ul>
<p>[gen1|gen2] [gen3|op1|op2] [mult1[31:24]] [mult1[23:16]] [mult1[15:8]] [mult1[7:0]]<br>
[mult2[31:24]] ... [mult3[15:8]] [mult3[7:0]]</p><br>
<ul>
<li>next 14 bytes are the exact same thing but for the frequency function(s), which<br>
   will be the same type of function as Amplitude and will do the same things</li>
<ul>

<p>[gen1|gen2] [gen3|op1|op2] ... [mult3[15:8]] [mult3[7:0]]</p>
<ul>
<li>finally a list of amplitude points which correspond to the envelope the user<br>
   draws. these will be arranged as pairs of 16 bit floats (time_i,val_i) as<br>
   described in the section on linearInterp. A sentinel bit of 0xF7 will designate<br>
   the end of the list and the end of the whole message</li>
</ul>

<p>[t1[31:24]][t1[23:16]][t1[15:8]][t1[7:0]] [v1[31:24]][v1[23:16]][v1[15:8]][v1[7:0]]<br>
...<br>
[tN[31:24]][tN[23:16]] ... [vN[15:8]][vN[7:0]]<br>
[11110111]</p><br>

<p>since this isn't real MIDI (midi would send most of these as 7-bit values with<br>
   a 0 as the first bit in each byte) and the only MIDI messages we're accepting<br>
   are note_on, note_off, MIDI note number and Velocity (amplitude) I'm gonna<br>
   completely gut the MIDI interpreter so we have as little to deal with as<br>
   possible. I'm hopeful we can it set up so the pyboard will be recognized as a<br>
   MIDI device, otherwise we'll use serial messages.</p><br>
<br>
</li>


<li>better phase Oscillator (working on it)</li>

<li>better wavetable program</li>
</ol>
