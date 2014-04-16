#
#   Copyright (c) 2013, Scott J Maddox
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
import pyqtgraph as pg

# local imports
from abstract_spectrum import AbstractSpectrum

# Use black text on white background
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

class SpectrumPlotWidget(pg.PlotWidget):
    #TODO: allow adding and removing spectrum
    def __init__(self, *spectra, **kwargs):
        '''
        **Keyword arguments:**
        
            ================ ================================================
            xaxis            Can be 'wavelength' (default) or 'energy'
            ================ ================================================
        '''
        super(SpectrumPlotWidget, self).__init__()
        self._spectra = spectra
        self._xaxis = kwargs.get('xaxis', 'wavelength')
        self._lines = []
        for spectrum in spectra:
            if self._xaxis == 'wavelength':
                x = spectrum.wavelength
            elif self._xaxis == 'energy':
                x = spectrum.energy
            else:
                raise ValueError('Unsupported value for xaxis: {}'
                                 .format(self._xaxis))
            y = spectrum.intensity
            line = self.plotItem.plot(x=x, y=y)
            self._lines.append(line)
            spectrum.sigChanged.connect(self.updateLines)
    
    def updateLines(self):
        for spectrum, line in zip(self._spectra, self._lines):
            if self._xaxis == 'wavelength':
                x = spectrum.wavelength
            elif self._xaxis == 'energy':
                x = spectrum.energy
            else:
                raise ValueError('Unsupported value for xaxis: {}'
                                 .format(self._xaxis))
            y = spectrum.intensity
            line.setData(x=x, y=y)
if __name__ == '__main__':
    from simulated_spectrum import (GaussianSpectrum)
    import numpy as np
    app = QtGui.QApplication([])
    energy = np.linspace(-5, 5, 100)
    spectrum = GaussianSpectrum(energy=energy)
    
    w = SpectrumPlotWidget(spectrum, xaxis='energy')
    w.show()
    w.raise_()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()