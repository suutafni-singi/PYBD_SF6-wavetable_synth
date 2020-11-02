import pyb
import uos
from pyb import UART
from array import array

uart = UART(4)
uart.init(baudrate=115200, bits=8, parity=None, stop=1,read_buf_len=8)
a = array('q',[])
uos.dupterm(uart)
x = uart.read(1)
uart.write(x)
