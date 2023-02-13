import pigpio
# import logging
# import sys
# import time

# from Adafruit_BNO055 import BNO055
accelerometer, gyroscope = None, None
pi = None


def init():
    global pi
    pi = pigpio.pi("main", 8888)

# number = GPIO number
# value = PWM value
def set_pin_pwm(number, value): 
    global pi
    pi.set_servo_pulsewidth(number, value)


# unnecessary for physical ROV
async def flush_pin_pwms():
    pass


# updates accelerometer and gyroscope values
async def poll_sensors():
    print('polling physical sensors not yet implemented')
    # TODO implement
