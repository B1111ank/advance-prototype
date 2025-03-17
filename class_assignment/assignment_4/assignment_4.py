import os, sys, io
import M5
from M5 import *
from hardware import RGB
from hardware import I2C
from hardware import Pin
from unit import IMUProUnit
from neopixel import NeoPixel
from time import *
from unit import ReflectiveIRUnit

M5.begin()

# setup IMU pro
i2c = I2C(0, scl=Pin(39), sda=Pin(38), freq=100000)
imu = IMUProUnit(i2c)
np = NeoPixel(Pin(7), 30)
imu_val = imu.get_accelerometer()

# setup for calculating lighting
numlight = 3
numlight_last = numlight

programstate = ''

# setup for calculating breathing
countg = 10.0
state = 'in'
counttime = 0
start = 0
countpeek = 0
peek = 0
breathecheck = False
startbreathe = 0
breathetime = 0

# setup for timing
speed = 4
pace = 0
runningtime = 0

reflect = ReflectiveIRUnit((6,5))
r_val = 0

# setup for pushup
pushup = 0
pushuptime = 0


btn_last = 1
btn = Pin(41, Pin.IN, Pin.PULL_UP)

imu_y_last = imu_val[1]
imu_x_last = imu_val[0]

def getNumMap(a):
    return 3 + a/5*27

while True:
    M5.update()
    imu_val = imu.get_accelerometer()
    
    # checking state
    if btn.value() == 0 and btn_last != btn.value():
        if programstate == 'pushup'or programstate == '':
            programstate = 'running'
            runningtime = time()
            print('programstate||'+ '1')
        else:
            programstate = 'pushup'
            pushuptime = time()
            print('programstate||'+ '2')
    
    btn_last = btn.value()

    
        
    # running state
    if programstate == 'running':
        dx = abs(imu_val[0])
        # check if the IMU acceloration is high
        if (dx > 1.5):
            numlight = getNumMap(dx)
            if numlight > numlight_last:
                numlight_last = numlight
            elif numlight < numlight_last:
                if numlight_last > peek:
                    peek = numlight_last
                    countpeek += 1
                    pace += 1
                numlight_last = numlight
        # reset peek
        if dx < 1:
            peek = 0
        # calculating breathing time
        if breathecheck == False:
            startbreathe = time_ns()
            breathecheck = True
        if breathecheck == True:
            if countpeek == 2:
                breathetime = int((time_ns() - startbreathe) / 1000000)
                breathecheck = False
                countpeek = 0
                if breathetime > 500:
    #                 print(breathetime)
                    speed = 4 * 2000 / breathetime
        # limit the breathe speed
        if speed < 4:
            speed = 4
        if speed > 12:
            speed = 12
        
        
    #     print(countg, counttime, speed)
        
        # create breathing effect
        if countg >= 160 and state == 'in':
            state = 'ex'
            counttime = time()*1000 - start
            start = time() * 1000
        if countg <= 10 and state == 'ex':
            state = 'in'
            counttime = time()*1000 - start
            start = time() * 1000
        
        for i in range(30):
            if i < numlight:
                np[i] = (0,int(countg),0)
            else:
                np[i] = (0,0,0)
        np.write()
        
        if state == 'in':
            countg += speed
        if state == 'ex':
            countg -= speed
        # send data to protopie
        print('pace||'+str(pace))
        print('breathe||'+str(int((countg-10)/1.5)))
        print('runtime||'+str((time() - runningtime)/60))
    
    # pushup state
    if programstate == 'pushup':
        r_val = reflect.get_analog_value()
        if r_val > 56000:
            r_val = 56000
        # activate when hand is facing down
        if imu_val[2] > 0.5:
            # count the pushups
            if r_val < 50000:
                if pushupcheck == False:
                    pushup += 1
                    pushupcheck = True
            if pushupcheck == True and r_val > 52000:
                pushupcheck = False
        # send data to protopie
        print('pushup||'+str(pushup))
        print('pushuploca||'+str(int((r_val-40000)/60)))
        print('pushuptime||'+str((time() - pushuptime)/60))

    
    sleep_ms(50)


