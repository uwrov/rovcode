import pigpio
import logging
import sys
import time
import serial
import busio
import board

#from Adafruit_BNO055 import BNO055
import adafruit_bno055
accelerometer, gyroscope = None, None
pi = None
bno = None

def init():
    global pi, bno
    pi = pigpio.pi("main", 8888)
    # uncomment if using I2C instead of UART
    # i2c = board.I2C()
    # bno = adafruit_bno055.BNO055_I2C(i2c)

    # UART setup
    uart = serial.Serial("/dev/serial0")
    bno = adafruit_bno055.BNO055_UART(uart)

# number = GPIO number
# value = PWM value
def set_pin_pwm(number, value): 
    global pi
    print(number, value)
    pi.set_servo_pulsewidth(number, value)


# unnecessary for physical ROV
async def flush_pin_pwms():
    pass


# updates accelerometer and gyroscope values
async def poll_sensors():
    global accelerometer, gyroscope
    # Gyroscope data (in degrees per second):
    gyroscope = bno.gyro
    # Accelerometer data (in meters per second squared):
    accelerometer = bno.acceleration
    
    print("accel: ", accelerometer)
    print("gyro: ", gyroscope)
