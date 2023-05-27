import core

def proportional(setpoint, measured):
    return setpoint - measured

def integral(p, delta):
    return p * delta

def derivative(p, last_p, delta):
    return -(p - last_p) / delta

def feed_forward():
    return 0 #placeholder value, not sure what to set to for now

# calling on accel and gyro tuples - not sure if this is how it should work
def manipulate_gyro_accel(accel, gyro):
    curr_accel_setpoint = (1, 1, 1) # ARBITRARY
    curr_gyro_setpoint = (1, 1, 1) #ARBITRARY
    k_p = 1
    k_i = 1
    k_d = 1
    for i in range(len(accel)):
        current_p = proportional(curr_accel_setpoint[i], accel[i]) #dependent on a value that idk how to get (curr_setpoint)
        curr_delta = 1 #dk how to get this
        placeholder_last_p = 1 #dk how to get this
        accel[i] = k_p * current_p + k_i * integral(current_p, curr_delta) + k_d * derivative(current_p, 
                placeholder_last_p, curr_delta) + feed_forward()

    for i in range(len(gyro)):
        current_p = proportional(curr_gyro_setpoint[i], gyro[i]) #dependent on a value that idk how to get (curr_setpoint)
        curr_delta = 1 #dk how to get this
        placeholder_last_p = 1 #dk how to get this
        gyro[i] = k_p * current_p + k_i * integral(current_p, curr_delta) + k_d * derivative(current_p, 
                placeholder_last_p, curr_delta) + feed_forward()