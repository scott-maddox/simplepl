#
#   Copyright (c) 2014, Scott J Maddox
#
#   This file is part of SimplePL.
#
#   SimplePL is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   SimplePL is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with semicontrol.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports

# third party imports
from PySide import QtGui, QtCore

# local imports
from spectrum_plot_widget import SpectrumPlotWidget
from _multi_parameter_control import MultiParameterControl
from measured_spectrum import openMeasuredSpectrum
from simulated_spectrum import (ConstantSpectrum,
                                GaussianSpectrum)
from summed_spectrum import SummedSpectrum


app = QtGui.QApplication([])

# Create main window with grid layout
w = QtGui.QWidget()

layout = QtGui.QHBoxLayout()

# Load the user's measured spectrum
from simplepl.utils import open_dialog

print 'Select a PL file...'
filepath = open_dialog('*.*')
print 'PL File Path:', filepath
print 'Select the system response file to use (if any)...'
sysres_filepath = open_dialog('*.*')
print 'System Response File Path:', sysres_filepath

measuredSpectrum = openMeasuredSpectrum(filepath, sysres_filepath)
energy = measuredSpectrum.getEnergy()
intensity = measuredSpectrum.getIntensity()

# Create some simulated spectrum
bg = ConstantSpectrum(energy=energy)
peak1 = GaussianSpectrum(energy=energy)
peak2 = GaussianSpectrum(energy=energy)
peak3 = GaussianSpectrum(energy=energy)
sum = SummedSpectrum(bg, peak1, peak2, peak3)
sum.energy = energy
bg.constant.max = peak1.amplitude.max = \
    peak2.amplitude.max = peak3.amplitude.max = intensity.max()
peak1.center.min = peak2.center.min = peak3.center.min = energy.min()
peak1.center.max = peak2.center.max = peak3.center.max = energy.max()
peak1.center.value = peak2.center.value = \
    peak3.center.value = energy[energy.size/2]
peak1.fwhm.min = peak2.fwhm.min = \
    peak3.fwhm.min = (energy.max() - energy.min())/100.
peak1.fwhm.max = peak2.fwhm.max = \
    peak3.fwhm.max = (energy.max() - energy.min())
peak1.fwhm.value = peak2.fwhm.value = \
    peak3.fwhm.value = (energy.max() - energy.min())/10

parameters = []
parameters.extend(bg.parameters)
parameters.extend(peak1.parameters)
parameters.extend(peak2.parameters)
parameters.extend(peak3.parameters)

# Add a spectrum plot widget
plot = SpectrumPlotWidget(measuredSpectrum, bg, peak1, peak2, peak3, sum,
                          xaxis='energy')
layout.addWidget(plot)

# Add parameter controls
control = MultiParameterControl(orientation=QtCore.Qt.Horizontal,
                                parameters=parameters)
layout.addWidget(control)

# Show the window
w.setLayout(layout)
w.show()
w.raise_()

# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()