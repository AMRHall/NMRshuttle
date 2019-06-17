#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 16:48:12 2019
@author: amrh1c18
"""

import serial
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")

class sensorShield(object):
    n = 9
    
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.port = port
        self.baud = baud
        
        # Set up output data file
        self.outData = open('FS100533_stability_36h.csv', 'w+')
        self.outData.write('Timestamp' + ', ' + 'Temperature 1 (degC)' + ', ' + 'Temperature 2 (degC)' + ', ' + 'Temperature 3 (degC)' + ', ' + 'Field strength (mT)\n')

        
    def openSensors(self):
        # Open connection to arduino
        self.sens = serial.Serial(self.port, self.baud)
        print("Opened connection to sensors")
        # Clear input buffer from Arduino
        print(self.sens.read_all())
            
    def clearBuffer(self):
        self.sens.read_all()
        
    def readSensors(self):
        rawData = str(self.sens.readline())
        if rawData[2] == "{":
            data = rawData.strip("b'{ }\\r\\n").split(", ")
            self.PT100_1 = float(data[0])
            self.PT100_2 = float(data[1])
            self.PT100_3 = float(data[2])
            self.hallSens = float(data[3])
            data = (str(self.PT100_1) + ", " + str(self.PT100_2) + ", " + str(self.PT100_3) + ", " + str(self.hallSens))           
            self.n += 1
            return data
        else:
            print(rawData.strip("b'{ }\\r\\n")) 
            
    def writeData(self):
        if self.n == 10:
            print('Writing data to file...')
            self.outData.write(str(dt.datetime.now()) + ', ' + str(self.PT100_1) + ', ' + str(self.PT100_2) + ', ' + str(self.PT100_3) + ', ' + str(self.hallSens) + '\n')
            self.n = 0

    def intialisePlot(self):
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.ax2 = self.ax1.twinx()
        self.xs = []
        self.t1 = []
        self.t2 = []
        self.t3 = []
        self.hp = []

    def plot(self):
        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        self.t1.append(self.PT100_1)
        self.t2.append(self.PT100_2)
        self.t3.append(self.PT100_3)
        self.hp.append(self.hallSens)
    
        # Limit x and y lists to 100 items
        self.xs = self.xs[-100:]
        self.t1 = self.t1[-100:]
        self.t2 = self.t2[-100:]
        self.t3 = self.t3[-100:]
        self.hp = self.hp[-100:]
    
        # Draw x and y lists
        self.ax1.clear()
        self.ax2.clear()
        ln1 = self.ax1.plot(self.xs, self.t1, color='r', label="PT100_1")
        ln2 = self.ax1.plot(self.xs, self.t2, color='g', label="PT100_2")
        ln3 = self.ax1.plot(self.xs, self.t3, color='b', label="PT100_3")
        ln4 = self.ax2.plot(self.xs, self.hp, color='orange', label="2Dex")
    
        # Format plot
        #plt.xticks(rotation=45, ha='right')
        self.ax1.tick_params(axis='x', rotation=90)
        self.ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
        plt.subplots_adjust(bottom=0.30, right=0.85)
        plt.title('Real-time sensor data')
        self.ax1.set_ylabel('Temperature (deg C)')
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")
        self.ax2.set_ylabel('Field strength (mT)')
        
        # Legend
        lns = ln1+ln2+ln3+ln4
        labs = [l.get_label() for l in lns]
        plt.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=4)
    
    
     
ss=sensorShield()
ss.openSensors()
ss.intialisePlot()

while True:
    data = ss.readSensors()
    ss.writeData()
    if data != None:
        print(data)
        ss.plot()
        plt.pause(0.1)
