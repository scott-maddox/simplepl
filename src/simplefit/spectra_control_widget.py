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
import numpy as np

# local imports
from vertical_scroll_area import VerticalScrollArea
from parameter_widgets import BoundedFloatParameterEdit
from spectrum_control_widget import SpectrumControlWidget
from abstract_spectrum import AbstractSpectrum
from measured_spectrum import MeasuredSpectrum
from simulated_spectrum import (ConstantSpectrum, GaussianSpectrum,
                                LorentzianSpectrum,
                                AsymmetricGaussianSpectrum,
                                WaveVectorConservingPLSpectrum,
                                WaveVectorNonConservingPLSpectrum)
from summed_spectrum import SummedSpectrum

class SpectraControlWidget(QtGui.QWidget):
    sigChanged = QtCore.Signal()
    sigSpectrumAdded = QtCore.Signal(AbstractSpectrum)
    sigSpectrumRemoved = QtCore.Signal(AbstractSpectrum)
    def __init__(self, *args, **kwargs):
        super(SpectraControlWidget, self).__init__(*args, **kwargs)
        self._energy = (kwargs.get('energy', None))
        self._energyMin = 0.
        self._energyMax = 1.
        self._intensityMax = 1.
        self._chi2 = np.nan
        self._spectra = []
        self._controls = []
        
        # Construct a summed spectrum
        self.summedSpectrum = SummedSpectrum()
        
        # Construct widgets
        self.parameterEdit = BoundedFloatParameterEdit(
                                            orientation=QtCore.Qt.Horizontal)
        addConstantButton = QtGui.QPushButton('Add Constant')
        addGaussianButton = QtGui.QPushButton('Add Gaussian')
        addLorentzianButton = QtGui.QPushButton('Add Lorentzian')
        addAsymmetricGaussianButton = QtGui.QPushButton('Add Asymmetric Gaussian')
        addWaveVectorConservingPLButton = (
                    QtGui.QPushButton('Add wave vector conserving PL'))
        addWaveVectorNonConservingPLButton = (
                    QtGui.QPushButton('Add wave vector non-conserving PL'))
        addConstantButton.setMinimumHeight(40)
        addGaussianButton.setMinimumHeight(40)
        addLorentzianButton.setMinimumHeight(40)
        addAsymmetricGaussianButton.setMinimumHeight(40)
        addWaveVectorConservingPLButton.setMinimumHeight(40)
        addWaveVectorNonConservingPLButton.setMinimumHeight(40)
        
        # Scroll area for the SpectrumWidgets
        scrollWidget = QtGui.QWidget()
        scroll = VerticalScrollArea()
        scroll.setWidget(scrollWidget)
        
        # Layout
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(5)
        layout.addWidget(self.parameterEdit)
        layout.addWidget(scroll, stretch=1)
        self.scrollLayout = QtGui.QVBoxLayout(scrollWidget)
        self.scrollLayout.addStretch(1)
        layout.addWidget(addConstantButton)
        layout.addWidget(addGaussianButton)
        layout.addWidget(addLorentzianButton)
        layout.addWidget(addAsymmetricGaussianButton)
        layout.addWidget(addWaveVectorConservingPLButton)
        layout.addWidget(addWaveVectorNonConservingPLButton)
        
        # Connect signals and slots
        addConstantButton.clicked.connect(self.addConstantSpectrum)
        addGaussianButton.clicked.connect(self.addGaussianSpectrum)
        addLorentzianButton.clicked.connect(self.addLorentzianSpectrum)
        addAsymmetricGaussianButton.clicked.connect(self.addAsymmetricGaussianSpectrum)
        addWaveVectorConservingPLButton.clicked.connect(
                                    self.addWaveVectorConservingPLSpectrum)
        addWaveVectorNonConservingPLButton.clicked.connect(
                                    self.addWaveVectorNonConservingPLSpectrum)
    
    def setEnergy(self, energy):
        self._energy = energy
        self._energyMin = energy.min()
        self._energyMax = energy.max()
        self.summedSpectrum.energy = energy
        for spectrum in self._spectra:
            spectrum.energy = energy
    
    def setIntensity(self, intensity):
        '''
        Set the intensity array. This is used to provide reasonable
        default simulation parameters.
        '''
        self._intensityMax = intensity.max()

    def addSpectrum(self, s):
        w = SpectrumControlWidget(spectrum=s)
        w.sigRemoveClicked.connect(self.removeSpectrum)
        w.sigParameterChanged.connect(self.parameterEdit._setParameter)
        self.summedSpectrum.addSpectrum(s)
        self.scrollLayout.insertWidget(self.scrollLayout.count() - 1, w)
        self._spectra.append(s)
        self._controls.append(w)
        self.sigSpectrumAdded.emit(s)
    
    @QtCore.Slot(AbstractSpectrum)
    def removeSpectrum(self, s):
        self.summedSpectrum.removeSpectrum(s)
        i = self._spectra.index(s)
        self._controls[i].sigRemoveClicked.disconnect(self.removeSpectrum)
        self._controls[i].sigParameterChanged.disconnect(
                                            self.parameterEdit._setParameter)
        self._controls[i].setParent(None) # remove from the layout
        del self._spectra[i]
        del self._controls[i]
        self.sigSpectrumRemoved.emit(s)

    def addConstantSpectrum(self):
        s = ConstantSpectrum(energy=self._energy)
        s.constant.max = self._intensityMax
        self.addSpectrum(s)
    
    def _addPeakSpectrum(self, s):
        s.amplitude.max = self._intensityMax
        s.center.max = self._energyMax
        s.center.min = self._energyMin
        s.fwhm.value = s.fwhm.min = (self._energyMax - self._energyMin)/80.
        s.fwhm.max = self._energyMax - self._energyMin
        self.addSpectrum(s)
        
    def addGaussianSpectrum(self):
        s = GaussianSpectrum(energy=self._energy)
        self._addPeakSpectrum(s)
        
    def addLorentzianSpectrum(self):
        s = LorentzianSpectrum(energy=self._energy)
        self._addPeakSpectrum(s)
        
    def addAsymmetricGaussianSpectrum(self):
        s = AsymmetricGaussianSpectrum(energy=self._energy)
        s.amplitude.max = self._intensityMax
        s.center.max = self._energyMax
        s.center.min = self._energyMin
        s.hwhm1.value = s.hwhm1.min = (self._energyMax - self._energyMin)/40.
        s.hwhm2.value = s.hwhm2.min = (self._energyMax - self._energyMin)/40.
        s.hwhm1.max = (self._energyMax - self._energyMin) / 2.
        s.hwhm2.max = (self._energyMax - self._energyMin) / 2.
        self.addSpectrum(s)
    
    def _addPLSpectrum(self, s):
        s.amplitude.max = s.amplitude.value = self._intensityMax
        s.bandgap.max = self._energyMax
        s.bandgap.min = self._energyMin
        s.temperature.min = 0
        s.temperature.max = 300
        s.temperature.value = 293
        self.addSpectrum(s)
        
    def addWaveVectorConservingPLSpectrum(self):
        s = WaveVectorConservingPLSpectrum(energy=self._energy)
        self._addPLSpectrum(s)
        
    def addWaveVectorNonConservingPLSpectrum(self):
        s = WaveVectorNonConservingPLSpectrum(energy=self._energy)
        self._addPLSpectrum(s)
    
#    def autoFit(self, spectrum):
#        exp_y = spectrum.intensity
#        parameters = []
#        for c, s in zip(self._controls, self._spectra):
#            for autoFitCheckBox, parameter in zip(c.lockFitCheckBoxes,
#                                                  s.parameters):
#                if not autoFitCheckBox.isChecked():
#                    parameters.extend(s.parameters)
#        guess = [p.value for p in parameters]
#        print 'guess', guess
#        bounds = [(p.min, p.max) for p in parameters]
#        print 'bounds', bounds
#        #TODO: figure out how to make this work faster. i need to write a
#        # function that doesn't depend on the event loop.
#        def f(x):
#            for v, p in zip(x, parameters):
#                p.value = v
#            QtGui.QApplication.instance().processEvents(
#                                                QtCore.QEventLoop.AllEvents)
#            sim_y = self.summedSpectrum.intensity
#            return exp_y - sim_y
#        from scipy.optimize import leastsq
#        result = leastsq(f, guess, full_output=True)
#        x, cov_x, infodict, mesg, ier = result
#        print 'x =', x
#        print 'cov_x =', cov_x
#        print 'infodict =', infodict
#        print 'mesg =', mesg
#        print 'ier =', ier
#        #TODO: save the guesses, and allow undo
    
    def autoFit(self, spectrum):
        '''
        Autofits the sum of the simulated spectra to the measured
        spectrum. Puts the resulting chi squared and the fitting parameters
        in the clipboard.
        '''
        if not self._spectra:
            return # autoFit does nothing if there are not spectra
        
        x = spectrum.energy
        y = spectrum.intensity
        pvalues = [] # initial parameter values (both locked and unlocked)
        p0 = [] # initial guess (unlocked parameter values)
        unlocked_parameters = [] # the unlocked parameter objects
        lock_mask = []
        funcs = []
        pcounts = []
        for spectrum, control in zip(self._spectra, self._controls):
            funcs.append(spectrum.function)
            pcounts.append(len(spectrum.parameters))
            for p, lock in zip(spectrum.parameters,
                               control.lockFitCheckBoxes):
                pvalues.append(p.value)
                if lock.isChecked():
                    lock_mask.append(True)
                else:
                    p0.append(p.value)
                    unlocked_parameters.append(p)
                    lock_mask.append(False)
        
        if not p0:
            return # autoFit does nothing if there are no unlocked parameters
        
        # create a function that sums up the spectrum functions
        def sum_funcs(x, *args):
            result = None
            i = 0 # current parameter index
            j = 0 # current args index
            for func, pcount in zip(funcs, pcounts):
                func_args = []
                for k in xrange(pcount):
                    if lock_mask[i]:
                        func_args.append(pvalues[i])
                    else:
                        func_args.append(args[j])
                        j += 1
                    i += 1
                if result is None:
                    result = func(x, *func_args)
                else:
                    result += func(x, *func_args)
            return result
        
        print 'p0 = ', p0
        from scipy.optimize import curve_fit
        popt, pcov = curve_fit(sum_funcs, x, y, p0)
        #TODO: make sigma user adjustable
        sigma = 6e-7 # estimated from a scan with laser blocked, using 300 ms time constnat
        chi = (y - sum_funcs(x, *popt)) / sigma
        chi2 = (chi ** 2).sum()
        dof = len(x) - len(popt)
        factor = (chi2 / dof)
        pcov_sigma = pcov / factor
        stddevs = np.sqrt(np.diagonal(pcov_sigma))
        print 'popt =', popt
        print 'stddevs =', stddevs
        for p in self.getFitParameters():
            p.stddev = np.nan
        for value, stddev, p in zip(popt, stddevs, unlocked_parameters):
            p.value = value
            p.stddev = stddev
        self._chi2 = chi2
        #TODO: save the guesses, and allow undo
    
    def getPeakIntegral(self):
        integral = 0.
        for spectrum in self._spectra:
            integral += spectrum.getIntegral()
        return integral
    
    def getFitChi2(self):
        '''Returns the fitting chi^2 value'''
        return self._chi2
    
    def getFitParameters(self):
        '''Returns the fitting parameter objects'''
        parameters = []
        for spectrum in self._spectra:
            for parameter in spectrum.parameters:
                parameters.append(parameter)
        return parameters
    
    def getFitValues(self):
        '''
        Returns the fitting parameter values in a list
        '''
        values = []
        for parameter in self.getFitParameters():
            values.append(parameter.value)
        return values
    
    def getFitStddevs(self):
        '''
        Returns the fitting parameter stddevs in a list
        '''
        stddevs = []
        for parameter in self.getFitParameters():
            stddevs.append(parameter.stddev)
        return stddevs
    
    def setFitValues(self, values):
        '''
        Sets the fitting parameter values. Changes the min/max if necessary.
        
        If there are twice as many values as parameters, it is assumed that
        the values are paired with stddev's (which will be ignored).
        '''
        parameters = self.getFitParameters()
        if len(values) == len(parameters):
            vals = values
        elif len(values) == 2 * len(parameters):
            vals = values[::2]
        else:
            raise ValueError('The number of values must match the number of'
                             ' parameters')
        for parameter, value in zip(parameters, vals):
            if value > parameter.max:
                parameter.max = value
            if value < parameter.min:
                parameter.min = value
            parameter.value = value
    
    def saveParameters(self, filepath):
        with open(filepath, '') as f:
            for s, c in zip(self._spectra, self._controls):
                f.write(c.label.text())
                for p in s.parameters:
                    f.write('\t%E'%p.value)
                f.write('\n')

if __name__ == '__main__':
    from simulated_spectrum import (ConstantSpectrum, GaussianSpectrum,
                                    LorentzianSpectrum)
    import numpy as np
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    cw = QtGui.QPushButton()
    win.setCentralWidget(cw)
    dw = QtGui.QDockWidget()
    dw.setWidget(SpectraControlWidget())
    win.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw)
    win.show()
    win.raise_()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()