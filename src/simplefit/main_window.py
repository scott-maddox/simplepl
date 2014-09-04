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
import os.path

# third party imports
from PySide import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

# local imports
from spectra_plot_item import SpectraPlotItem
from measured_spectrum import openMeasuredSpectrum
from spectra_control_widget import SpectraControlWidget

#TODO:
############################################################################
# File # Simulate # Fit #
############################################################################
#    Min    Value    Max   #
# | 0.   || 1.   || 1.   | #
############################
# Constant            X  | #
# ------o------------ Lk | #
# ______________________ | #
# Gaussian            X  | #
# A ----------o------ Lk | #
# C ---------o------- Lk | #
# W ----o------------ Lk ^ #
# ______________________ U #
# Gaussian            X  U #
# A ----------o------ Lk V #
# C ---------o------- Lk | #
# W ----o------------ Lk | #
# ______________________ | #
# |     Add Constant   | | #
# ______________________ | #
# |     Add Gaussian   | | #
# ______________________ | #
# |    Add Lorentzian  | | #
# ______________________ | #
############################

# Simulate options:
## Add Constant
## Add Gaussian
## Add Lorentzian

# Fit options:
## (whatever the various fitting algorithms are)

# The left panel should be dockable.
# Even better would be to have icons instead of the A, C, and W labels


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.spectrum = None

    def initUI(self):
        self.setWindowTitle('SimpleFit')

        openAction = QtGui.QAction('&Open a spectrum', self)
        openAction.setStatusTip('Open a spectrum')
        openAction.setToolTip('Open a spectrum')
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openFile)

        saveAction = QtGui.QAction('&Save parameters', self)
        saveAction.setStatusTip('Save parameters')
        saveAction.setToolTip('Save parameters')
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveFile)

        aboutAction = QtGui.QAction('&About', self)
        aboutAction.triggered.connect(self.about)

        autoFitAction = QtGui.QAction('Auto&fit', self)
        autoFitAction.setStatusTip('Autofit the spectrum')
        autoFitAction.setToolTip('Autofit the spectrum')
        autoFitAction.setShortcut('Ctrl+F')
        autoFitAction.triggered.connect(self.autoFit)

        copyNumericIntegralAction = QtGui.QAction('Copy &numeric integral', self)
        copyNumericIntegralAction.setStatusTip('Integrate numerically and copy the result')
        copyNumericIntegralAction.setToolTip('Integrate numerically and copy the result')
        copyNumericIntegralAction.setShortcut('Ctrl+N')
        copyNumericIntegralAction.triggered.connect(self.copyNumericIntegral)

        copyPeakIntegralAction = QtGui.QAction('Copy fit &integral', self)
        copyPeakIntegralAction.setStatusTip('Integrate the fit peaks and copy the result')
        copyPeakIntegralAction.setToolTip('Integrate the fit peaks and copy the result')
        copyPeakIntegralAction.setShortcut('Ctrl+I')
        copyPeakIntegralAction.triggered.connect(self.copyPeakIntegral)

        copyFitChi2Action = QtGui.QAction('Copy fit chi^2', self)
        copyFitChi2Action.setStatusTip('Copy the fitting chi^2 to the clipboard')
        copyFitChi2Action.setToolTip('Copy the fitting chi^2 to the clipboard')
        copyFitChi2Action.setShortcut('Ctrl+X')
        copyFitChi2Action.triggered.connect(self.copyFitChi2)

        copyFitValuesAndStddevsAction = QtGui.QAction('&Copy fit values and stddevs', self)
        copyFitValuesAndStddevsAction.setStatusTip('Copy the fit parameter values and stddevs to the clipboard')
        copyFitValuesAndStddevsAction.setToolTip('Copy the fit parameter values and stddevs to the clipboard')
        copyFitValuesAndStddevsAction.setShortcut('Ctrl+C')
        copyFitValuesAndStddevsAction.triggered.connect(self.copyFitValuesAndStddevs)
        
        copyAllResultsAction = QtGui.QAction('Copy &all of the above', self)
        copyAllResultsAction.setStatusTip('Copy all the above values to the clipboard')
        copyAllResultsAction.setToolTip('Copy all the above values to the clipboard')
        copyAllResultsAction.setShortcut('Ctrl+A')
        copyAllResultsAction.triggered.connect(self.copyAllResults)

        copyFitValuesAction = QtGui.QAction('&Copy fit values', self)
        copyFitValuesAction.setStatusTip('Copy the fit parameter values to the clipboard')
        copyFitValuesAction.setToolTip('Copy the fit parameter values to the clipboard')
        copyFitValuesAction.triggered.connect(self.copyFitValues)

        copyFitStddevsAction = QtGui.QAction('&Copy fit stddevs', self)
        copyFitStddevsAction.setStatusTip('Copy the fit parameter stddevs to the clipboard')
        copyFitStddevsAction.setToolTip('Copy the fit parameter stddevs to the clipboard')
        copyFitStddevsAction.triggered.connect(self.copyFitStddevs)

        pasteFitValuesAction = QtGui.QAction('&Paste fit values', self)
        pasteFitValuesAction.setStatusTip('Paste the fit parameter values from the clipboard')
        pasteFitValuesAction.setToolTip('Paste the fit parameter values from the clipboard')
        pasteFitValuesAction.setShortcut('Ctrl+V')
        pasteFitValuesAction.triggered.connect(self.pasteFitValues)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        toolsMenu = menubar.addMenu('Tools')
        toolsMenu.addAction(autoFitAction)
        toolsMenu.addAction(copyNumericIntegralAction)
        toolsMenu.addAction(copyPeakIntegralAction)
        toolsMenu.addAction(copyFitChi2Action)
        toolsMenu.addAction(copyFitValuesAndStddevsAction)
        toolsMenu.addAction(copyAllResultsAction)
        toolsMenu.addAction(copyFitValuesAction)
        toolsMenu.addAction(copyFitStddevsAction)
        toolsMenu.addAction(pasteFitValuesAction)
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(aboutAction)
        
        view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(view)
        self.plot = SpectraPlotItem(xaxis='energy')
        view.addItem(self.plot, 0, 0)
        self.setCentralWidget(view)
        self.control = SpectraControlWidget()
        self.plot.addSpectrum(self.control.summedSpectrum)
        dw = QtGui.QDockWidget()
        dw.setWidget(self.control)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dw)
        self.control.sigSpectrumAdded.connect(self.plot.addSpectrum)
        self.control.sigSpectrumRemoved.connect(self.plot.removeSpectrum)
        
        self.setWindowTitle('SimpleFit')
        self.resize(1280,800)
        #self.moveCenter()
        self.moveTopLeft()

    def openFile(self):
        filepath, filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a PL spectrum file')
        if not filepath:
            return
        dirpath, filename = os.path.split(filepath)
        self.setWindowTitle(u'SimpleFit - {}'.format(filename))
        spectrum = openMeasuredSpectrum(filepath)
        # Check if the system response removed is included.
        # If not, ask user to select a system response file.
        print spectrum.intensity
        if not len(spectrum.intensity):
            sysres_filepath, filter = QtGui.QFileDialog.getOpenFileName(
                parent=self, caption='Open a system response file')
            if not sysres_filepath:
                return
            spectrum = openMeasuredSpectrum(filepath, sysres_filepath)
            
        # remove the previous measured spectrum
        if self.spectrum:
            self.plot.removeSpectrum(self.spectrum)
        
        # plot the measured spectrum
        self.plot.addSpectrum(spectrum)
        self.spectrum = spectrum
        
        # update the simulated spectrum
        self.control.setEnergy(spectrum.energy)
        self.control.setIntensity(spectrum.intensity)
    
    def saveFile(self):
        filepath, filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                                caption='Save fitting parameters to a file')
        self.control.saveParameters(filepath)
        
    def about(self):
        title = 'About SimpleFit'
        text = """
   Copyright (c) 2013, Scott J Maddox

   This file is part of SimplePL.

   SimplePL is free software: you can redistribute it and/or modify
   it under the terms of the GNU Affero General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

   SimplePL is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Affero General Public License for more details.

   You should have received a copy of the GNU Affero General Public
   License along with semicontrol.  If not, see
   <http://www.gnu.org/licenses/>.
        """
        QtGui.QMessageBox.about(self, title, text)
    
    def autoFit(self):
        if self.spectrum is None:
            return # do nothing if no measured spectrum
        self.control.autoFit(self.spectrum)
    
    def getNumericIntegral(self):
        if self.spectrum is None:
            return # do nothing if no measured spectrum
        x = self.spectrum.energy[::-1]
        y = self.spectrum.intensity[::-1]
        from scipy.integrate import cumtrapz
        return cumtrapz(y, x).max()
    
    def copyNumericIntegral(self):
        integral = self.getNumericIntegral()
        print 'numeric integral = %E'%integral
        QtGui.QApplication.clipboard().setText('%E'%integral)
    
    def copyPeakIntegral(self):
        integral = self.control.getPeakIntegral()
        print 'peak integral = %E'%integral
        QtGui.QApplication.clipboard().setText('%E'%integral)
    
    def copyFitChi2(self):
        chi2 = self.control.getFitChi2()
        print 'fitting chi2 = %E'%chi2
        QtGui.QApplication.clipboard().setText('%E'%chi2)
    
    def copyFitValuesAndStddevs(self):
        values = self.control.getFitValues()
        stddevs = self.control.getFitStddevs()
        s = []
        for value, stddev in zip(values, stddevs):
            s.append('%E'%value)
            s.append('%E'%stddev)
        result = '\t'.join(s)
        print 'copying fit values and stddevs:', result
        QtGui.QApplication.clipboard().setText(result)
    
    def copyAllResults(self):
        vals = []
        vals.append(self.getNumericIntegral())
        vals.append(self.control.getPeakIntegral())
        vals.append(self.control.getFitChi2())
        values = self.control.getFitValues()
        stddevs = self.control.getFitStddevs()
        for value, stddev in zip(values, stddevs):
            vals.append(value)
            vals.append(stddev)
        s = []
        for val in vals:
            s.append('%E'%val)
        result = '\t'.join(s)
        print 'copying all results:', result
        QtGui.QApplication.clipboard().setText(result)
    
    def copyFitValues(self):
        values = self.control.getFitValues()
        s = []
        for value in values:
            s.append('%E'%value)
        result = '\t'.join(s)
        print 'copying fit values:', result
        QtGui.QApplication.clipboard().setText(result)
    
    def copyFitStddevs(self):
        stddevs = self.control.getFitStddevs()
        s = []
        for stddev in stddevs:
            s.append('%E'%stddev)
        result = '\t'.join(s)
        print 'copying fit stddevs:', result
        QtGui.QApplication.clipboard().setText(result)
    
    def pasteFitValues(self):
        '''
        Pastes the fitting parameter values from the clipboard.
        
        If there are twice as many values as parameters, it is assumed that
        the values are paired with stddev's (which will be ignored).
        '''
        s = QtGui.QApplication.clipboard().text()
        vals = []
        for sval in s.split('\t'):
            if not sval:
                vals.append(np.nan)
            else:
                vals.append(float(sval))
        print 'setting parameters:', vals
        self.control.setFitValues(vals)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def moveTopLeft(self):
        qr = self.frameGeometry()
        p = QtGui.QDesktopWidget().availableGeometry().topLeft()
        self.move(p)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit?',
                'Are you sure you want to quit?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
            return
        else:
            event.ignore()
            return
        #TODO do something if data is unsaved?