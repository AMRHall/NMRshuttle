
# sensorShield.py
#
# Andrew Hall 2020 (c)
# a.m.r.hall@soton.ac.uk
#
# Python script for measuring temperature and field strength data
# using PT100 temperature sensors and 2Dex hall sensor
# Also includes graphical user interface.
#
# Jul 2020
version = 'v1.4'

import tkinter as tk
from tkinter import filedialog
import serial, sys, time
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import serial.tools.list_ports as list_ports

matplotlib.use('TkAgg')


class sensorShield(object):
    startTime = 0
    
    offset = 0.0
    sensitivity = 51.5


    def __init__(self, baud=9600): 
        # Open connection to arduino
        for device in list_ports.comports():
            if device.manufacturer == 'Arduino Srl (www.arduino.org)':
                port = device.device
        try:
            self.sens = serial.Serial(port, baud, timeout=0.1)
        except:
            print('Sensor device not found')
            if GUI == True:
                errMsg()
            else:
                sys.exit()
        print("Opened connection to sensors")
        # Clear input buffer from Arduino
        print(self.sens.read_all())
        
    def clearBuffer(self):
        print(self.sens.read_all())
        
    def readSensors(self):
        data = None
        buffer = self.sens.readlines()
        for line in buffer:
            rawData = str(line)
            if rawData[2] == "{" and len(rawData) > 45:
                data = rawData.strip("b'{ }\\r\\n").split(", ")
                self.PT100_1 = float(data[0])
                self.PT100_2 = float(data[1])
                self.PT100_3 = float(data[2])
                self.hallSens = round(1000*((float(data[3])-self.offset)/self.sensitivity),2)
                self.dyneoSetTemp = round(float(data[4]),1)
                self.dyneoActualTemp = round(float(data[5]),1)
                data = (str(self.PT100_1) + ", " + str(self.PT100_2) + ", " + str(self.PT100_3) + ", " + str(self.hallSens)+ ", " + str(self.dyneoSetTemp)+ ", " + str(self.dyneoActualTemp))           
            if data != None:
                return data
       # else:
       #     print(rawData.strip("b'{ }\\r\\n")) 
            
    def openFile(self, interval, path):
        self.outData = open(path, 'w+')
        self.outData.write('Timestamp' + ', ' + 'Temperature 1 (degC)' + ', ' + 'Temperature 2 (degC)' + ', ' + 'Temperature 3 (degC)' + ', ' + 'Field strength (mT)' + ',' + 'Dyneo Set Temperature (degC)' + ',' + 'Sample Temperature (degC)\n')
        self.n = interval - 1
    
    def writeData(self, interval, variables):
        elapsedTime = time.time() - self.startTime
        if elapsedTime >= interval:
            print('Writing data to file...')
            outStr = str(dt.datetime.now()) 
            outStr += ', '
            if variables[0] == 1:
                outStr +=str(self.PT100_1)
            outStr += ', '
            if variables[1]  == 1:
                outStr +=str(self.PT100_2)
            outStr += ', '
            if variables[2]  == 1:
                outStr +=str(self.PT100_3)
            outStr += ', '
            if variables[3]  == 1:
                outStr +=str(self.hallSens)
            outStr += ', '
            if variables[4]  == 1:
                outStr +=str(self.dyneoSetTemp)
            outStr += ', '
            if variables[5]  == 1:
                outStr +=str(self.dyneoActualTemp)
            self.outData.write(outStr + '\n')
            self.outData.flush()
            self.startTime = time.time()



        
class gui(object):
    
    def __init__(self):
        # Set up sensors
        self.sens=sensorShield()
    	
        # Create Tkinter window
        self.root = tk.Tk()
        self.root.wm_title("Temperature and Field Strength Sensors")
      
        # Create frames for layout
        self.frame1 = tk.Frame(self.root)
        self.frame2 = tk.Frame(self.root)
        self.frame3 = tk.Frame(self.root)
        
        
        # Buttons to select which sensors to measure
        self.PT100_1_display = tk.IntVar()
        PT100_1_button = tk.Checkbutton(master=self.frame1, text="PT100_1", variable=self.PT100_1_display)
        self.PT100_1_display.set(1)
        
        self.PT100_2_display = tk.IntVar()
        PT100_2_button = tk.Checkbutton(master=self.frame1, text="PT100_2", variable=self.PT100_2_display)
        self.PT100_2_display.set(1)
        
        self.PT100_3_display = tk.IntVar()
        PT100_3_button = tk.Checkbutton(master=self.frame1, text="PT100_3", variable=self.PT100_3_display)
        self.PT100_3_display.set(1)
        
        self.HallSens_display = tk.IntVar()
        HallSens_button = tk.Checkbutton(master=self.frame1, text="Hall sensor", variable=self.HallSens_display)
        self.HallSens_display.set(1)
        
        self.SetTemp_display = tk.IntVar()
        SetTemp_button = tk.Checkbutton(master=self.frame1, text="Set temperature", variable=self.SetTemp_display)
        self.SetTemp_display.set(1)
        
        self.SampleTemp_display = tk.IntVar()
        SampleTemp_button = tk.Checkbutton(master=self.frame1, text="Sample temperature", variable=self.SampleTemp_display)
        self.SampleTemp_display.set(1)       


        # Buttons for data saving
        self.save_var = tk.IntVar()
        self.save_button = tk.Button(master=self.frame2, text="Start saving", command=self.startSave, width=12)
        self.save = False
        
        SaveInterval_label = tk.Label(master=self.frame2, text="Data save interval (s):")
        self.SaveInterval = tk.IntVar()
        self.SaveInterval_input = tk.Entry(master=self.frame2, width=5, textvariable=self.SaveInterval)
        self.SaveInterval.set(10)
        
        FilePath_label = tk.Label(master=self.frame2, text="File path for data:")
        self.FilePath = tk.Entry(master=self.frame2, width=40)
        self.FilePath.insert(10, "Sensor_data.csv")
        self.FilePath_button = tk.Button(master=self.frame2, text="...", command=self.fileDirectory)
        
        Exit_button = tk.Button(master=self.root, text="EXIT", command=self.exitProgram)


        # Settings for Hall sensor calibration
        HallSensOffset_label = tk.Label(master=self.frame2, text="Hall sensor offset:")
        self.HallSensOffset = tk.Entry(master=self.frame2, width=10)
        self.HallSensOffset.insert(10, self.sens.offset)

        HallSensSensitivity_label = tk.Label(master=self.frame2, text="Hall sensor sensitivity:")
        self.HallSensSensitivity = tk.Entry(master=self.frame2, width=10)
        self.HallSensSensitivity.insert(10, self.sens.sensitivity)


        # Plot settings
        # Temperature plot
        Temp_max_label = tk.Label(master=self.frame3, text="Temperature scale maximum:")
        self.Temp_autoscale_max = tk.IntVar()
        Temp_autoscale_button1 = tk.Checkbutton(master=self.frame3, text="Auto", variable=self.Temp_autoscale_max)
        self.Temp_autoscale_max.set(1)        
        self.Temp_max = tk.Entry(master=self.frame3, width=10)

        Temp_min_label = tk.Label(master=self.frame3, text="Temperature scale minimum:")
        self.Temp_autoscale_min = tk.IntVar()
        Temp_autoscale_button2 = tk.Checkbutton(master=self.frame3, text="Auto", variable=self.Temp_autoscale_min)
        self.Temp_autoscale_min.set(1)        
        self.Temp_min = tk.Entry(master=self.frame3, width=10)    
        
        # Field plot
        Field_max_label = tk.Label(master=self.frame3, text="Field scale maximum:")
        self.Field_autoscale_max = tk.IntVar()
        Field_autoscale_button1 = tk.Checkbutton(master=self.frame3, text="Auto", variable=self.Field_autoscale_max)
        self.Field_autoscale_max.set(1)        
        self.Field_max = tk.Entry(master=self.frame3, width=10)

        Field_min_label = tk.Label(master=self.frame3, text="Field scale minimum:")
        self.Field_autoscale_min = tk.IntVar()
        Field_autoscale_button2 = tk.Checkbutton(master=self.frame3, text="Auto", variable=self.Field_autoscale_min)
        self.Field_autoscale_min.set(1)        
        self.Field_min = tk.Entry(master=self.frame3, width=10)            
        
        TimeScale_label = tk.Label(master=self.frame3, text="Number of time points to plot:")
        self.TimePoints = tk.Entry(master=self.frame3, width=10)
        self.TimePoints.insert(0,1500)
        
        # Layout elements
        self.frame1.grid(column=0, row=2, columnspan=3)
        self.frame2.grid(column=0, row=3)
        self.frame3.grid(column=1, row=3)
        
        PT100_1_button.grid(column=0, row=0, padx=5, pady=(0,15))
        PT100_2_button.grid(column=1, row=0, padx=5, pady=(0,15))
        PT100_3_button.grid(column=2, row=0, padx=5, pady=(0,15))        
        HallSens_button.grid(column=3, row=0, padx=5, pady=(0,15))
        SetTemp_button.grid(column=4, row=0, padx=5, pady=(0,15))
        SampleTemp_button.grid(column=5, row=0, padx=5, pady=(0,15))
        
        self.save_button.grid(column=2, row=0)        
        SaveInterval_label.grid(column=0, row=0, sticky='w')
        self.SaveInterval_input.grid(column=1, row=0, sticky='w')
        FilePath_label.grid(column=0, row=1, sticky='w')
        self.FilePath.grid(column=1, row=1, columnspan=3, sticky='w')
        self.FilePath_button.grid(column=4, row=1, sticky='w')     
     
        HallSensOffset_label.grid(column=0, row=2, sticky='w')
        self.HallSensOffset.grid(column=1, row=2, sticky='w')
        HallSensSensitivity_label.grid(column=0, row=3, sticky='w')
        self.HallSensSensitivity.grid(column=1, row=3, sticky='w')
        
        Temp_max_label.grid(column=0, row=0, sticky='w')
        self.Temp_max.grid(column=1, row=0)
        Temp_autoscale_button1.grid(column=2, row=0)
        Temp_min_label.grid(column=0, row=1, sticky='w')
        self.Temp_min.grid(column=1, row=1)
        Temp_autoscale_button2.grid(column=2, row=1)
        
        Field_max_label.grid(column=0, row=2, sticky='w')
        self.Field_max.grid(column=1, row=2)
        Field_autoscale_button1.grid(column=2, row=2)
        Field_min_label.grid(column=0, row=3, sticky='w')
        self.Field_min.grid(column=1, row=3)
        Field_autoscale_button2.grid(column=2, row=3)
        
        TimeScale_label.grid(column=0, row=4, sticky='w')
        self.TimePoints.grid(column=1, row=4)
               
        Exit_button.grid(column=2, row=6, pady=(15,0), sticky='e')       
        
        
        
        # Set up plot
        self.intialisePlot()
        self.sens.clearBuffer()

        
        # Measure and update graph
        ani = animation.FuncAnimation(self.fig, self.animate, interval=5, blit=False)
        
        
        tk.mainloop()
    
    
    def intialisePlot(self):
        # Set up plot with two y axes and a shared x axis
        self.fig = plt.figure(figsize=(12,5))
    
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().grid(column=0, row=1, columnspan=3)
        tk.Label(self.root,text="Sensor data vs. Time",font=('Arial',18)).grid(column=0, row=0, columnspan=6)
        
        self.ax1 = self.fig.add_subplot(1, 2, 1)
        self.ax2 = self.fig.add_subplot(1, 2, 2)
        
        # Create a blank list for each x and y dataset
        self.xs = []
        self.Temp1 = []
        self.Temp2 = []
        self.Temp3 = []
        self.hallProbe = []
        self.DyneoSet = []
        self.SampleTemp = []


    def plot(self):

        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        self.Temp1.append(self.sens.PT100_1)
        self.Temp2.append(self.sens.PT100_2)
        self.Temp3.append(self.sens.PT100_3)
        self.hallProbe.append(self.sens.hallSens)
        self.DyneoSet.append(self.sens.dyneoSetTemp)
        self.SampleTemp.append(self.sens.dyneoActualTemp)
        
        # Limit x and y lists to number of time points set (default is around 5 min)
        points = int(self.TimePoints.get())
        self.xs = self.xs[-points:]
        self.Temp1 = self.Temp1[-points:]
        self.Temp2 = self.Temp2[-points:]
        self.Temp3 = self.Temp3[-points:]
        self.hallProbe = self.hallProbe[-points:]
        self.DyneoSet = self.DyneoSet[-points:]
        self.SampleTemp = self.SampleTemp[-points:]
        
        # Draw x and y lists
        self.ax1.clear()
        self.ax2.clear()
        lns=[]
        if self.PT100_1_display.get() == 1:
            ln1 = self.ax1.plot(self.xs, self.Temp1, color='r', label="PT100_1")
            lns+=ln1
        if self.PT100_2_display.get() == 1:
            ln2 = self.ax1.plot(self.xs, self.Temp2, color='g', label="PT100_2")
            lns+=ln2
        if self.PT100_3_display.get() == 1:
            ln3 = self.ax1.plot(self.xs, self.Temp3, color='b', label="PT100_3")
            lns+=ln3
        if self.HallSens_display.get() == 1:
            ln4 = self.ax2.plot(self.xs, self.hallProbe, color='orange', label="Hall sensor")
            lns+=ln4
        if self.SetTemp_display.get() == 1:
            ln5 = self.ax1.plot(self.xs, self.DyneoSet, color='r', linestyle="dashed", label="Set temperature")
            lns+=ln5
        if self.SampleTemp_display.get() == 1:
            ln6 = self.ax1.plot(self.xs, self.SampleTemp, color='g', linestyle="dashed", label="Sample temperature")
            lns+=ln6
    
        # Format plot
        self.ax1.tick_params(axis='x', rotation=90)
        self.ax1.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.ax2.tick_params(axis='x', rotation=90)
        self.ax2.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.fig.subplots_adjust(bottom=0.30, right=0.85)
        self.ax1.set_ylabel('Temperature (deg C)')
        self.ax2.yaxis.tick_right()
        self.ax2.yaxis.set_label_position("right")
        self.ax2.set_ylabel('Field strength (mT)')
        
        Temp_min, Temp_max = self.ax1.get_ylim()
        Field_min, Field_max = self.ax2.get_ylim()
        
        if self.Temp_autoscale_max.get() == 1:
            self.Temp_max.delete(0,tk.END)
            self.Temp_max.insert(10, round(Temp_max+10,0))
            Temp_max = round(Temp_max+10,0)
        else:
            Temp_max = float(self.Temp_max.get())
        if self.Temp_autoscale_min.get() == 1:
            self.Temp_min.delete(0,tk.END)
            self.Temp_min.insert(10, round(Temp_min-10,0))
            Temp_min = round(Temp_min-10,0)
        else:
            Temp_min = float(self.Temp_min.get())
        
        if self.Field_autoscale_max.get() == 1:
            self.Field_max.delete(0,tk.END)
            self.Field_max.insert(10, round(Field_max+10,0))
            Field_max = round(Field_max+10,0)
        else:
            Field_max = float(self.Field_max.get())
        if self.Field_autoscale_min.get() == 1:
            self.Field_min.delete(0,tk.END)
            self.Field_min.insert(10, round(Field_min-10,0))
            Field_min = round(Field_min-10,0)
        else:
            Field_min = float(self.Field_min.get())        
        
        self.ax1.set_ylim(Temp_min, Temp_max)
        self.ax2.set_ylim(Field_min, Field_max)

        # Legend
        labs = [l.get_label() for l in lns]
        self.ax1.legend(lns, labs, loc='upper center', bbox_to_anchor=(1.1, -0.35), ncol=6)

    def animate(self,i):
        # Update Hall sensor settings
        self.sens.offset = float(self.HallSensOffset.get())
        self.sens.sensitivity = float(self.HallSensSensitivity.get())

        data = self.sens.readSensors()
        if self.save == True:
            self.sens.writeData(self.SaveInterval.get(), [self.PT100_1_display.get(),self.PT100_2_display.get(),self.PT100_3_display.get(),self.HallSens_display.get(),self.SetTemp_display.get(),self.SampleTemp_display.get()])
        if data != None:
            print(data)
            self.plot()
        
    def startSave(self):
        self.sens.openFile(self.save_var.get(), self.FilePath.get())
        self.save = True
        self.save_button.config(relief='sunken', fg='red', text='Saving...')
        
    def fileDirectory(self):
        path = filedialog.asksaveasfilename(title = "Select file",filetypes = (("csv files","*.csv"),("all files","*.*")))
        self.FilePath.delete(0,'end')
        self.FilePath.insert(10, path)
        
    def exitProgram(self):
        self.root.quit() 
        self.root.destroy()
        sys.exit()
        
        
        
class errMsg(object):
	
    def __init__(self):
        self.errMsg = tk.Tk()
        self.errMsg.eval('tk::PlaceWindow . center')
        self.errMsg.wm_title("Temperature and Field Strength Sensors")
        
        exitButton_label = tk.Label(master=self.errMsg, text="Sensor device not found!", font =('Arial', 14))
        exitButton = tk.Button(master=self.errMsg, text="EXIT", command=self.exitProgram)

        exitButton_label.grid(column=0, row=0, padx=50, pady=[20,10])
        exitButton.grid(column=0, row=1, pady=20)
        
        tk.mainloop()
   
    def exitProgram(self):
        self.errMsg.destroy()
        sys.exit()
        
        
        
GUI = True
gui()

        
