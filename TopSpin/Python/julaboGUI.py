# -*- coding: utf-8 -*-
"""
julaboGUI.py
Author: Andrew Hall
Version: 1.0
Updated: Jul 2020

User interface for remote control of Julabo heater/chiller circulator
and flow direction switching valves
"""

import tkinter as tk
import tkinter.scrolledtext as scrolled_text
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import julaboController
import sys

# This is needed to allow matplotlib to work properly on Linux machine.
matplotlib.use('TkAgg')


class gui(object):
    
    def __init__(self):
        
        self.on = False
        
        # Controls for Julabo
        # Create Tkinter window
        self.window = tk.Tk()
        self.window.title("Julabo Dyneo control")
        
        # Create frames for layout
        self.plot_frame = tk.Frame(self.window, bg='black')
        frame1 = tk.Frame(self.window)
        frame2 = tk.LabelFrame(self.window, text="Plot settings")
        frame3 = tk.LabelFrame(self.window, text='Flow direction control')
        frame3b = tk.Frame(frame3)
        frame4 = tk.LabelFrame(self.window, text='Log')
        
        # Set temperature entry box
        self.set_temp = tk.StringVar(frame1)
        self.set_temp.set(format(20.00, '.2f'))
        self.user_input = tk.Entry(frame1, textvariable=self.set_temp, font="Arial 36 bold", width=5, justify="right")
        self.units = tk.Label(frame1, text="\u00B0C", font="Arial 36 bold", width=2, justify="left")
        
        # Measured temperature box
        self.temp_var = tk.StringVar(frame1)
        self.temp_var.set("--.-- \u00B0C")
        self.current_temp = tk.Label(frame1, textvariable=self.temp_var, font="Arial 36 bold", fg="yellow", bg="black", width=7)
        
        # On/off buttons for Julabo
        self.on_button = tk.Button(frame1, text="ON", fg="green", font="Arial 20 bold", padx=5, pady=5, command=self.switch_on)
        self.off_button = tk.Button(frame1, text="OFF", fg="red", font="Arial 20 bold", padx=5, pady=5, command=self.switch_off)
        
        
        # Plot settings
        Temp_max_label = tk.Label(master=frame2, text="Temperature scale maximum:", width=25, anchor="w")
        self.Temp_autoscale_max = tk.IntVar()
        Temp_autoscale_button1 = tk.Checkbutton(master=frame2, text="Auto", variable=self.Temp_autoscale_max)
        self.Temp_autoscale_max.set(1)        
        self.Temp_max = tk.Entry(master=frame2, width=10)
    
        Temp_min_label = tk.Label(master=frame2, text="Temperature scale minimum:", width=25, anchor="w")
        self.Temp_autoscale_min = tk.IntVar()
        Temp_autoscale_button2 = tk.Checkbutton(master=frame2, text="Auto", variable=self.Temp_autoscale_min)
        self.Temp_autoscale_min.set(1)        
        self.Temp_min = tk.Entry(master=frame2, width=10)   
        
        TimeScale_label = tk.Label(master=frame2, text="Number of time points to plot:", width=25, anchor="w")
        self.TimePoints = tk.Entry(master=frame2, width=10)
        self.TimePoints.insert(0,1500)
        
        
        # Controls for valves
        valvePos_label = tk.Label(master=frame3, text="Flow direction:", width=24, anchor="w")
        self.valvePos_var = tk.StringVar(frame3)
        self.valvePos_var.set("\u27f3")
        valvePos = tk.Label(frame3, textvariable=self.valvePos_var, font="Arial 36 bold")
        
        switchDelay_label = tk.Label(master=frame3, text="Delay for flow switching (s):", width=24, anchor="w")
        self.switchDelay = tk.Entry(master=frame3, width=10) 
        self.switchDelay.insert(0,300)
        setDelay = tk.Button(frame3, text="Set", command=self.set_valve_delay)
        
        position_label = tk.Label(master=frame3, text="Set flow direction manually:", width=24, anchor="w")
        self.position_var = tk.StringVar(frame3)
        self.position_var.set('Auto')
        positionA_button = tk.Radiobutton(master=frame3b, text='A', variable=self.position_var, value='A', command=self.set_valve_position)
        positionB_button = tk.Radiobutton(master=frame3b, text='B', variable=self.position_var, value='B', command=self.set_valve_position)
        positionAuto_button = tk.Radiobutton(master=frame3b, text='Auto', variable=self.position_var, value='Auto', command=self.set_valve_position)
        
        self.valve_status = tk.StringVar(frame3)
        
        
        # Log display (units for height and width are in characters)
        self.log = scrolled_text.ScrolledText(master=frame4, width=45, height=5, font="Courier 9")
        
        
        # Layout elements
        self.plot_frame.grid(column=0, row=0, rowspan=2, sticky="we")
        frame1.grid(column=0, row=2)
        frame2.grid(column=1, row=0)
        frame3.grid(column=1, row=1)
        frame4.grid(column=1, row=2, padx=10)
        
        self.user_input.grid(row=0, column=0, padx=6)
        self.units.grid(row=0, column=1, sticky="w")
        self.current_temp.grid(row=0, column=2)
        self.on_button.grid(row=1, column=0, columnspan=2, sticky="wnes")
        self.off_button.grid(row=1, column=2, sticky="wnes")
        
        Temp_max_label.grid(column=0, row=0, sticky='w')
        self.Temp_max.grid(column=1, row=0)
        Temp_autoscale_button1.grid(column=2, row=0)
        Temp_min_label.grid(column=0, row=1, sticky='w')
        self.Temp_min.grid(column=1, row=1)
        Temp_autoscale_button2.grid(column=2, row=1)
        TimeScale_label.grid(column=0, row=4, sticky='w')
        self.TimePoints.grid(column=1, row=4)
        
        valvePos_label.grid(column=0, row=0)
        valvePos.grid(column=1, row=0)
        switchDelay_label.grid(column=0, row=1)
        self.switchDelay.grid(column=1, row=1)
        setDelay.grid(column=2, row=1)
        position_label.grid(column=0, row=2)
        
        frame3b.grid(column=1, row=2, columnspan=3)
        positionA_button.grid(column=0, row=0)
        positionB_button.grid(column=1, row=0)
        positionAuto_button.grid(column=2, row=0)
        
        self.log.grid()
        
        
        
        # Initialise plot, Julabo and valves. If valve module is not connected
        # then disable and grey out buttons.
        self.initialise_plot()
        try:
            self.d = julaboController.dyneo()  
        except:
            errMsg("Dyneo not found")
            
        try:
            self.v = julaboController.valves()
        except:
            self.valve_disable = True
            self.disableChildren(frame3)
            self.add_to_log('Valve interface not found!\n', priority=True)
        else:
            self.valve_disable = False
            
            
        
        # Animate plot
        ani = animation.FuncAnimation(self.fig, self.animate, interval=200, blit=False)
        
        self.window.mainloop()
    


    def disableChildren(self, parent):
        for child in parent.winfo_children():
                wtype = child.winfo_class()
                if wtype not in ('Frame','Labelframe'):
                    child.configure(state='disable')
                else:
                    self.disableChildren(child)
        
        
    def initialise_plot(self):
        # Set up plot
        self.fig = plt.figure(figsize=(6,4))
        plt.style.use('dark_background')
        self.fig.patch.set_facecolor('black')
        
        canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas.get_tk_widget().grid(column=0, row=0, columnspan=3)
        
        self.ax = self.fig.add_subplot(1,1,1)
        
        # Create a blank list for each x and y dataset
        self.xs =[]
        self.setpoints = []
        self.temps = []
        
        
    def plot(self, temperature):
        # Add x and y to lists
        self.xs.append(dt.datetime.now().strftime('%H:%M:%S'))
        try:
            self.setpoints.append(float(self.set_temp.get()))
        except:
            self.setpoints.append(None)
        self.temps.append(temperature)
        
        # Limit x and y lists to number of time points set (default is around 5 min)
        points = int(self.TimePoints.get())
        self.xs = self.xs[-points:]
        self.setpoints = self.setpoints[-points:]
        self.temps = self.temps[-points:]
        
        # Draw plot
        self.ax.clear()
        self.ax.plot(self.xs, self.setpoints, color='r', linestyle="dashed", label='Setpoint')
        self.ax.plot(self.xs, self.temps, color='g', label='Temperature')
        
        self.ax.set_ylabel('Temperature (\u00B0C)')
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        
        
        # Set maximum and minimum plot limits either automatically or using 
        # settings given by user.
        Temp_min, Temp_max = self.ax.get_ylim()
        
        if self.Temp_autoscale_max.get() == 1:
            self.Temp_max.delete(0,tk.END)
            self.Temp_max.insert(10, round(Temp_max+5,0))
            Temp_max = round(Temp_max+5,0)
        else:
            try:
                Temp_max = float(self.Temp_max.get())
            except:
                Temp_max = round(Temp_max+5,0)
        if self.Temp_autoscale_min.get() == 1:
            self.Temp_min.delete(0,tk.END)
            self.Temp_min.insert(10, round(Temp_min-5,0))
            Temp_min = round(Temp_min-5,0)
        else:
            try:
                Temp_min = float(self.Temp_min.get())
            except:
                Temp_min = round(Temp_min-5,0)
            
        self.ax.set_ylim(Temp_min, Temp_max)
        
        
        
        
    def add_to_log(self, string, priority=False):
        if priority == True:
            self.log.insert(tk.END, string, 'priority')
        else:
            self.log.insert(tk.END, string)
        self.log.tag_config('priority', foreground='red')
        self.log.see(tk.END)
        
        
        
    def switch_on(self):
        self.d.setTemp(float(self.set_temp.get()))
        self.d.switchOn()
        self.add_to_log('Julabo: ON\nSet temperature: ' + self.set_temp.get() + ' \u00B0C\n')
        if self.valve_disable == False:
            self.v.switchOn()
            self.set_valve_delay()
        self.on = True
        
    
    
    def switch_off(self):
        self.d.switchOff()
        if self.valve_disable == False:
            self.v.switchOff()
        self.on = False
        self.add_to_log('Julabo: OFF\n')
         
    
    
    def measure_temperature(self):
        self.errors = self.d.checkStatus()
        if self.errors == None:
            pass
        elif self.errors[0] == '-':
            self.add_to_log(self.errors, priority=True)
            self.errors = ''
        
        temperature = self.d.readTemp()
        displayTemp = temperature
        
        try:
            set_temp = float(self.set_temp.get())
        except:
            set_temp = 0.0
        
        # Set the colour of the temperature readout: Blue = too cold, Red = 
        # too hot, Green = just right, Yellow = No data.
        if temperature == None:
            self.current_temp.config(fg="yellow")
            displayTemp = '--.--'
        elif temperature > set_temp-0.1 and temperature < set_temp+0.1:
            self.current_temp.config(fg="green")
        elif temperature > set_temp:
            self.current_temp.config(fg="red")
        else:
            self.current_temp.config(fg="blue")
        
        self.temp_var.set(str(displayTemp) + " \u00B0C")
        
        return temperature
    
    
    
    def get_valve_state(self):
        position = int(self.v.readPosition())
        status = self.v.checkStatus()

        if status != self.valve_status:
            self.valve_status = status
            self.add_to_log("Valves: " + status)
        
        # Set flow direction arrow indicator
        if position == 1:
            self.valvePos_var.set("\u27f2")
        else:
            self.valvePos_var.set("\u27f3")
            
            
    def set_valve_delay(self):
        delay = float(self.switchDelay.get())
        # To stop the valve switching too quickly a minimum delay of 30 seconds
        # is enforced.
        if delay >= 30:
            self.v.setDelay(delay)
            self.add_to_log("Flow switching delay: " + str(delay) + "\n")
        else:
            self.add_to_log("Switching delay must be a minimum of 30 s\n")
            
            
    def set_valve_position(self):
        position = self.position_var.get()
        if position == 'A':
            self.v.switchOff()  # Stop the valve switching
            self.add_to_log("Manual override: Valve position A\n")
        elif position == 'B':
            self.v.switchOff()  # Stop the valve switching
            self.v.setPosition(1)   # Energise both valves
            self.add_to_log("Manual override: Valve position B\n")
        elif self.on == True:
            self.v.switchOn()
        else:
            self.v.switchOff()
        
    
    def animate(self, i):
        temperature = self.measure_temperature()
        
        if self.on == True:
            self.plot(temperature)
        if self.valve_disable == False:
            self.get_valve_state()
                
                
            
            
class errMsg(object):
	
    def __init__(self, message):
        self.errMsg = tk.Tk()
        self.errMsg.eval('tk::PlaceWindow . center')
        self.errMsg.wm_title("Julabo Dyneo Control")
        
        tk.Label(master=self.errMsg, text=message, font =('Arial', 14)).grid(column=0, row=0, columnspan=2, padx=50, pady=[20,10])
        okButton = tk.Button(master=self.errMsg, text="OK", command=self.closeErrMsg)
        exitButton = tk.Button(master=self.errMsg, text="EXIT", command=self.exitProgram)
        
        okButton.grid(column=0, row=1, pady=20)
        exitButton.grid(column=1, row=1, pady=20)
        
        tk.mainloop()
        
    def closeErrMsg(self):
        self.errMsg.destroy()
        
    def exitProgram(self):
        self.errMsg.destroy()
        sys.exit(1)
        
        
gui()
