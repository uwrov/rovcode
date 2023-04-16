import pigpio
import logging
import sys
import time

# from Adafruit_BNO055 import BNO055
accelerometer, gyroscope = None, None
pi = None


def init():
    global pi
    pi = pigpio.pi("main", 8888)
    # bno = BNO055.BNO055(serial_port='/dev/serial0', rst=18)

# number = GPIO number
# value = PWM value
def set_pin_pwm(number, value): 
    global pi
    print("number :" +  str(number))
    print("value: " + str(value))
    pi.set_servo_pulsewidth(number, value)


# unnecessary for physical ROV
async def flush_pin_pwms():
    pass


# updates accelerometer and gyroscope values
async def poll_sensors():
    # # Gyroscope data (in degrees per second):
    # gyroscope = bno.read_gyroscope()
    # # Accelerometer data (in meters per second squared):
    # accelerometer = bno.read_accelerometer()
    pass
