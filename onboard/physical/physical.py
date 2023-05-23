import pigpio
import logging
import sys
import time
import serial
import busio
import board

# from adafruit_bno055 import BNO055
import adafruit_bno055
accelerometer, gyroscope = None, None
pi = None
bno = None

def init():
    global pi, bno
    pi = pigpio.pi("main", 8888)
    # uart = busio.UART(8, 10)
    # i2c = busio.I2C(board.SCL, board.SDA)
    i2c = board.I2C()
    bno = adafruit_bno055.BNO055_I2C(i2c)
    # bno = BNO055(serial_port='/dev/serial0', rst=12)

# number = GPIO number
# value = PWM value
def set_pin_pwm(number, value): 
    global pi
    # print("number :" +  str(number))
    # print("value: " + str(value))
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
