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
from .measured_spectrum import MeasuredSpectrum
from .expanding_spectrum import ExpandingSpectrum
from .instruments.spectrometer import Spectrometer
from .instruments.lockin import Lockin
from .dialogs.start_scan_dialog import StartScanDialog
from .dialogs.diverters_config_dialog import DivertersConfigDialog
from .dialogs.lockin_config_dialog import LockinConfigDialog
from .dialogs.gratings_and_filters_config_dialog import (
                                            GratingsAndFiltersConfigDialog)
from .dialogs.set_wavelength_dialog import SetWavelengthDialog
from .dialogs.ports_config_dialog import PortsConfigDialog


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Internal flags
        self._scanSaved = True

        # Initialize QSettings object
        self._settings = QtCore.QSettings()

        # Initialize GUI stuff
        self.spectrum = None
        self.initUI()

        # Diable all actions except for configuring the ports,
        # until the instruments are initialized
        self._spectrometerInitilized = False
        self._lockinInitilized = False
        self._isScanning = False
        self.updateActions()

        # Initialize the instruments
        self.initSpectrometer()
        self.initLockin()

        # Initialize the current instrument values
        sysResPath = self._settings.value('sysResPath', '')
        self._sysresParser = SimplePLParser(None, sysResPath)
        self._grating = None
        self._filter = None
        self._wavelength = None
        self._signal = None
        self._rawSignal = None
        self._phase = None
        self._wavelengthTarget = None

    def initSpectrometer(self):
        self.spectrometer = Spectrometer()
        self.spectrometer.sigException.connect(self.spectrometerException)
        self.spectrometer.sigInitialized.connect(self.spectrometerInitialized)
        self.spectrometer.sigChangingGrating.connect(self.changingGrating)
        self.spectrometer.sigChangingFilter.connect(self.changingFilter)
        self.spectrometer.sigChangingWavelength.connect(
                                                    self.changingWavelength)
        self.spectrometer.sigGrating.connect(self.updateGrating)
        self.spectrometer.sigFilter.connect(self.updateFilter)
        self.spectrometer.sigWavelength.connect(self.updateWavelength)
        self.spectrometer.thread.start()

    def initLockin(self):
        self.lockin = Lockin()
        self.lockin.sigException.connect(self.lockinException)
        self.lockin.sigInitialized.connect(self.lockinInitialized)
        self.lockin.sigRawSignal.connect(self.updateRawSignal)
        self.lockin.sigPhase.connect(self.updatePhase)
        self.lockin.thread.start()

    @QtCore.Slot(Exception)
    def spectrometerException(self, e):
        raise e

    @QtCore.Slot(Exception)
    def lockinException(self, e):
        raise e

    @QtCore.Slot()
    def spectrometerInitialized(self):
        self._spectrometerInitilized = True
        self.updateActions()

    @QtCore.Slot()
    def lockinInitialized(self):
        self._lockinInitilized = True
        self.updateActions()

    @QtCore.Slot()
    def changingGrating(self):
        self.gratingLabel.setText('Grating=?')
        self.wavelengthLabel.setText('Wavelength=?')

    @QtCore.Slot()
    def changingFilter(self):
        self.filterLabel.setText('Filter=?')

    @QtCore.Slot()
    def changingWavelength(self):
        self.wavelengthLabel.setText('Wavelength=?')

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
        sysres = self._sysresParser.getSysRes(self._wavelength)
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

        self.saveAsAction = QtGui.QAction('&Save As', self)
        self.saveAsAction.setStatusTip('Save the current spectrum')
        self.saveAsAction.setToolTip('Save the current spectrum')
        self.saveAsAction.setShortcut('Ctrl+Shift+S')
        self.saveAsAction.triggered.connect(self.saveAsFile)

        self.closeAction = QtGui.QAction('Close &Window', self)
        self.closeAction.setStatusTip('Close the Window')
        self.closeAction.setToolTip('Close the Window')
        self.closeAction.setShortcut('Ctrl+W')
        self.closeAction.triggered.connect(self.close)

        self.viewWavelengthAction = QtGui.QAction('&Wavelength', self)
        self.viewWavelengthAction.setStatusTip('Plot against Wavelength')
        self.viewWavelengthAction.setToolTip('Plot against Wavelength')
        self.viewWavelengthAction.setShortcut('Ctrl+Shift+W')
        self.viewWavelengthAction.triggered.connect(self.viewWavelength)
        self.viewWavelengthAction.setCheckable(True)
        self.viewWavelengthAction.setChecked(True)

        self.viewEnergyAction = QtGui.QAction('&Energy', self)
        self.viewEnergyAction.setStatusTip('Plot against Energy')
        self.viewEnergyAction.setToolTip('Plot against Energy')
        self.viewEnergyAction.setShortcut('Ctrl+Shift+e')
        self.viewEnergyAction.triggered.connect(self.viewEnergy)
        self.viewEnergyAction.setCheckable(True)

        group = QtGui.QActionGroup(self)
        group.addAction(self.viewWavelengthAction)
        group.addAction(self.viewEnergyAction)

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

        self.configPortsAction = QtGui.QAction('&Ports', self)
        self.configPortsAction.setStatusTip('Configure the instrument ports')
        self.configPortsAction.setToolTip('Configure the instrument ports')
        self.configPortsAction.triggered.connect(self.configPorts)

        self.configSysResAction = QtGui.QAction('System &Response', self)
        self.configSysResAction.setStatusTip('Configure the system response')
        self.configSysResAction.setToolTip('Configure the system response')
        self.configSysResAction.triggered.connect(self.configSysRes)

        self.configLockinAction = QtGui.QAction('&Lock-in', self)
        self.configLockinAction.setStatusTip(
                                            'Configure the lock-in amplifier')
        self.configLockinAction.setToolTip(
                                            'Configure the lock-in amplifier')
        self.configLockinAction.triggered.connect(
                                                    self.configLockin)

        self.configDivertersAction = QtGui.QAction('&Diverters', self)
        self.configDivertersAction.setStatusTip(
                                                'Configure the diverters')
        self.configDivertersAction.setToolTip('Configure the diverters')
        self.configDivertersAction.triggered.connect(
                                                    self.configDiverters)

        self.configGratingsAndFiltersAction = QtGui.QAction(
                                                    '&Gratings and Filters',
                                                    self)
        self.configGratingsAndFiltersAction.setStatusTip(
                                        'Configure the gratings and filters')
        self.configGratingsAndFiltersAction.setToolTip(
                                        'Configure the gratings and filters')
        self.configGratingsAndFiltersAction.triggered.connect(
                                        self.configGratingsAndFilters)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.closeAction)
        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(self.viewWavelengthAction)
        viewMenu.addAction(self.viewEnergyAction)
        scanMenu = menubar.addMenu('&Scan')
        scanMenu.addAction(self.gotoWavelengthAction)
        scanMenu.addAction(self.startScanAction)
        scanMenu.addAction(self.abortScanAction)
        configMenu = menubar.addMenu('&Config')
        configMenu.addAction(self.configPortsAction)
        configMenu.addAction(self.configSysResAction)
        configMenu.addAction(self.configLockinAction)
        configMenu.addAction(self.configDivertersAction)
        configMenu.addAction(self.configGratingsAndFiltersAction)
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
        self.setMinimumSize(576, 432)
        self.readWindowSettings()

    def viewWavelength(self):
        self.plot.setXAxisView('wavelength')

    def viewEnergy(self):
        self.plot.setXAxisView('energy')

    def setWavelength(self):
        wavelength = SetWavelengthDialog.getWavelength(
                                        spectrometer=self.spectrometer,
                                        wavelength=self._wavelength,
                                        parent=self)
        if wavelength is None:
            return
        self._wavelengthTarget = wavelength
        self.spectrometer.setWavelength(self._wavelengthTarget)

    def updateActions(self):
        spec = self._spectrometerInitilized
        lockin = self._lockinInitilized
        both = spec and lockin
        scanning = self._isScanning
        notScanning = not scanning
        all = both and notScanning
        self.openAction.setEnabled(notScanning)
        self.saveAction.setEnabled(not self._scanSaved and notScanning)
        self.saveAsAction.setEnabled(notScanning and self.spectrum is not None)
        self.gotoWavelengthAction.setEnabled(spec)
        self.startScanAction.setEnabled(all)
        self.abortScanAction.setEnabled(scanning)
        self.configPortsAction.setEnabled(notScanning)
        self.configSysResAction.setEnabled(notScanning)
        self.configLockinAction.setEnabled(lockin and notScanning)
        self.configDivertersAction.setEnabled(spec and notScanning)
        self.configGratingsAndFiltersAction.setEnabled(spec and notScanning)

    @QtCore.Slot(float)
    def _scanPart1(self, wavelength):
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
        self.applyDivertersConfig()
        self.applyLockinConfig()

        # Get the scan parameters
        params = StartScanDialog.getScanParameters(
                                        spectrometer=self.spectrometer,
                                        parent=self)
        if params is None:
            return

        start, _stop, _step, _delay = params

        self.updateActions()
        self.abortScanAction.setEnabled(True)

        if self.spectrum:
            self.plot.removeSpectrum(self.spectrum)
        self.spectrum = ExpandingSpectrum(self._sysresParser)
        self.plot.addSpectrum(self.spectrum)
        self.spectrometer.sigWavelength.connect(self._scanPart1)
        self.lockin.sigAdjustAndGetOutputsFinished.connect(self._scanPart2)
        self._isScanning = True

        self._wavelengthTarget = start
        self.spectrometer.setWavelength(self._wavelengthTarget)

    def abortScan(self):
        if not self._isScanning:
            self.updateActions()
            return
        self._isScanning = False
        self.spectrometer.sigWavelength.disconnect(
                                            self._scanPart1)
        self.lockin.sigAdjustAndGetOutputsFinished.disconnect(
                                            self._scanPart2)
        self.updateActions()

    def configDiverters(self):
        # Get the config parameters
        entranceMirror, exitMirror, accepted = (
                DivertersConfigDialog.getDivertersConfig(parent=self))
        if not accepted:
            return

        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def configPorts(self):
        # Get the ports
        ports = PortsConfigDialog.getPortsConfig(parent=self)
        if ports is None:
            return

        # Restart the lockin and spectrometer
        self.lockin.thread.quit()
        self.spectrometer.thread.quit()

        self.lockin.thread.wait()
        self.spectrometer.thread.wait()

        self.updateActions()
        self.configPortsAction.setEnabled(True)
        self.initSpectrometer()
        self.initLockin()

    def configSysRes(self):
        sysResPath = self._settings.value('sysResPath', None)
        sysResPath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a system response file',
                                dir=sysResPath)
        if not sysResPath:
            return
        sysResPath = self._settings.value('sysResPath', None)
        self._sysresParser = SimplePLParser(None, sysResPath)

    def configLockin(self):
        # Get the config parameters
        timeConstantIndex, reserveModeIndex, inputLineFilterIndex, accepted = (
                LockinConfigDialog.getLockinConfig(self.lockin, parent=self))
        if not accepted:
            return
        self.lockin.setTimeConstantIndex(timeConstantIndex)
        self.lockin.setReserveModeIndex(reserveModeIndex)
        self.lockin.setInputLineFilterIndex(inputLineFilterIndex)

    def configGratingsAndFilters(self):
        GratingsAndFiltersConfigDialog.getAdvancedConfig(self.spectrometer, parent=self)

    def applyDivertersConfig(self):
        entranceMirror = self._settings.value('spectrometer/entrance_mirror',
                                        'Front')
        exitMirror = self._settings.value('spectrometer/exit_mirror',
                                    'Side')
        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def applyLockinConfig(self):
        timeConstantIndex = self._settings.value('lockin/time_constant_index',
                                           9)  # 300 ms default
        reserveModeIndex = self._settings.value('lockin/reserve_mode_index',
                                          0)  # High reserve default
        inputLineFilterIndex = self._settings.value('lockin/input_line_filter_index',
                                              3)  # both filters default
        self.lockin.setTimeConstantIndex(timeConstantIndex)
        self.lockin.setReserveModeIndex(reserveModeIndex)
        self.lockin.setInputLineFilterIndex(inputLineFilterIndex)

    def openFile(self):
        dirpath = self._settings.value('last_directory', '')
        filepath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a PL spectrum file',
                                dir=dirpath)
        if not filepath:
            return
        dirpath, filename = os.path.split(filepath)
        self._settings.setValue('last_directory', dirpath)
        self.setWindowTitle(u'SimplePL - {}'.format(filename))
        spectrum = MeasuredSpectrum.open(filepath)
        # Check if the system response removed is included.
        # If not, ask user to select a system response file.
        if not len(spectrum.getSignal()):
            sysres_filepath, _filter = QtGui.QFileDialog.getOpenFileName(
                                        parent=self,
                                        caption='Open a system response file')
            if not sysres_filepath:
                return
            spectrum = MeasuredSpectrum.open(filepath, sysres_filepath)

        # remove the previous measured spectrum
        if self.spectrum:
            self.plot.removeSpectrum(self.spectrum)

        # plot the measured spectrum
        self.plot.addSpectrum(spectrum)
        self.spectrum = spectrum
        self.updateActions()

    def savePrompt(self):
        reply = QtGui.QMessageBox.question(self, 'Save?',
                'Do you want to save the current scan?',
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.saveFile()

    def saveFile(self):
        dirpath = self._settings.value('last_directory', '')
        filepath, _filter = QtGui.QFileDialog.getSaveFileName(parent=self,
                                caption='Save the current spectrum',
                                dir=dirpath,
                                filter='Tab Delimited Text (*.txt)')
        if not filepath:
            return
        dirpath, _filename = os.path.split(filepath)
        self._settings.setValue('last_directory', dirpath)
        self.spectrum.save(filepath)
        self._scanSaved = True

    def saveAsFile(self):
        self.saveFile()

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
            self.spectrometer.thread.quit()
            self.lockin.thread.quit()
            self.spectrometer.thread.wait()
            self.lockin.thread.wait()
            self.writeWindowSettings()
            event.accept()
        else:
            event.ignore()

    def writeWindowSettings(self):
        self._settings.setValue("MainWindow/size", self.size())
        self._settings.setValue("MainWindow/pos", self.pos())

    def readWindowSettings(self):
        self.resize(self._settings.value("MainWindow/size",
                                         QtCore.QSize(1280, 800)))
        pos = self._settings.value("MainWindow/pos")
        if pos is None:
            self.moveCenter()  # default to centered
        else:
            self.move(pos)
