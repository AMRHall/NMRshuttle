#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 16:48:12 2019

@author: amrh1c18
"""

import serial
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import csv

sens = serial.Serial('/dev/cu.usbmodem14201', 115200)

def readSensors():
    # Read temperature (Celsius)
    rawData = str(sens.readline())
    if rawData[2] == "{":
        data = rawData.strip("b'{ }\\r\\n").split(", ")
        global PT100_1, PT100_2, PT100_3, hallSens
        PT100_1 = float(data[0])
        PT100_2 = float(data[1])
        PT100_3 = float(data[2])
        hallSens = float(data[3])
        writeData()
        #print(str(PT100_1) + ", " + str(PT100_2) + ", " + str(PT100_3) + ", " + str(hallSens))
    else:
        print(rawData.strip("b'{ }\\r\\n"))

def animate(i, xs, ys1, ys2, ys3, ys4):
    
    # Read data from sensors
    readSensors()
    
    # Add x and y to lists
    xs.append(dt.datetime.now().strftime('%H:%M:%S'))
    ys1.append(PT100_1)
    ys2.append(PT100_2)
    ys3.append(PT100_2)
    ys4.append(PT100_2)

    # Limit x and y lists to 100 items
    xs = xs[-100:]
    ys1 = ys1[-100:]
    ys2 = ys2[-100:]
    ys3 = ys3[-100:]
    ys4 = ys4[-100:]
    
    # Draw x and y lists
    ax1.clear()
    ax2.clear()
    ax1.plot(xs, ys1)
    ax1.plot(xs, ys2)
    ax1.plot(xs, ys3)
    ax2.plot(xs, ys4)

    # Format plot
    fig.autofmt_xdate()
    plt.subplots_adjust(bottom=0.30)
    ax1.set_ylabel('Temperature (deg C)')
    ax2.set_ylabel('Field strength (mT)')

def writeData():
    if n == 0 or n == 10:
        wr.writerow([dt.datetime.now().strftime('%H:%M:%S'), PT100_1, PT100_2, PT100_3, hallSens])
        n = 0
    n += 1
    
# Create figure for plotting
fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax2 = ax1.twiny()
xs = []
ys1 = []
ys2 = []

# Set up output data file
outData = open('testData.csv', 'w+')
wr = csv.writer(outData, delimiter='\t')
wr.writerow(['Timestamp','Temperature 1 (degC)', 'Temperature 2 (degC)', 'Temperature 3 (degC)', 'Field strength (mT)'])
n = 0

# Set up plot to call animate() function periodically
readSensors()
ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys1, ys2), interval=500)
plt.show()


