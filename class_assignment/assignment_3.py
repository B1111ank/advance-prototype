from machine import Pin
from neopixel import NeoPixel
from time import *

print('NeoPixel LED + button  Example')

# button input on pin 2:
btn = Pin(1, Pin.IN, Pin.PULL_UP)
btn_val_last = 1
program_state = 'disconnect'

startTime = 0
modeTimer = 3000
# create NeoPixel driver on pin 13 for 16 pixel:
np = NeoPixel(Pin(7), 30)

# delay 2 seconds:

program_state = 'START'
print('start fading green color up and down..')

while True:


    print('btn =', btn.value(), btn_val_last)
  # check that the button changed from high to low:
    if btn.value() == 1:
        program_state = 'disconnect'
    elif btn.value() == 0:
        if btn_val_last == 1:
            program_state = 'starting'
            startTime = time() * 1000
        else:
            if (time()*1000) - startTime > 5000:
                program_state = 'finishing'
    btn_val_last = btn.value()
        
    if program_state == 'disconnect':
        for g in range(150):
            for i in range(30):
                np[i] = (g, g, g)
            np.write()
            sleep_ms(1)
            if btn.value() == 0:
                for i in range(30):
                    np[i] = (0, 0, 0)
                np.write()
                break
        for g in range(150):
            for i in range(30):
                np[i] = (150-g, 150-g, 150-g)
            np.write()
            sleep_ms(1)
            if btn.value() == 0:
                for i in range(30):
                    np[i] = (0, 0, 0)
                np.write()
                break
    if program_state == 'starting':
        for i in range(30):
            for g in range(50):
                np[i] = (0,g*4,0)
                sleep_ms(1)
                np.write()
            if btn.value() == 1:
                for i in range(30):
                    np[i] = (0, 0, 0)
                np.write()
                break
    if program_state == 'finishing':
        if np[0][0] < 190:
            for g in range(200):
                for i in range(30):
                    np[i] = (g,np[i][1],0)
                np.write()
            sleep_ms(1)
