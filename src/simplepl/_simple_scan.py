# std lib imports
import time
import threading

# third party imports
import numpy as np
import pyqtgraph as pg
from PySide import QtCore, QtGui
import numpy as np

# local imports
from spectra_pro_2500i import SpectraPro2500i
from srs_sr830 import SR830

#####################################################################
# User Variables
#####################################################################

sample_id = r'E120730D'
#focused_to = r'x 0.45, y 3, z 0.4 - OD 0.8'
focused_to = r'endstop - OD 0'

T = 300

wavelength_start = 2600.
wavelength_stop = 5000.1
wavelength_step = 10.
time_constant = .3

#####################################################################

spec = SpectraPro2500i()
sr830 = SR830()

sr830.set_time_constant_seconds(time_constant)
time_constant = sr830.get_time_constant_seconds()
print 'time_constant = %g seconds'%time_constant
delay = time_constant*5

class AcqThread(threading.Thread):
    def __init__(self):
        super(AcqThread, self).__init__()

        
        
        self.fig = plt.figure()

        self.ax3 = self.fig.add_subplot(111)
        self.ax3.set_xlabel('Wavelength (nm)')
        self.ax3.set_ylabel('Signal')
        self.ax3.yaxis.major.formatter.set_powerlimits((0,0))
        self.line3, = self.ax3.plot([float('nan')], 'b-')
        #self.text3 = self.fig.text(0.5, .95, '??? K')
        self.ax4 = self.ax3.twinx()
        self.ax4.set_ylabel('Phase')
        self.line4, = self.ax4.plot([float('nan')], 'r--')

    def run(self):
        self.wants_abort = False
            
        timestamp = time.strftime(r'%Y-%m-%d-%H-%M-%S')
        self.scan()
        filename = 'out/%s - %s - %s - %g sec delay - %d K.txt'%(timestamp,
                                                                 sample_id, 
                                                                 focused_to,
                                                                 delay, T)
        self.save_scan(filename)
    
    def scan(self):
        self.wavelength = []
        self.signal = []
        self.phase = []
        sr830.auto_adjust_sensitivity()
        t0 = time.time()
        for nm in np.arange(wavelength_start, wavelength_stop, wavelength_step):
            spec.goto(nm)
            R, theta = sr830.adjust_and_get_outputs(delay)
            print 'Time: %.1f s, Wavelength: %.1f nm, Signal: %E'%(time.time()-t0, nm, R)

            self.wavelength.append(nm)
            self.signal.append(R)
            self.phase.append(theta)
            
            self.line3.set_data(self.wavelength, self.signal)
            self.line4.set_data(self.wavelength, self.phase)
            if self.wants_abort:
                return

            self.ax3.relim()
            self.ax3.autoscale_view()
            self.ax4.relim()
            self.ax4.autoscale_view()
            self.fig.canvas.draw()
    
    def save_scan(self, filename):
        with open(filename, 'w') as f:
            f.write('Wavelength\tRaw_Signal\tPhase\n')
            for i in xrange(len(self.wavelength)):
                f.write('%.1f\t%E\t%.1f\n'%(self.wavelength[i],
                                            self.signal[i],
                                            self.phase[i]))
        


thread = AcqThread()
thread.start()
plt.show()
thread.wants_abort = True