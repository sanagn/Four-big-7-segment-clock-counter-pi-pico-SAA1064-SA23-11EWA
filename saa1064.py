# micropython library
# for SAS1064 4 7-segment driver
# must remove all print

from machine import I2C

PATTERN = {' ': 0, '!': 134, '"': 34, '#': 0, '$': 0, '%': 0, '&': 0,
'\'': 2, '(': 0, ')': 0, '*': 0, '+': 0, ',': 4, '-': 64, '.': 128,
'/': 82, '0': 63, '1': 6, '2': 91, '3': 79,'4': 102, '5': 109, '6': 125,
'7': 7, '8': 127, '9': 111, ':': 0, ';': 0, '<': 0, '=': 72, '>': 0,
'?': 0, '@': 93, 'A': 119, 'B': 124, 'C': 57, 'D': 94, 'E': 121,'F': 113,
'G': 61, 'H': 118, 'I': 48, 'J': 14, 'K': 112, 'L': 56, 'M': 85, 'N': 84,
'O': 63, 'P': 115, 'Q': 103, 'R': 80, 'S': 45, 'T': 120, 'U': 62, 'V': 54,
'W': 106, 'X': 73, 'Y': 110, 'Z': 27, '[': 57, '\\': 100, ']': 15,
'^': 35, '_': 8, '`': 32, 'a': 119, 'b': 124, 'c': 88, 'd': 94, 'e': 121,
'f': 113, 'g': 61, 'h': 116, 'i': 16, 'j': 12, 'k': 112, 'l': 48, 'm': 85,
'n': 84, 'o': 92, 'p': 115, 'q': 103, 'r': 80, 's': 45, 't': 120, 'u': 28,
'v': 54, 'w': 106, 'x': 73, 'y': 110, 'z': 27, '{': 0, '|': 48, '}': 0,
'~': 65}

class SAA1064:
    def __init__(self, i2c, address=0x38):
        self.i2c = i2c
        self.address = address
        self.init_display()

    def init_display(self):
        """
        Initialize the SAA1064 by setting up control registers.
        Register 0x00 controls operating mode, brightness, etc.
        # b0 = 1: dynamic mode (autoincrement digits)  
        # b1 = 1: digit 1/3 not blanked, b2 = 1: digit 2/4 not blanked
        # b4 = 1: 3 mA segment current 
        # write to control register  
        """
        control_register = 0x00
        control_byte = 0b00010111
        data_to_write = bytearray([0x77])
        self.i2c.writeto_mem(self.address, control_register, data_to_write) 

    def set_brightness(self, level):
        """
        Set brightness level (0-7). The higher the value, the brighter the display.
        """
        if level < 0 or level > 7:
            raise ValueError("Brightness level must be between 0 and 7.")
        control_register = 0x00
        address=0x38
        control_byte = 0b00010111
        brightness = 0x07 | (level << 4) # Modify the brightness level
        self.i2c.writeto_mem(self.address, control_register, bytearray([brightness]))
        
    def display_digit(self, text):
        # Display 4 digits (values between 0-9) on the 7-segment displays.
        # Digits must be an array of 4 values.
        print(text)
        if len(text) != 4:
            raise ValueError("Provide exactly 4 digits.")
        # Convert digits to 7-segment codes
        data = self._encode_digits(text)
        # Send digit codes to the SAA1064
        #data = bytearray([0x01] + digit_codes)  # 0x01 is the register for the digit data
        print ("dsds", data)
        # Send digit codes to the SAA1064
        for i in range(4):
            #data = "%4d" %i # right adjusted
            data2 = bytearray(data) 
            print ("dada", data2)      
            #data = toSegment(text)
            self.i2c.writeto_mem(self.address, i+1, bytearray([data2[i]]))
            #time.sleep(0.01)    

    def display_digit_dp(self, text):
        # Display 4 digits (values between 0-9) on the 7-segment displays.
        # Digits must be an array of 4 values.
        if len(text) != 4:
            raise ValueError("Provide exactly 4 digits.")
        # Convert digits to 7-segment codes
        data = self._encode_digits(text)
        # Send digit codes to the SAA1064
        for i in range(4): 
            #data = bytearray([0x01] + digit_codes)  # 0x01 is the register for the digit data
            #data = "%4d" %i # right adjusted
            print("before ",data)
            #data2 = bytearray(data)
            dp_pf = 128 # dot point suffix
            dp_text = [x + dp_pf for x in data]
            print("dp_text ", dp_text)
            data2 = bytearray(dp_text)
            print("after",data2)
            self.i2c.writeto_mem(self.address, i+1, bytearray([data2[i]]))
            #self.i2c.writeto_mem(self.address, i+1, bytearray([data[i]]))

    def _encode_digits(self, text):
        """
        Convert numerical (0-9) and text digits  to the corresponding 7-segment codes.
        """
        data =[]
        for c in text:
            print("tetr",text)
            data.append(PATTERN[c])
        return data

        #digit_map = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]  # 0-9
        #return [digit_map[d] for d in digits]

# Example usage:
# Create an I2C object, assuming you are using I2C on pins SCL=22, SDA=21
# i2c = I2C(0, scl=Pin(22), sda=Pin(21))
# saa1064 = SAA1064(i2c)

# Set brightness level (0-7)
# saa1064.set_brightness(4)

# Display digits 1, 2, 3, 4
# saa1064.display_digit([1, 2, 3, 4])
