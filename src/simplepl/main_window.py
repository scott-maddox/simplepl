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
#   License along with SimplePL.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# std lib imports
import os.path

# third party imports
from PySide import QtGui, QtCore
import pyqtgraph as pg

# local imports
from .simple_pl_parser import SimplePLParser
from .spectra_plot_item import SpectraPlotItem
from .measured_spectrum import openMeasuredSpectrum
from .expanding_spectrum import ExpandingSpectrum
from .instruments.spectrometer import Spectrometer
from .instruments.lockin import Lockin
from .start_scan_dialog import StartScanDialog
from .spectrometer_config_dialog import SpectrometerConfigDialog
from .lockin_config_dialog import LockinConfigDialog


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Internal flags
        self._scanSaved = True

        # Initialize QSettings object
        self._settings = QtCore.QSettings()

        # Initialize instruments
        self.spectrometer = Spectrometer()
        self.lockin = Lockin()
        self.spectrometer.sigChangingGrating.connect(self.changingGrating)
        self.spectrometer.sigChangingFilter.connect(self.changingFilter)
        self.spectrometer.sigGrating.connect(self.updateGrating)
        self.spectrometer.sigFilter.connect(self.updateFilter)
        self.spectrometer.sigWavelength.connect(self.updateWavelength)
        self.lockin.sigRawSignal.connect(self.updateRawSignal)
        self.lockin.sigPhase.connect(self.updatePhase)
        self.spectrometer.getGrating()
        self.spectrometer.getFilter()
        self.spectrometer.getWavelength()

        # Initialize the current instrument values
        self._isScanning = False
        self._sysresParser = SimplePLParser(None,
                '2014-05-01 sysres - InSb detector - 2.5 mm slits - N2.txt')
        self._grating = None
        self._filter = None
        self._wavelength = None
        self._signal = None
        self._rawSignal = None
        self._phase = None
        self._wavelengthTarget = None

        # Initialize GUI stuff
        self.spectrum = None
        self.initUI()

    @QtCore.Slot()
    def changingGrating(self):
        self.gratingLabel.setText('Grating=?')
        self.wavelengthLabel.setText('Wavelength=?')

    @QtCore.Slot()
    def changingFilter(self):
        self.filterLabel.setText('Filter=?')

    @QtCore.Slot(float)
    def updateGrating(self, grating):
        self._grating = grating
        try:
            s = 'Grating=%d' % grating
        except:
            s = 'Grating=?'
        self.gratingLabel.setText(s)

    @QtCore.Slot(float)
    def updateFilter(self, filt):
        self._filter = filt
        try:
            s = 'Filter=%d' % filt
        except:
            s = 'Filter=?'
        self.filterLabel.setText(s)

    @QtCore.Slot(float)
    def updateWavelength(self, wavelength):
        self._wavelength = wavelength
        try:
            s = 'Wavelength=%.1f' % wavelength
        except:
            s = 'Wavelength=?'
        self.wavelengthLabel.setText(s)

    @QtCore.Slot(float)
    def updateRawSignal(self, rawSignal):
        self._rawSignal = rawSignal
        try:
            s = 'Raw Signal=%.3E' % rawSignal
        except:
            s = 'Raw Signal=?'
        self.rawSignalLabel.setText(s)

        # Calculate the signal by dividing by the system response,
        # and update that too
        sysres = self._sysresParser.get_sysres(self._wavelength)
        self.updateSignal(rawSignal / sysres)

    @QtCore.Slot(float)
    def updateSignal(self, signal):
        self._signal = signal
        try:
            s = 'Signal=%.3E' % signal
        except:
            s = 'Signal=?'
        self.signalLabel.setText(s)

    @QtCore.Slot(float)
    def updatePhase(self, phase):
        self._phase = phase
        try:
            s = 'Phase=%.1f' % phase
        except:
            s = 'Phase=?'
        self.phaseLabel.setText(s)

    def initUI(self):
        self.setWindowTitle('SimplePL')

        self.aboutAction = QtGui.QAction('&About', self)
        self.aboutAction.triggered.connect(self.about)

        self.openAction = QtGui.QAction('&Open', self)
        self.openAction.setStatusTip('Open a spectrum')
        self.openAction.setToolTip('Open a spectrum')
        self.openAction.setShortcut('Ctrl+O')
        self.openAction.triggered.connect(self.openFile)

        self.saveAction = QtGui.QAction('&Save', self)
        self.saveAction.setStatusTip('Save the current spectrum')
        self.saveAction.setToolTip('Save the current spectrum')
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.triggered.connect(self.saveFile)

        self.closeAction = QtGui.QAction('Close &Window', self)
        self.closeAction.setStatusTip('Close the Window')
        self.closeAction.setToolTip('Close the Window')
        self.closeAction.setShortcut('Ctrl+W')
        self.closeAction.triggered.connect(self.close)

        self.gotoWavelengthAction = QtGui.QAction('&Go to wavelength', self)
        self.gotoWavelengthAction.setStatusTip('Go to a wavelength')
        self.gotoWavelengthAction.setToolTip('Go to a wavelength')
        self.gotoWavelengthAction.setShortcut('Ctrl+G')
        self.gotoWavelengthAction.triggered.connect(self.setWavelength)

        self.startScanAction = QtGui.QAction('S&tart Scan', self)
        self.startScanAction.setStatusTip('Start a scan')
        self.startScanAction.setToolTip('Start a scan')
        self.startScanAction.setShortcut('Ctrl+T')
        self.startScanAction.triggered.connect(self.startScan)

        self.abortScanAction = QtGui.QAction('A&bort Scan', self)
        self.abortScanAction.setStatusTip('Abort the current scan')
        self.abortScanAction.setToolTip('Abort the current scan')
        self.abortScanAction.setShortcut('Ctrl+B')
        self.abortScanAction.triggered.connect(self.abortScan)
        self.abortScanAction.setEnabled(False)

        self.configSpectrometerAction = QtGui.QAction('&Spectrometer', self)
        self.configSpectrometerAction.setStatusTip(
                                                'Configure the spectrometer')
        self.configSpectrometerAction.setToolTip('Configure the spectrometer')
        self.configSpectrometerAction.triggered.connect(
                                                    self.configSpectrometer)

        self.configLockinAction = QtGui.QAction('&Lockin', self)
        self.configLockinAction.setStatusTip(
                                            'Configure the lock-in amplifier')
        self.configLockinAction.setToolTip(
                                            'Configure the lock-in amplifier')
        self.configLockinAction.triggered.connect(
                                                    self.configLockin)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.closeAction)
        scanMenu = menubar.addMenu('&Scan')
        scanMenu.addAction(self.gotoWavelengthAction)
        scanMenu.addAction(self.startScanAction)
        scanMenu.addAction(self.abortScanAction)
        configMenu = menubar.addMenu('&Config')
        configMenu.addAction(self.configSpectrometerAction)
        configMenu.addAction(self.configLockinAction)
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(self.aboutAction)

        statusBar = self.statusBar()
        self.gratingLabel = QtGui.QLabel('Grating=?')
        self.filterLabel = QtGui.QLabel('Filter=?')
        self.wavelengthLabel = QtGui.QLabel('Wavelength=?')
        self.signalLabel = QtGui.QLabel('Signal=?')
        self.rawSignalLabel = QtGui.QLabel('Raw Signal=?')
        self.phaseLabel = QtGui.QLabel('Phase=?')
        statusBar.addWidget(self.gratingLabel, stretch=1)
        statusBar.addWidget(self.filterLabel, stretch=1)
        statusBar.addWidget(self.wavelengthLabel, stretch=1)
        statusBar.addWidget(self.signalLabel, stretch=1)
        statusBar.addWidget(self.rawSignalLabel, stretch=1)
        statusBar.addWidget(self.phaseLabel, stretch=1)

        view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(view)
        self.plot = SpectraPlotItem(xaxis='wavelength')
        view.addItem(self.plot, 0, 0)
        self.setCentralWidget(view)

        self.setWindowTitle('SimplePL')
        self.resize(1280, 800)
        self.moveTopLeft()

    def setWavelength(self):
        wavelengthMin = float(self._settings.value('wavelength/min', 800.))
        wavelengthMax = float(self._settings.value('wavelength/max', 5500.))
        wavelength = self._wavelength or wavelengthMin
        wavelengthPrecision = float(self._settings.value(
                                             'wavelength/precision', 0.1))
        target, accepted = QtGui.QInputDialog().getDouble(self,
                                            'Go to a wavelength',
                                            'Target wavelength (wavelength):',
                                            wavelength,
                                            wavelengthMin,
                                            wavelengthMax,
                                            wavelengthPrecision)
        if not accepted:
            return
        self._wavelengthTarget = target
        self.wavelengthLabel.setText('Wavelength=?')
        self.spectrometer.setWavelength(self._wavelengthTarget)

    def enableActions(self):
        self.aboutAction.setEnabled(True)
        self.openAction.setEnabled(True)
        self.saveAction.setEnabled(True)
        self.gotoWavelengthAction.setEnabled(True)
        self.startScanAction.setEnabled(True)
        self.abortScanAction.setEnabled(False)
        self.configSpectrometerAction.setEnabled(True)
        self.configLockinAction.setEnabled(True)

    def disableActions(self):
        self.aboutAction.setEnabled(False)
        self.openAction.setEnabled(False)
        self.saveAction.setEnabled(False)
        self.gotoWavelengthAction.setEnabled(False)
        self.startScanAction.setEnabled(False)
        self.abortScanAction.setEnabled(True)
        self.configSpectrometerAction.setEnabled(False)
        self.configLockinAction.setEnabled(False)

    @QtCore.Slot(float)
    def _scanPart1(self, wavelength):
        self.updateWavelength(wavelength)
        delay = float(self._settings.value('scan/delay', 0.5))
        self.lockin.adjustAndGetOutputs(delay)

    @QtCore.Slot(float, float)
    def _scanPart2(self, rawSignal, phase):
        # Update the spectrum
        self.spectrum.append(self._wavelength, rawSignal, phase)

        # Check if the scan is finished
        stop = float(self._settings.value('scan/stop', 5500.))
        step = float(self._settings.value('scan/step', 10.))
        self._wavelengthTarget += step
        if (step > 0 and self._wavelengthTarget > stop or
            step < 0 and self._wavelengthTarget < stop):
            # If it is, disconnect the signals and slots
            self.abortScan()
            return
        else:
            # If it isn't, go to the next wavelength
            self.wavelengthLabel.setText('Wavelength=?')
            self.spectrometer.setWavelength(self._wavelengthTarget)

    def startScan(self):
        if not self._scanSaved:
            self.savePrompt()  # Prompt the user to save the scan
        self._scanSaved = False

        # Apply the spectrometer and lockin config's
        self.applySpectrometerConfig()
        self.applyLockinConfig()

        # Get the scan parameters
        start, _stop, _step, _delay, accepted = (
                            StartScanDialog.getScanParameters(parent=self))
        if not accepted:
            return

        self.disableActions()

        if self.spectrum:
            self.plot.removeSpectrum(self.spectrum)
        self.spectrum = ExpandingSpectrum(self._sysresParser)
        self.plot.addSpectrum(self.spectrum)
        self.spectrometer.sigWavelength.connect(
                                            self._scanPart1)
        self.lockin.sigAdjustAndGetOutputsFinished.connect(
                                            self._scanPart2)
        self._isScanning = True

        self._wavelengthTarget = start
        self.spectrometer.setWavelength(self._wavelengthTarget)

    def abortScan(self):
        if not self._isScanning:
            self.enableActions()
            return
        self._isScanning = False
        self.spectrometer.sigWavelength.disconnect(
                                            self._scanPart1)
        self.lockin.sigAdjustAndGetOutputsFinished.disconnect(
                                            self._scanPart2)
        self.enableActions()

    def configSpectrometer(self):
        # Get the config parameters
        entranceMirror, exitMirror, accepted = (
                SpectrometerConfigDialog.getSpectrometerConfig(parent=self))
        if not accepted:
            return

        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def configLockin(self):
        # Get the config parameters
        timeConstantIndex, reserveModeIndex, inputLineFilterIndex, accepted = (
                LockinConfigDialog.getLockinConfig(self.lockin, parent=self))
        if not accepted:
            return
        self.lockin.setTimeConstantIndex(timeConstantIndex)
        self.lockin.setReserveModeIndex(reserveModeIndex)
        self.lockin.setInputLineFilterIndex(inputLineFilterIndex)

    def applySpectrometerConfig(self):
        settings = QtCore.QSettings()
        entranceMirror = settings.value('spectrometer/entrance_mirror',
                                        'Front')
        exitMirror = settings.value('spectrometer/exit_mirror',
                                    'Side')
        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def applyLockinConfig(self):
        settings = QtCore.QSettings()
        timeConstantIndex = settings.value('lockin/time_constant_index',
                                           9)  # 300 ms default
        reserveModeIndex = settings.value('lockin/reserve_mode_index',
                                          0)  # High reserve default
        inputLineFilterIndex = settings.value('lockin/input_line_filter_index',
                                              3)  # both filters default
        self.lockin.setTimeConstantIndex(timeConstantIndex)
        self.lockin.setReserveModeIndex(reserveModeIndex)
        self.lockin.setInputLineFilterIndex(inputLineFilterIndex)

    def openFile(self):
        settings = QtCore.QSettings()
        dirpath = settings.value('last_directory', '')
        filepath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a PL spectrum file',
                                dir=dirpath)
        if not filepath:
            return
        dirpath, filename = os.path.split(filepath)
        settings.setValue('last_directory', dirpath)
        self.setWindowTitle(u'SimplePL - {}'.format(filename))
        spectrum = openMeasuredSpectrum(filepath)
        # Check if the system response removed is included.
        # If not, ask user to select a system response file.
        print spectrum.intensity
        if not len(spectrum.intensity):
            sysres_filepath, _filter = QtGui.QFileDialog.getOpenFileName(
                                        parent=self,
                                        caption='Open a system response file')
            if not sysres_filepath:
                return
            spectrum = openMeasuredSpectrum(filepath, sysres_filepath)

        # remove the previous measured spectrum
        if self.spectrum:
            self.plot.removeSpectrum(self.spectrum)

        # plot the measured spectrum
        self.plot.addSpectrum(spectrum)
        self.spectrum = spectrum

    def savePrompt(self):
        reply = QtGui.QMessageBox.question(self, 'Save?',
                'Do you want to save the current scan?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.saveFile()

    def saveFile(self):
        settings = QtCore.QSettings()
        dirpath = settings.value('last_directory', '')
        filepath, _filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                                caption='Save the current spectrum',
                                dir=dirpath,
                                filter='Tab Delimited Text (*.txt)')
        if not filepath:
            return
        dirpath, _filename = os.path.split(filepath)
        settings.setValue('last_directory', dirpath)
        wavelength = self.spectrum.wavelength
        rawSignal = self.spectrum.raw
        phase = self.spectrum.phase
        signal = self.spectrum.intensity
        with open(filepath, 'w') as f:
            f.write('Wavelength\tSignal\tRaw_Signal\tPhase\n')
            for i in xrange(wavelength.size):
                f.write('%.1f\t%E\t%E\t%.1f\n' % (wavelength[i],
                                                  signal[i],
                                                  rawSignal[i],
                                                  phase[i]))
        self._scanSaved = True

    def about(self):
        title = 'About SimplePL'
        text = """
   Copyright (c) 2014, Scott J Maddox

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
   License along with SimplePL.  If not, see
   <http://www.gnu.org/licenses/>.
        """
        QtGui.QMessageBox.about(self, title, text)

    def moveCenter(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def moveTopLeft(self):
        p = QtGui.QDesktopWidget().availableGeometry().topLeft()
        self.move(p)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit?',
                'Are you sure you want to quit?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            if not self._scanSaved:
                self.abortScan()
                self.savePrompt()  # Prompt the user to save the scan
            self.spectrometer.requestQuit()
            self.lockin.requestQuit()
            self.spectrometer.thread.wait()
            self.lockin.thread.wait()
            event.accept()
        else:
            event.ignore()
