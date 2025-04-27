import os, sys, io
import M5
from M5 import *
from hardware import RGB
from hardware import I2C
from hardware import Pin

from unit import VibratorUnit
from unit import IMUProUnit
from unit import ENVPROUnit
from unit import ThermalUnit
from unit import GlassUnit

from neopixel import NeoPixel
from time import *
import math


vibrator = VibratorUnit((1, 2))
vibrator.turn_off()

i2c0 = I2C(0, scl=Pin(2), sda=Pin(1), freq=100000)

i2c = I2C(0, scl=Pin(39), sda=Pin(38), freq=100000)
imu = IMUProUnit(i2c)

#faint variable
faint = False
faintcount = 0
fainttime = 0
imu_val = imu.get_accelerometer()
imu_last = imu_val

#thermal variable
thermal = ThermalUnit(i2c)
thermal.set_refresh_rate(0)
np = NeoPixel(Pin(7), 30)
temp_data = []
led_pixels = [[] for _ in range(30)]
sector = 345 / 30

#enviro variable
envpro = ENVPROUnit(i2c0)
env_val = [0,0,0]

glass = GlassUnit(i2c, 0x3d)

def calDir(width,height):
    cx = (width - 1) / 2
    cy = (height - 1) / 2
    temp_data = []
    for y in range(height):
        for x in range(width):
            temp_data.append(thermal.get_pixel_temperature(x,y))
            dx = x - cx
            dy = y - cy
            theta = math.atan2(dy, dx)
            deg = (math.degrees(theta) + 360) % 360
            startAngle = (262.5 - deg + 360) % 360
            
            if startAngle < 345:
                index = int(startAngle / sector)
                led_pixels[index].append(thermal.get_pixel_temperature(x,y))

        

while True:
    M5.update()
    # check fainted
    imu_val = imu.get_accelerometer()
    for i in range(3):
        if abs(imu_val[i] - imu_last[i]) < 0.1:
            faintcount += 1
        else:
            faint = False
    if faintcount >= 3 and faint == False:
        faint = True
        fainttime = time()
        faintcount = 0
    
    if faint == True:
        if time() - fainttime> 5:
            print('faint||'+ 'fainted')
            vibrator.once(freq=100, duty=10, duration=50)
    else:
        print('faint||'+ 'normal')
        
    imu_last = imu_val
    
    #check fire direction
    for sublist in led_pixels:
        sublist.clear()
    calDir(32,24)
    for i in range(30):
        if led_pixels[i]:
            max_temp = max(led_pixels[i])
        max_temp = int(((max_temp)-20)*10)
        if max_temp > 255:
            max_temp = 255
        if max_temp < 0:
            max_temp = 0
        np[i] = (max_temp,30-max_temp,0)
    np.write()     
    thermal.update_temperature_buffer()
    if faint == True:
        blink = np
        for i in range(30):
            np[i] = (0,0,0)
        np.write()
        for i in range(30):
            np[i] = blink[i]
        np.write
    
    #check environment status
    env_val[0] = envpro.get_temperature()
    env_val[1] = envpro.get_humidity()
    env_val[2] = envpro.get_gas_resistance()

    glass.clear()
    Widgets.Label("Temp", 10, 10, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    Widgets.Label(str(int(env_val[0])), 80, 10, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    Widgets.Label("Gas", 10, 20, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    Widgets.Label(str(int(env_val[2])), 80, 20, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    Widgets.Label("Humid", 10, 30, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    Widgets.Label(str(int(env_val[1])), 80, 30, 1.0, 0xffffff, 0x222222, Widgets.FONTS.DejaVu9, glass)
    #check remaining oxygen
    print('temp||'+ str(int(env_val[0])))
    print('gas||'+ str(int(env_val[1])))
    print('humid||'+ str(int(env_val[2])))
    
    sleep_ms(100)

