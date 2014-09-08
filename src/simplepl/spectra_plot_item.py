#
#   Copyright (c) 2013-2014, Scott J Maddox
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
#   License along with SimplePL.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports

# third party imports
from PySide import QtCore
import pyqtgraph as pg
from pyqtgraph.graphicsItems.PlotItem import PlotItem
from pyqtgraph.graphicsItems.ViewBox import ViewBox
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataItem

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
        xAxisView : str
            can be 'wavelength' (default) or 'energy'
        '''
        super(SpectraPlotItem, self).__init__(parent=None, name=None,
            labels=None, title=None, viewBox=None, axisItems=None,
            enableMenu=True, **kwargs)
        self._spectra = []
        self._signalLines = []
        self._rawSignalLines = []
        self._phaseLines = []
        self._xAxisView = kwargs.get('xAxisView', 'wavelength')
        self._phaseViewBox = None
        self.showAxis('right')

        # Label the axes
        self.setLabel('left', 'Signal', 'V')
        self.setLabel('right', 'Phase', '&deg;')
        self.updateXAxisLabel()

        # Add the spectra
        for spectrum in spectra:
            self.addSpectrum(spectrum)

    def updateLogMode(self):
        x = self.ctrl.logXCheck.isChecked()
        y = self.ctrl.logYCheck.isChecked()
        for i in self.items:
            if hasattr(i, 'setLogMode'):
                i.setLogMode(x,y)
        self.getAxis('bottom').setLogMode(x)
        self.getAxis('top').setLogMode(x)
        self.getAxis('left').setLogMode(y)
        #self.getAxis('right').setLogMode(y)  # disable log mode for phase axis
        self.enableAutoRange()
        self.recomputeAverages()

    def updateXAxisLabel(self):
        if self._xAxisView == 'wavelength':
            self.setLabel('bottom', 'Wavelength (nm)', '')
        elif self._xAxisView == 'energy':
            self.setLabel('bottom', 'Energy', 'eV')

    def setXAxisView(self, s):
        self._xAxisView = s
        self.updateXAxisLabel()
        self.updateLines()

    def _getPhaseViewBox(self):
        if self._phaseViewBox is None:
            # Initialize it
            self._phaseViewBox = ViewBox()
            self.scene().addItem(self._phaseViewBox)
            self.getAxis('right').linkToView(self._phaseViewBox)
            self._phaseViewBox.setXLink(self)
            self.updateViews()
            self.vb.sigResized.connect(self.updateViews)
        return self._phaseViewBox

    def updateViews(self):
        # View has resized; update auxiliary views to match
        self._phaseViewBox.setGeometry(self.vb.sceneBoundingRect())

        # need to re-update linked axes since this was called
        # incorrectly while views had different shapes.
        # (probably this should be handled in ViewBox.resizeEvent)
        self._phaseViewBox.linkedViewChanged(self.vb,
                                             self._phaseViewBox.XAxis)

    def getColor(self):
        return pg.mkColor('b')

    @QtCore.Slot(AbstractSpectrum)
    def removeSpectrum(self, spectrum):
        if spectrum not in self._spectra:
            raise ValueError('spectrum not in plot')
        spectrum.sigChanged.disconnect(self.updateLines())
        i = self._spectra.index(spectrum)
        self._spectra.pop(i)
        self.removeItem(self._signalLines.pop(i))
        self.removeItem(self._rawSignalLines.pop(i))
        self._getPhaseViewBox().removeItem(self._phaseLines.pop(i))

    def getX(self, spectrum):
        if self._xAxisView == 'wavelength':
            return spectrum.getWavelength()
        elif self._xAxisView == 'energy':
            return spectrum.getEnergy()
        else:
            raise ValueError('Unsupported value for xaxis: {}'
                             .format(self._xAxisView))

    @QtCore.Slot(AbstractSpectrum)
    def addSpectrum(self, spectrum):
        if spectrum in self._spectra:
            raise ValueError('spectrum alread in plot')

        signalColor = self.getColor()
        rawSignalColor = signalColor.lighter()
        phaseColor = rawSignalColor.lighter(120)

        signalLine = self.plot(x=self.getX(spectrum),
                               y=spectrum.getSignal(),
                                  pen=pg.mkPen(signalColor))
        rawSignalLine = self.plot(x=self.getX(spectrum),
                                  y=spectrum.getRawSignal(),
                                  pen=pg.mkPen(rawSignalColor,
                                               style=QtCore.Qt.DashLine))
        phaseLine = PlotDataItem(x=self.getX(spectrum),
                                 y=spectrum.getPhase(),
                                 pen=pg.mkPen(phaseColor,
                                              style=QtCore.Qt.DotLine))
        self._getPhaseViewBox().addItem(phaseLine)

        self._signalLines.append(signalLine)
        self._rawSignalLines.append(rawSignalLine)
        self._phaseLines.append(phaseLine)
        self._spectra.append(spectrum)
        spectrum.sigChanged.connect(self.updateLines)

    def updateLines(self):
        for spectrum, line in zip(self._spectra, self._signalLines):
            line.setData(x=self.getX(spectrum),
                         y=spectrum.getSignal())
        for spectrum, line in zip(self._spectra, self._rawSignalLines):
            line.setData(x=self.getX(spectrum),
                         y=spectrum.getRawSignal())
        for spectrum, line in zip(self._spectra, self._phaseLines):
            line.setData(x=self.getX(spectrum),
                         y=spectrum.getPhase())
