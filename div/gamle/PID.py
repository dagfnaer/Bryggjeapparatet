# PID Regulator /ivmech @ github.com/ivmech/ivPID/blob/master/PID.puy
from subprocess import check_output
import time
#import matplotlib.pyplot as plt
#import RPi.GPIO as GPIO
import signal
import sys
import os

class PID:
    #####################
    ## PID CONTROLLER  ##
    #####################
    
    def __init__(self,P,I,D):
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.sample_time = 1.0
        self.current_time = time.time()
        self.last_time = self.current_time

        self.clear()

    def clear(self):
        """CLears PID Computations and coefficients"""
        self.setPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup guard (?)
        self.int_error = 0.0
        self.windup_guard = 100.0

        self.output = 0.0

        

    def pid_update(self,current_val):

        error = self.setPoint - current_val

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if(self.ITerm < -self.windup_guard):
                self.ITerm = -self.windup_guard
            elif(self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error/delta_time

            # Store calculations and errors for next time

            self.last_time = self.current_time
            self.last_error = error
            self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
            if(self.output > self.outMax):
                self.output = self.outMax
            elif(self.output < self.outMin):
                self.output = self.outMin

            
    def setKp(self,P):
        self.Kp = P
    def setKi(self,I):
        self.Ki = I
    def setKd(self,D):
        self.Kd = D
        
    def getPoint(self):
        return self.set_point
    def getError(self):
        return self.error

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setSampleTime(self, sample_time):
        """
        PID that should be updated at a regular interval.
        Based on a pre-determined sample time, the PID decides if it should compute or return immediately.
        """
        self.sample_time = sample_time

    def setOutputLim(self, Min, Max):
        """
        Setting the minimum and maximum output values
        """
        if(Min >= Max):
            return
        self.outMin = Min
        self.outMax = Max

        if(self.output > self.outMax):
            self.output = self.outMax
        elif(self.output < self.outMin):
            self.output = self.outMin
    
    

        
