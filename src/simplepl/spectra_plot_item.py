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
from PySide import QtCore
import pyqtgraph as pg
from pyqtgraph.graphicsItems.PlotItem import PlotItem

# local imports
from abstract_spectrum import AbstractSpectrum

# Use black text on white background
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


class SpectraPlotItem(PlotItem):

    def __init__(self, parent=None, name=None, labels=None,
                 title=None, viewBox=None, axisItems=None, enableMenu=True,
                 *spectra, **kwargs):
        '''
        Keyword Arguments
        -----------------
        xaxis : str
            can be 'wavelength' (default) or 'energy'
        '''
        super(SpectraPlotItem, self).__init__(parent=None, name=None,
            labels=None, title=None, viewBox=None, axisItems=None,
            enableMenu=True, **kwargs)
        self._spectra = []
        self._signalLines = []
        self._rawSignalLines = []
        self._PhaseLines = []
        self._xaxis = kwargs.get('xaxis', 'wavelength')
        for spectrum in spectra:
            self.addSpectrum(spectrum)

        self._signalPen = pg.mkPen('b')
        self._rawSignalPen = pg.mkPen('#5050B0', style=QtCore.Qt.DashLine)

    @QtCore.Slot(AbstractSpectrum)
    def removeSpectrum(self, spectrum):
        if spectrum not in self._spectra:
            raise ValueError('spectrum not in plot')
        spectrum.sigChanged.disconnect(self.updateLines())
        i = self._spectra.index(spectrum)
        self.removeItem(self._signalLines[i])
        del self._spectra[i]
        del self._signalLines[i]

    def getX(self, spectrum):
        if self._xaxis == 'wavelength':
            return spectrum.getWavelength()
        elif self._xaxis == 'energy':
            return spectrum.getEnergy()
        else:
            raise ValueError('Unsupported value for xaxis: {}'
                             .format(self._xaxis))

    @QtCore.Slot(AbstractSpectrum)
    def addSpectrum(self, spectrum):
        if spectrum in self._spectra:
            raise ValueError('spectrum alread in plot')

        signalLine = self.plot(x=self.getX(spectrum),
                               y=spectrum.getSignal(),
                               pen=self._signalPen)
        rawSignalLine = self.plot(x=self.getX(spectrum),
                                  y=spectrum.getRawSignal(),
                                  pen=self._rawSignalPen)
        self._signalLines.append(signalLine)
        self._rawSignalLines.append(rawSignalLine)
        self._spectra.append(spectrum)
        spectrum.sigChanged.connect(self.updateLines)

    def updateLines(self):
        for spectrum, line in zip(self._spectra, self._signalLines):
            line.setData(x=self.getX(spectrum),
                         y=spectrum.getSignal())
        for spectrum, line in zip(self._spectra, self._rawSignalLines):
            line.setData(x=self.getX(spectrum),
                         y=spectrum.getRawSignal())
