#############################
## PID RELAY ##
###########################

import PID
import time
import matplotlib.pyplot as plt
import numpy as np
import signal
import sys
import os
from measuretemp import get_temp
#import RPi.GPIO as GPIO
import random # Random temp input
from time import strftime

relayPin = 6 # Define output relay pin

#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(pin, GPIO.OUT)

#

WindowSize = 5000 # ???
winStartTime = time.time()
def mesh(P, I, D, temp, setPoint):
        pid = PID.PID(P, I, D) # Start PID funksjonen

        # Config PID
        pid.setPoint = setPoint
        pid.setSampleTime(1)
        pid.setOutputLim(0.01,100)
        pid.setWindup(20)

        
        temp = temp

        relay_list = []
        time_list = []
        temp_list = []
        # if(time.time() > nextRead)
        
        pid.pid_update(temp)
        output = pid.output
        #print(output)
        if(time.time() - winStartTime > WindowSize):
                winStartTime += WindowSize
        if(output > time.time() - winStartTime):
                #print("High") # Set relay pin high
                logic = 1
                temp +=0.1
        else:
                #print("Low") # Set relay pin low
                logic = 0
                temp -=0.1
        relay_list.append(logic)
        temp_list.append(temp)
        with open("mesh_temp.csv","a") as log:
                log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(temp)))

        return output
                
if __name__ == "__main__":
    try:
        while True:
            mesh(10, 1, 0.4, L=100)
            time.sleep(2)
    except KeyboardInterrupt:
        print("Done")

##def setup():
##	startTime = time.time() #Get current time
##
##	setPoint = 100
##
##	pid.Range(0, WindowSize) #Set PID range between 0 and the full window size
##
##	pid.SetMode(AUTOMATIC) # Turn the PID on
##
##def main():
##	temp = readADC()
##	pid.Compute() # Compute PID
##
##	############
##	# Turn the output pin on/of based on pid output
##	##########
##	getCurrentTime = time.time()
##	if(getCurrentTime - startTime > WindowSize):
##		startTime += WindowSize
##	if(Output < getCurrentTime - startTime):
##		GPIO(relayPin, True)
##	else:
##		GPIO(relayPin, False)
