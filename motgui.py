# -------------------------------------------------------------
#   File: motgui.py
#   Contributors: Jacob Magers, Daniel Mulkey, Rebecka Tumblin
#   Latest Revision: June 2014
#   Descripton: See readme.md
#   Thank you: Dan Steck and Richard Wagner
# -------------------------------------------------------------

from Tkinter import *
import tkMessageBox
import matplotlib
matplotlib.use('TkAgg')
from tkFileDialog import askopenfilename
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import numpy as np
import csv
import math

root = Tk()
root.wm_title("Magneto-Optical Trap Data Interface")

# Data File Variable
filename = StringVar()
counts = []
time_since = []
running_time = []

# Labels
labelname = StringVar()
graphtitle = StringVar()

# Legend
legend_array = ["0 atoms in MOT","1 atom in MOT","2 atoms in MOT"]

# Transitions Variable
transitions_list = StringVar()

# Time Variables
time_lower = IntVar()
time_upper = IntVar()
time_lower.set(0)
time_upper.set(1000)

# X-Axis Variables
x_lower = DoubleVar()
x_upper = DoubleVar()
x_lower.set(0.0)
x_upper.set(1000.0)

# Y-Axis Vvariables
y_lower = DoubleVar()
y_upper = DoubleVar()
y_lower.set(0.0)
y_upper.set(3200.0)

# Graph Select
graphtype = StringVar()
graphtype.set('Fluorescence')
graphs = ['Fluorescence', 'Power Spectrum']

#Save Variables
fileformat = StringVar()
fileformat.set('.pdf')
save_type = ['.pdf', '.eps', '.png']
savename = StringVar()

# Commands
def import_file():
        filename.set(askopenfilename(parent=root))
        running_time[:] = []
        print "Importing data..."
        with open (filename.get()) as data:
                # The first 5 lines in the .dat files are headers; throw them out
                next(data)
                next(data)
                next(data)
                next(data)
                next(data)
                reader=csv.reader(data,delimiter='\t')
                for row in reader:
                        #counts.append(int(row[0]))
                        #time_since.append(int(row[1]))
                        running_time.append(int(row[2]))               
        print "Binning data..."    
        def bin_rounder(x, base):
                return int(base * math.ceil(float(x)/base)) 
        # Fluorescence bins
        global fhundred_ms_bins
        global fhist_list
        global trimmed_fhundred_ms_bins
        global trimmed_fhist_list
        fbin_width = 5000000           
        fhigh_bin = bin_rounder(max(running_time), fbin_width)
        fns_bins = list(np.linspace(0,fhigh_bin,fhigh_bin/fbin_width+1))
        # Get bins in 100ms second increments for the fluorescence plot
        fhundred_ms_bins = [int(x/fbin_width) for x in fns_bins]
        fhundred_ms_bins.pop()
        fhist, fbin_edges = np.histogram(running_time,bins=fns_bins)
        fhist_list = list(fhist)
        trimmed_fhundred_ms_bins = fhundred_ms_bins[0:len(fhundred_ms_bins)]
        trimmed_fhist_list = fhist_list[0:len(fhist_list)]
        # Power Spectrum bins
        global pone_ms_bins
        global phist_list
        global trimmed_pone_ms_bins
        global trimmed_phist_list
        pbin_width = 50000          
        phigh_bin = bin_rounder(max(running_time), pbin_width)
        pns_bins = list(np.linspace(0,phigh_bin,phigh_bin/pbin_width+1))
        # Get bins in 1ms second increments for the Power Spectrum plot
        pone_ms_bins = [int(x/pbin_width) for x in pns_bins]
        pone_ms_bins.pop()
        phist, pbin_edges = np.histogram(running_time,bins=pns_bins)
        phist_list = list(phist)
        trimmed_phist_list = fhist_list[0:len(phist_list)]
        print "Finding Transitions."
        # Find time stamp associated with a change in the number of trapped atoms
        transitions = []
        threshold = 450
        for i in xrange(3, len(fhist_list)):
                if (math.fabs(fhist_list[i] - fhist_list[i-1])) > threshold:
                        transitions.append(i)
                elif (math.fabs(fhist_list[i] - fhist_list[i-2])) > threshold and (math.fabs(fhist_list[i] - fhist_list[i-1])) < threshold:
                        transitions.append(i-1)
                elif (math.fabs(fhist_list[i] - fhist_list[i-3])) > threshold and (math.fabs(fhist_list[i] - fhist_list[i-2])) < threshold and (math.fabs(fhist_list[i] - fhist_list[i-1])) < threshold:
                        transitions.append(i-2)
        # Get rid of duplicates from transition finder
        transitions2 = []    
        [transitions2.append(i) for i in transitions if not i in transitions2]
        transitions_string = str(transitions2).strip('[]')
        global transitions_list
        transitions_list.set(transitions_string)
        set_graphtype()
        canvas.show()

def set_graphtype():
        print "Setting Graph Type:", graphtype.get()
	graphtype.set(graphtype.get())
        if graphtype.get() == "Fluorescence":
                clear_graph()
                # Set default X and Y limits and make X scale linear
                x_lower.set(float(0.0))
                x_upper.set(float(1000.0))
                y_lower.set(float(1000.0))
                y_upper.set(float(3200.0))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                print "Setting linear X scale."
                ax.set_xscale('linear')
                # Set graph title and labels
                print "Setting Title: Fluorescence"
                graphtitle.set("Fluorescence")
                ax.set_title(str(graphtitle.get()))
                print "Setting Y Label: Photon Count Rate (photons/100ms)"
                ax.set_ylabel("Photon Count Rate (photons/100ms)")
                print "Setting X Label: Time (100ms)"
                ax.set_xlabel("Time (100ms)")
                labelname.set("Fluorescence Data")
                ax.axhline(y=1400, color='k', linestyle='--')
                ax.axhline(y=2050, color='k', linestyle='-.')
                ax.axhline(y=2700, color='k', linestyle=':')
                ax.legend(legend_array, loc=2)
	elif graphtype.get() == "Power Spectrum":
                clear_graph()
                # Set X and Y limits and make X scale logarithmic
                x_lower.set(float(0.01))
                x_upper.set(float(1000.0))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                y_lower.set(float(0.0))
                y_upper.set(float(30000000))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                print "Setting logarithmic X scale."
                ax.set_xscale('log')
                # Repeated on purpose here; fixes bug
                x_lower.set(float(0.01))
                x_upper.set(float(1000.0))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                y_lower.set(float(0.0))
                y_upper.set(float(30000000))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                ax.set_xscale('log')
                # Set graph title and labels
                print "Setting Title: Power Spectrum"
                graphtitle.set("Power Spectrum")
                ax.set_title(str(graphtitle.get()))
                print "Setting Y Label: Intensity^2/Hz (arbitrary units)"
                ax.set_ylabel("Intensity^2/Hz (arbitrary units)")
                print "Setting X Label: Omega (2pi MHz)"
                ax.set_xlabel("Omega (2pi MHz)")
                labelname.set("Power Spectrum Data")
        canvas.show()
        
def set_timelimits():
	print "Setting Time Limits:", time_lower.get(), "to", time_upper.get()
        global trimmed_fhundred_ms_bins
        global trimmed_fhist_list
        global trimmed_phist_list
        global fourier
        global freq
	time_lower.set(int(time_lower.get()))
	time_upper.set(int(time_upper.get()))
	# Make new lists by slicing from entire data set.
        trimmed_fhundred_ms_bins = fhundred_ms_bins[0:len(fhundred_ms_bins)]
        trimmed_fhist_list = fhist_list[0:len(fhist_list)]
	trimmed_fhundred_ms_bins = trimmed_fhundred_ms_bins[time_lower.get():time_upper.get()]
	trimmed_fhist_list = trimmed_fhist_list[time_lower.get():time_upper.get()]
        trimmed_phist_list = phist_list[0:len(phist_list)]
	trimmed_phist_list = trimmed_phist_list[time_lower.get()*100:time_upper.get()*100]
	# Do the FFT for the Power Spectrum Plot.
	print "Taking FFT."
	sample_rate = 1e3
	fourier = np.absolute(np.fft.rfft(trimmed_phist_list))**2
	freq = np.fft.rfftfreq(time_upper.get()*100-time_lower.get()*100, d=1./sample_rate)
	canvas.show()

def set_xlimits():
	print "Setting X Limits:", x_lower.get(), "to", x_upper.get()
        ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
        canvas.show()

def set_ylimits():
        print "Setting Y Limits:", y_lower.get(), "to", y_upper.get()
        ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
        canvas.show()

def set_title():
        print "Setting Title:", graphtitle.get()
        ax.set_title(str(graphtitle.get()))
        canvas.show()

def graph():
	if graphtype.get() == "Fluorescence":
		print "Plotting."
		ax.plot(trimmed_fhundred_ms_bins, trimmed_fhist_list, label=str(labelname.get()))
	elif graphtype.get() == "Power Spectrum":
                if time_lower.get() == 0 and time_upper.get() == 1000:
                        tkMessageBox.showerror(title="Error", message="Please set a time window other than 0 to 1000.")
                else:
                        print "Plotting."
                        ax.plot(freq[1:], fourier[1:], label=str(labelname.get()))
	canvas.show()

def clear_graph():
        ax.clear()
        if graphtype.get() == "Fluorescence":
                # Set default X and Y limits and make X scale linear
                x_lower.set(float(0.0))
                x_upper.set(float(1000.0))
                y_lower.set(float(1000.0))
                y_upper.set(float(3200.0))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                print "Clearing Plot. Resetting axes."
                ax.set_xscale('linear')
                # Set graph title and labels
                graphtitle.set("Fluorescence")
                ax.set_title(str(graphtitle.get()))
                ax.set_ylabel("Photon Count Rate (photons/100ms)")
                ax.set_xlabel("Time (100ms)")
                labelname.set("Fluorescence Data")
                ax.axhline(y=1400, color='k', linestyle='--')
                ax.axhline(y=2050, color='k', linestyle='-.')
                ax.axhline(y=2700, color='k', linestyle=':')
                ax.legend(legend_array, loc=2)
	elif graphtype.get() == "Power Spectrum":
                # Set X and Y limits and make X scale logarithmic
                print "Clearing Plot. Resetting axes."
                x_lower.set(float(0.01))
                x_upper.set(float(1000.0))
                y_lower.set(float(0.0))
                y_upper.set(float(30000000))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                ax.set_xscale('log')
                # Repeated on purpose here; fixes bug
                x_lower.set(float(0.01))
                x_upper.set(float(1000.0))
                y_lower.set(float(0.0))
                y_upper.set(float(30000000))
                ax.set_xlim(float(x_lower.get()), float(x_upper.get()))
                ax.set_ylim(float(y_lower.get()), float(y_upper.get()))
                ax.set_xscale('log')
                # Set graph title and labels
                graphtitle.set("Power Spectrum")
                ax.set_title(str(graphtitle.get()))
                ax.set_ylabel("Intensity^2/Hz (arbitrary units)")
                ax.set_xlabel("Omega (2pi MHz)")
                labelname.set("Power Spectrum Data")
        canvas.show()

def save():
	print "Saving as "+str(savename.get())+fileformat.get()
	fname = str(savename.get())+fileformat.get()
	fig1 = plt.gcf()
	fig1.savefig(fname)

def quit_program():
    root.quit()

f = plt.figure()
ax = f.add_subplot(111)

# GUI

# Grid Stuff
title_row = 22 - 20
unused_row1 = 22 - 20
unused_row2 = 22 - 20
graphtype_row = 24 - 20
unused_row3 = 24 - 20
time_lim_row = 25 - 20
unused_row4 = 25 - 20
xlim_row = 27 - 20
unused_row5 = 27 - 20
y_lim_row = 28 - 20
unused_row6 = 28 - 20
tran_row = 30 - 20
unused_row7 = 31 - 20
draw_row = 32 - 20
label_row = 33 - 20
image_row = 34 - 20
export_row = 35 - 20
save_row = 36 - 20
quit_row = 37 - 20

# Figure
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().grid(row=0, column=0, rowspan=20, columnspan = 30, sticky=W)
canvas._tkcanvas.grid(row=0, column=0, rowspan=20, columnspan = 30, sticky=W)
Label(root,text=' ').grid(row=title_row-1, column=0, columnspan=1, sticky=W)

# Get File
Label(root,text=' ').grid(row=title_row, column=0+30, columnspan=1, sticky=W)
Label(root,text='Data File:').grid(row=title_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=25, textvariable=filename).grid(row=title_row, column=2+30, columnspan=4)
Button(root, text="...", command=import_file).grid(row=title_row, column=6+30, rowspan=1)

# Graphs
Label(root,text='Graph: ').grid(row=graphtype_row, column=1+30, columnspan=1, sticky=W)
OptionMenu(root,graphtype,*graphs).grid(row=graphtype_row, column=2+30, columnspan=4, sticky=EW)
Button(root, text="Set", command=set_graphtype).grid(row=graphtype_row, column=6+30, rowspan=1)

# Time Limits
Label(root,text='Time: ').grid(row=time_lim_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=10, textvariable=time_lower).grid(row=time_lim_row, column=2+30, columnspan=2)
Label(root,text='to').grid(row=time_lim_row, column=4+30, rowspan=1, sticky=W)
Entry(root, width=10, textvariable=time_upper).grid(row=time_lim_row, column=4+30, columnspan=2, sticky=E)
Button(root, text="Set", command=set_timelimits).grid(row=time_lim_row, column=6+30, rowspan=1)

# X Limits
Label(root,text='X Limits: ').grid(row=xlim_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=10, textvariable=x_lower).grid(row=xlim_row, column=2+30, columnspan=2)
Label(root,text='to').grid(row=xlim_row, column=4+30, rowspan=1, sticky=W)
Entry(root, width=10, textvariable=x_upper).grid(row=xlim_row, column=4+30, columnspan=2, sticky=E)
Button(root, text="Set", command=set_xlimits).grid(row=xlim_row, column=6+30, rowspan=1)

# Y Limits
Label(root,text='Y Limits: ').grid(row=y_lim_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=10, textvariable=y_lower).grid(row=y_lim_row, column=2+30, columnspan=2)
Label(root,text='to').grid(row=y_lim_row, column=4+30, rowspan=1, sticky=W)
Entry(root, width=10, textvariable=y_upper).grid(row=y_lim_row, column=4+30, columnspan=2, sticky=E)
Button(root, text="Set", command=set_ylimits).grid(row=y_lim_row, column=6+30, rowspan=1)

# Transitions
Label(root,text='Transitions:').grid(row=tran_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=25, textvariable=transitions_list).grid(row=tran_row, column=2+30, columnspan=4)

# Draw/Clear Plot
Button(root, text="Draw Plot", command=graph).grid(row=draw_row, column=2+30, columnspan=2, sticky=EW)
Button(root, text="Clear Plot", command=clear_graph).grid(row=draw_row, column=4+30, columnspan=2, sticky=EW)
Label(root,text=' ').grid(row=draw_row+1, column=0+30, columnspan=1, sticky=W)

# Graph Title
Label(root,text='Title:').grid(row=label_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=25, textvariable=graphtitle).grid(row=label_row, column=2+30, columnspan=4)
Button(root, text="Set", command=set_title).grid(row=label_row, column=6+30, rowspan=1)

# Save Figure
Label(root,text='Save').grid(row=image_row, column=1+30, columnspan=1, sticky=W)
Label(root,text='Figure Image').grid(row=image_row, column=2+30, columnspan=4)
Label(root,text='as:').grid(row=export_row, column=1+30, columnspan=1, sticky=W)
Entry(root, width=25, textvariable=savename).grid(row=export_row, column=2+30, columnspan=4)
OptionMenu(root,fileformat,*save_type).grid(row=export_row, column=6+30, rowspan=1)
Label(root,text=" ").grid(row=save_row, column=1+30, columnspan=1, sticky=W)
Label(root,text='').grid(row=save_row, column=2+30, columnspan=4)
Button(root, text="Save", command=save).grid(row=save_row, column=6+30, rowspan=1)

# Terminate Program
Button(root, text="Quit", command=quit_program).grid(row=quit_row, column=6+30, rowspan=1)

mainloop()
