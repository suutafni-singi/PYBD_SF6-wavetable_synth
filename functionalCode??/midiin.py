# -*- coding: utf-8 -*-
# Code referenced from https://github.com/SpotlightKid/micropython-stm-lib/blob/master/midi/midi/midiin.py

"""MicroPython MIDI input library."""

from .constants import *
class MidiIn:
 def __init__(self,device,callback=None,debug=False,softthru=False):
  if not hasattr(device,'any'):
   raise TypeError("device instance must have a 'any' method.")
  if not hasattr(device,'read'):
   raise TypeError("device instance must have a 'read' method.")
  if softthru and not hasattr(device,'write'):
   raise TypeError("device instance must have a 'write' method if " "soft thru is enabled.")
  self.device=device
  self.callback=callback
  self.debug=debug
  self.softthru=softthru
  self._msgbuf=None
  self._status=None
  self._ignore_active_sense=False
  self._ignore_clock=False
  self._ignore_sysex=False
 def __repr__(self):
  return '<MidiIn: device={} callback={}>'.format(self.device,'yes' if callable(self.callback)else 'no')
 def poll(self):
  msgs=self._read()
  out = 0
  if msgs and self.callback:
   out = 1
   for msg in msgs:
    self.callback(msg)
  return out
 def ignore_types(self,active_sensing=False,clock=False,sysex=False):
  self._ignore_active_sense=active_sensing
  self._ignore_clock=clock
  self._ignore_sysex=sysex
 def _error(self,msg,*args):
  if self.debug:
   import sys
   print(msg%args,file=sys.stderr)
 def _read(self):
  msgs=[]
  while self.device.any():
   data=self.device.read(1)[0]
   if self.softthru:
    self.device.write(bytes([data]))
   if data&0x80:
    if TIMING_CLOCK<=data<=SYSTEM_RESET:
     if data==ACTIVE_SENSING and self._ignore_active_sensing:
      continue
     elif data==TIMING_CLOCK and self._ignore_clock:
      continue
     elif data!=0xFD:
      msgs.append(bytearray([data]))
     else:
      self._error("Read undefined system real-time status " "byte 0x%0X.",data)
    elif data==SYSTEM_EXCLUSIVE:
     self._status=SYSTEM_EXCLUSIVE
     if self._ignore_sysex:
      self._msgbuf=None
     else:
      self._msgbuf=bytearray([data])
    elif data==END_OF_EXCLUSIVE:
     if self._msgbuf and not self._ignore_sysex:
      self._msgbuf.append(data)
      msgs.append(self._msgbuf)
     self._msgbuf=None
     self._status=None
    elif MIDI_TIME_CODE<=data<=TUNING_REQUEST:
     self._status=None
     self._msgbuf=None
     if data==TUNING_REQUEST:
      msgs.append(bytearray([data]))
     elif data<=SONG_SELECT:
      self._msgbuf=bytearray([data])
     else:
      self._error("Read undefined system common status byte " "0x%0X.",data)
    else:
     self._status=data
     self._msgbuf=bytearray([data])
   else:
    if self._status==SYSTEM_EXCLUSIVE and self._ignore_sysex:
     continue
    if self._status and not self._msgbuf:
     self._msgbuf=bytearray([self._status])
    if not self._msgbuf:
     self._error("Read unexpected data byte 0x%0X."%data)
     continue
    self._msgbuf.append(data)
    if(self._status!=SYSTEM_EXCLUSIVE and(len(self._msgbuf)==3 or self._msgbuf[0]&0xF0 in(PROGRAM_CHANGE,CHANNEL_PRESSURE,MTC,SPP))):
     msgs.append(self._msgbuf)
     self._msgbuf=None
  return msgs
