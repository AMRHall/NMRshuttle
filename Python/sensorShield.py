#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:21:04 2019

@author: amrh1c18
"""

import tkinter as tk
from tkinter import filedialog
import serial
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import os


class sensorShield(object):
    n = 0
    
    def __init__(self, port='/dev/ttyACM1', baud=9600): 
        # Open connection to arduino
        if os.path.exists(port) == True:
            self.sens = serial.Serial(port, baud)
            print("Opened connection to sensors")
        else:
            print("Serial port not found")
            return
        # Clear input buffer from Arduino
        print(self.sens.read_all())

        
    def clearBuffer(self):
        print(self.sens.read_all())
        
    def readSensors(self):
        rawData = str(self.sens.readline())
        if rawData[2] == "{" and len(rawData) > 24:
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
            
    def openFile(self, interval, path):
        self.outData = open(path, 'w+')
        self.outData.write('Timestamp' + ', ' + 'Temperature 1 (degC)' + ', ' + 'Temperature 2 (degC)' + ', ' + 'Temperature 3 (degC)' + ', ' + 'Field strength (mT)\n')
        self.n = interval - 1
    
    def writeData(self, interval, variables):
        if self.n == interval:
            print('Writing data to file...')
            outStr = str(dt.datetime.now()) 
            outStr += ', '
            if variables[0] == 1:
                outStr += str(self.PT100_1)
            outStr += ', '
            if variables[1]  == 1:
                outStr +=str(self.PT100_2)
            outStr += ', '
            if variables[2]  == 1:
                outStr +=str(self.PT100_3)
            outStr += ', '
            if variables[3]  == 1:
                outStr +=str(self.hallSens)
            self.outData.write(outStr + '\n')
            self.n = 0
            self.outData.flush()


        
class gui(object):
    
    def __init__(self, port='/dev/ttyACM1'):
        # Create Tkinter window
        self.root = tk.Tk()
        self.root.wm_title("Temperature and Field Strength Sensors")
        
        
        # Buttons to select which sensors to measure
        self.var1 = tk.IntVar()
        button1 = tk.Checkbutton(master=self.root, text="PT100_1", variable=self.var1)
        button1.grid(column=0, row=2, pady=(0,15))
        self.var1.set(1)
        
        self.var2 = tk.IntVar()
        button2 = tk.Checkbutton(master=self.root, text="PT100_2", variable=self.var2)
        button2.grid(column=1, row=2, pady=(0,15))
        self.var2.set(1)
        
        self.var3 = tk.IntVar()
        button3 = tk.Checkbutton(master=self.root, text="PT100_3", variable=self.var3)
        button3.grid(column=2, row=2, pady=(0,15))
        self.var3.set(1)
        
        self.var4 = tk.IntVar()
        button4 = tk.Checkbutton(master=self.root, text="2Dex", variable=self.var4)
        button4.grid(column=3, row=2, pady=(0,15))
        self.var4.set(1)
        

        # Buttons for data saving
        self.var5 = tk.IntVar()
        self.button5 = tk.Button(master=self.root, text="Start saving", command=self.startSave)
        self.button5.grid(column=3, row=3)
        self.save = False
        
        tk.Label(master=self.root, text="Data save interval:").grid(column=0, row=3, sticky='w')
        self.var6 = tk.IntVar()
        entrybox1 = tk.Entry(master=self.root, width=5, textvariable=self.var6)
        entrybox1.grid(column=1, row=3, sticky='w')
        self.var6.set(10)
        
        tk.Label(master=self.root, text="File path for data:").grid(column=0, row=4, sticky='w')
        self.entrybox2 = tk.Entry(master=self.root, width=40)
        self.entrybox2.grid(column=1, row=4, columnspan=3, sticky='w')
        self.entrybox2.insert(10, "Sensor_data.csv")
        self.button6 = tk.Button(master=self.root, text="...", command=self.fileDirectory)
        self.button6.grid(column=3, row=4, sticky='w')
        
        button7 = tk.Button(master=self.root, text="EXIT", command=self.exitProgram)
        button7.grid(column=3, row=5, pady=(15,0), sticky='e')

        # Set up sensors and plot
        self.sens=sensorShield(port=port)
        self.intialisePlot()
        self.sens.clearBuffer()
        
        
        # Measure and update graph
        ani = animation.FuncAnimation(self.fig, self.animate, interval=5, blit=False)
        
        
        tk.mainloop()
    
    
    def intialisePlot(self):
        # Set up plot with two y axes and a shared x axis
        self.fig = plt.figure(figsize=(8,5))
    
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().grid(column=0, row=1, columnspan=4)
        tk.Label(self.root,text="Sensor data vs. Time",font=('Arial',18)).grid(column=0, row=0, columnspan=4)
        
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        self.ax2 = self.ax1.twinx()
        
        # Create a blank list for each x and y dataset
        self.xs = []
        self.Temp1 = []
        self.Temp2 = []
        self.Temp3 = []
        self.hallProbe = []

    def plot(self):
        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        self.Temp1.append(self.sens.PT100_1)
        self.Temp2.append(self.sens.PT100_2)
        self.Temp3.append(self.sens.PT100_3)
        self.hallProbe.append(self.sens.hallSens)
        
        # Limit x and y lists to 100 items
        self.xs = self.xs[-100:]
        self.Temp1 = self.Temp1[-100:]
        self.Temp2 = self.Temp2[-100:]
        self.Temp3 = self.Temp3[-100:]
        self.hallProbe = self.hallProbe[-100:]
        
        # Draw x and y lists
        self.ax1.clear()
        self.ax2.clear()
        lns=[]
        if self.var1.get() == 1:
            ln1 = self.ax1.plot(self.xs, self.Temp1, color='r', label="PT100_1")
            lns+=ln1
        if self.var2.get() == 1:
            ln2 = self.ax1.plot(self.xs, self.Temp2, color='g', label="PT100_2")
            lns+=ln2
        if self.var3.get() == 1:
            ln3 = self.ax1.plot(self.xs, self.Temp3, color='b', label="PT100_3")
            lns+=ln3
        if self.var4.get() == 1:
            ln4 = self.ax2.plot(self.xs, self.hallProbe, color='orange', label="2Dex")
            lns+=ln4
    
        # Format plot
        self.ax1.tick_params(axis='x', rotation=90)
        self.ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.fig.subplots_adjust(bottom=0.30, right=0.85)
        self.ax1.set_ylabel('Temperature (deg C)')
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")
        self.ax2.set_ylabel('Field strength (mT)')

        # Legend
        labs = [l.get_label() for l in lns]
        self.ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(0.5, -0.35), ncol=4)

    def animate(self,i):
        data = self.sens.readSensors()
        if self.save == True:
            self.sens.writeData(self.var6.get(), [self.var1.get(),self.var2.get(),self.var3.get(),self.var4.get()])
        if data != None:
            print(data)
            self.plot()
        
    def startSave(self):
        self.sens.openFile(self.var6.get(), self.entrybox2.get())
        self.save = True
        self.button5.config(relief='sunken', fg='red', text='Saving...')
        
    def fileDirectory(self):
        path = filedialog.asksaveasfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        self.entrybox2.delete(0,'end')
        self.entrybox2.insert(10, path)

    def exitProgram(self):
        self.root.destroy()
        return
