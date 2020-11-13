# main.py -- put your code here!
import pyb

def weirdLED():
    for i in range(1 << 6):
        par = i % 2
        pyb.LED(par+1).toggle()
        pyb.delay(i+1)
        for j in range(i):
            pyb.LED(par+2).toggle()
            pyb.delay(j+1)
            pyb.LED(par+1).toggle()
            pyb.delay(int(((i+j+1)/(i*j+1))/2))

    for k in range(4):
        pyb.LED(1+k).off()
    return

# define code to write the driver

weirdLED()
