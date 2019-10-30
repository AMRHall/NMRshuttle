# -*- coding: utf-8 -*-
"""
julaboController.py
Author: Andrew Hall
Version: 2.0
Updated: 30th Oct 2019
Script for remote control of Julabo heater/chiller circulator
See https://www.julabo.com/sites/default/files/he-se_protocol_0.pdf for full 
list of available commands.
"""

import tkinter as tk
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import serial, time, sys
import serial.tools.list_ports as list_ports

matplotlib.use('TkAgg')


class dyneo(object):
    def __init__(self):
        for device in list_ports.comports():
                if device.description == 'CORIO':
                        port = device.device
        try:
                self.dyneo = serial.Serial(port=port, baudrate=4800, bytesize=7, parity=serial.PARITY_EVEN, stopbits=1, timeout=0.1)
        except:
                sys.exit(1)
    
    
    def switchOn(self):
        self.dyneo.write(b'out_mode_05 1\r')
        
        
    def switchOff(self):
        self.dyneo.write(b'out_mode_05 0\r')


    def readTemp(self):
        self.dyneo.write(b'in_pv_02\r')
        reply = str(self.dyneo.readline())
        try:
            temp = float(reply.strip("b'\\r\\n"))
        except:
            temp = -1
        return temp
    
    
    def setTemp(self,setpoint):
        self.dyneo.write(bytes('out_sp_00 ' + str(setpoint) + '\r', 'utf-8'))
        print('Set temperature: ' + str(setpoint) + u'\N{DEGREE SIGN}C')
        
    def setTemp_wait(self, setpoint):
        self.setTemp(setpoint)
        startTime = time.time()
        
        temp = self.readTemp()
        
        n = 0
        while n < 60:
            temp = self.readTemp()
            print('\rActual temperature: ' + str(temp) + u'\N{DEGREE SIGN}C', end=' ')
            if temp > setpoint-0.1 and temp < setpoint+0.1:
                n += 1
            else:
                n = 0
            time.sleep(1)
    
        elapsedTime = round(time.time() - startTime)
        print('\nSetpoint reached. Elapsed time: ' + str(elapsedTime))


    def checkStatus(self):
        self.dyneo.write(b'status\r')
        status = str(self.dyneo.readline()).strip("b'\\r\\n")
        return status
    
    def close(self):
        self.dyneo.close()
        sys.exit()




class gui(object):
    
    def __init__(self):
        
        self.on = False
        
        # Create Tkinter window
        self.window = tk.Tk()
        self.window.title("Julabo Dyneo control")
        
        self.set_temp = tk.StringVar(self.window)
        self.set_temp.set(format(20.00, '.2f'))
        
        self.temp_var = tk.StringVar(self.window)
        self.temp_var.set("--.-- \u00B0C")
        
        self.user_input = tk.Entry(self.window, textvariable=self.set_temp, font="Arial 36 bold", width=6, justify="right")
        self.user_input.grid(row=1, column=0)
        self.units = tk.Label(self.window, text="\u00B0C", font="Arial 36 bold", width=2, justify="left").grid(row=1, column=1, sticky="w")
        
        self.current_temp = tk.Label(self.window, textvariable=self.temp_var, font="Arial 36 bold", fg="yellow", bg="black", width=9)
        self.current_temp.grid(row=1, column=2)
        
        self.on_button = tk.Button(self.window, text="ON", fg="green", font="Arial 20 bold", padx=5, pady=5, command=self.switch_on).grid(row=2, column=0, columnspan=2, sticky="wnes")
        self.off_button = tk.Button(self.window, text="OFF", fg="red", font="Arial 20 bold", padx=5, pady=5, command=self.switch_off).grid(row=2, column=2, sticky="wnes")
        
        self.initialise_plot()
        self.d = dyneo()      
        
        ani = animation.FuncAnimation(self.fig, self.animate, interval=200, blit=False)
        
        self.window.mainloop()
        
        
    def initialise_plot(self):
        # Set up plot
        self.fig = plt.figure(figsize=(5,3))
        plt.style.use('dark_background')
        self.fig.patch.set_facecolor('black')
        
        canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        canvas.get_tk_widget().grid(column=0, row=0, columnspan=3)
        
        self.ax = self.fig.add_subplot(1,1,1)
        
        # Create a blank list for each x and y dataset
        self.xs =[]
        self.setpoints = []
        self.temps = []
        
        
    def plot(self):
        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        self.setpoints.append(float(self.set_temp.get()))
        self.temps.append(self.temperature)
        
        # Limit x and y lists to 1500 items
        self.xs = self.xs[-1500:]
        self.setpoints = self.setpoints[-1500:]
        self.temps = self.temps[-1500:]
        
        # Draw plot
        self.ax.clear()
        self.ax.plot(self.xs, self.setpoints, color='r', label='Setpoint')
        self.ax.plot(self.xs, self.temps, color='g', label='Temperature')
        
        self.ax.set_ylabel('Temperature (\u00B0C)')
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        
        
    def switch_on(self):
        self.d.setTemp(float(self.set_temp.get()))
        self.d.switchOn()
        self.on = True
        return
    
    
    def switch_off(self):
        self.d.switchOff()
        self.off = False
        return 
    
    
    def measure_temperature(self):
        self.temperature = self.d.readTemp()
        
        if self.temperature == -1:
            self.current_temp.config(fg="yellow")
            self.temperature = '--.--'
        elif self.temperature > float(self.set_temp.get())-0.1 and self.temperature < float(self.set_temp.get())+0.1:
            self.current_temp.config(fg="green")
            self.temp_var.set("--.-- \u00B0C")
        elif self.temperature > float(self.set_temp.get()):
            self.current_temp.config(fg="red")
        elif self.temperature < float(self.set_temp.get()):
            self.current_temp.config(fg="blue")

        self.temp_var.set(str(self.temperature) + " \u00B0C")
    
    
    def animate(self, i):
        self.measure_temperature()
        
        if self.on == True:
            self.plot()
