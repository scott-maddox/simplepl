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
import pyqtgraph as pg
from PySide import QtCore

# local imports
from abstract_spectrum import AbstractSpectrum

# Use black text on white background
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

class SpectraPlotItem(pg.PlotItem):
    #TODO: allow adding and removing spectrum
    def __init__(self, parent=None, name=None, labels=None,
                 title=None, viewBox=None, axisItems=None, enableMenu=True,
                 *spectra, **kwargs):
        '''
        **Keyword arguments:**
        
            ================ ================================================
            xaxis            Can be 'wavelength' (default) or 'energy'
            ================ ================================================
        '''
        super(SpectraPlotItem, self).__init__(parent=None, name=None,
            labels=None, title=None, viewBox=None, axisItems=None,
            enableMenu=True, **kwargs)
        self._spectra = []
        self._lines = []
        self._xaxis = kwargs.get('xaxis', 'wavelength')
        for spectrum in spectra:
            self.addSpectrum(spectrum)
    
    @QtCore.Slot(AbstractSpectrum)
    def removeSpectrum(self, spectrum):
        if spectrum not in self._spectra:
            raise ValueError('spectrum not in plot')
        spectrum.sigChanged.disconnect(self.updateLines())
        i = self._spectra.index(spectrum)
        self.removeItem(self._lines[i])
        del self._spectra[i]
        del self._lines[i]

    @QtCore.Slot(AbstractSpectrum)
    def addSpectrum(self, spectrum):
        if spectrum in self._spectra:
            raise ValueError('spectrum alread in plot')
        if self._xaxis == 'wavelength':
            x = spectrum.wavelength
        elif self._xaxis == 'energy':
            x = spectrum.energy
        else:
            raise ValueError('Unsupported value for xaxis: {}'
                             .format(self._xaxis))
        y = spectrum.intensity
        line = self.plot(x=x, y=y)
        self._lines.append(line)
        self._spectra.append(spectrum)
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
    
    def autofit(self):
        raise NotImplementedError()

if __name__ == '__main__':
    from PySide import QtGui, QtCore
    from simulated_spectrum import (GaussianSpectrum, LorentzianSpectrum)
    import numpy as np
    app = QtGui.QApplication([])
    energy = np.linspace(-5, 5, 1000)
    s1 = GaussianSpectrum(energy=energy)
    s2 = LorentzianSpectrum(energy=energy)
    
    w = pg.GraphicsLayoutWidget()
    
    #w = SpectraPlotItem(spectrum, xaxis='energy')
    p = SpectraPlotItem(xaxis='energy')
    p.addSpectrum(s1)
    p.addSpectrum(s2)
    p.removeSpectrum(s1)
    p.addSpectrum(s1)
    
    w.addItem(p, 0, 0)
    w.show()
    w.raise_()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()