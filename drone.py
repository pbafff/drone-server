from dronekit import connect, VehicleMode
from collections import deque
import time

queue = deque()
channels = {'1': 1500, '2': 1500, '3': 1500, '4': 1500}
attitude_listener_callback = None

def connectToDrone():
    #.connect_string = connect_string
    #vehicle = connect('/dev/serial0', baud=115200)
    vehicle = connect('0.0.0.0:14550', wait_ready=True)

    print("Basic pre-arm checks")

    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialize...")
        time.sleep(1)

    print("Arming motors")

    vehicle.mode = VehicleMode("ALT_HOLD")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        vehicle.armed = True
        time.sleep(1)
    
    @vehicle.on_attribute('attitude')
    def attitude_listener(self, name, msg):
        attitude_listener_callback({'attribute': 'attitude', 'payload': msg.__dict__})

    while vehicle.armed:
        if len(queue) > 0:
            output = queue.pop()
            vehicle.channels.overrides = output
        else:
            vehicle.channels.overrides = channels
        time.sleep(0.04)

def handleInput(input):
    print 'INPUTS'
    print input
    axesList = input['axes'].values()
    axesList[3] = -(axesList[3])
    print axesList
    triggerList = [-(input['buttons']['lt']) or input['buttons']['rt']]
    triggerPWM = map(convertToPWM, triggerList)
    axesPWM = map(convertToPWM, axesList)
    print axesPWM
    channels_ = {'1': triggerPWM[0],'2': axesPWM[2], '3': axesPWM[3], '4': axesPWM[1]}
    queue.append(channels_)
    global channels
    channels = channels_

def convertToPWM(val):
    rounded = round(val, 4)
    slope = (2000 - 1000) / (1 - -1)
    return 1000 + slope * (rounded - -1)

def defineAttitudeListenerCallback(callback):
    global attitude_listener_callback
    attitude_listener_callback = callback


