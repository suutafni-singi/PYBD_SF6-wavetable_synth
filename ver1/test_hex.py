# When button is pressed in Max/MSP, run test_main
def test_main(arg):
    print(" ")
    print("Pulse RESET Low")
    print("Hold RESET High")
    print(" ")
    print("Signals to send over I2C SDA line")
    # Get arg patch from MaxMSP
    num_switches = arg & 0xFF
    chip = (arg >> 8) & 0xFF
    # Chip 0 to 7
    while((num_switches - 1) >= 0):
        # Get values from pins and figure out the according hex
        # This is based on which ADG is called, will alter the slave value
        # Chip 0 - 0x00
        # Chip 1 - 0x02
        # Chip 2 - 0x04
        # Chip 3 - 0x06
        # Chip 4 - 0x08
        # Chip 5 - 0x0A
        # Chip 6 - 0x0C
        # Chip 7 - 0x0E

        # Write value, bit 0 is 0
        device_append_val = (chip << 1) & 0xE

        device_addr = '0xE'
        device_addr = device_addr + str(device_append_val)

        # print('START -',end=' ')
        # print(device_addr,end="")
        # print(" - ACK -",end="")
        x = (((arg >> (16 * (num_switches)) + 8)) & 0xFF) # Get x value
        y = ((arg >> (16 * (num_switches))) & 0xFF) # Get y value

        # Write the get_hex(x,y,1) to the ADG
        # print(get_hex(x,y,1), end = ' ')

        # print(" - ACK -", end = ' ')

        # Check if more values to parse, (number of tuples remaining in MaxMSP patch)
        if((num_switches - 1) > 0):
            print("Start - " + str(device_addr) + " - ACK - " + str(get_hex(x,y,1)) + " - ACK - 0x00 - ACK - STOP")
            num_switches = num_switches - 1
        else:
            print("Start - " + str(device_addr) + " - ACK - " + str(get_hex(x,y,1) + " - ACK - 0x01 - ACK - STOP"))
            print("Routing Signal Construction Completed")
            num_switches = num_switches - 1

# Get hex value according to x and y values passed in of matrices I/O and whether to switch on/off
def get_hex(x,y,status):
    output = '0x'
    # If turning matrix on
    if(status):
        if(x == 0 or x == 1):
            output = output + '8'
        elif(x == 2 or x == 3):
            output = output + '9'
        elif(x == 4 or x == 5):
            output = output + 'A'
        elif(x == 6 or x == 7):
            output = output + 'C'
        elif(x == 8 or x == 9):
            output = output + 'D'
        elif(x == 10 or x == 11):
            output = output + 'E'
    else:
        if(x == 0 or x == 1):
            output = output + '0'
        elif(x == 2 or x == 3):
            output = output + '1'
        elif(x == 4 or x == 5):
            output = output + '2'
        elif(x == 6 or x == 7):
            output = output + '4'
        elif(x == 8 or x == 9):
            output = output + '5'
        elif(x == 10 or x == 11):
            output = output + '6'

    # If x is even
    if(x%2 == 0):
        if(y == 0):
            output = output + '0'
        elif(y == 1):
            output = output + '1'
        elif(y == 2):
            output = output + '2'
        elif(y == 3):
            output = output + '3'
        elif(y == 4):
            output = output + '4'
        elif(y == 5):
            output = output + '5'
        elif(y == 6):
            output = output + '6'
        elif(y == 7):
            output = output + '7'
    else:
        if(y == 0):
            output = output + '8'
        elif(y == 1):
            output = output + '9'
        elif(y == 2):
            output = output + 'A'
        elif(y == 3):
            output = output + 'B'
        elif(y == 4):
            output = output + 'C'
        elif(y == 5):
            output = output + 'D'
        elif(y == 6):
            output = output + 'E'
        elif(y == 7):
            output = output + 'F'

    return output

arg = 0x04060A01070301020304
test_main(arg)
print(" ")
