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
import os.path

# third party imports
from PySide import QtGui, QtCore
import pyqtgraph as pg

# local imports
from .scanners import Scanner, GoToer
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
from .dialogs.config_instruments_dialog import ConfigInstrumentsDialog
from .dialogs.generate_veusz_file_dialog import GenerateVeuszFileDialog
from .dialogs.about_dialog import AboutDialog


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize private variables
        self.plot = None
        self.spectrum = None
        self._grating = None
        self._filter = None
        self._wavelength = None
        self._signal = None
        self._rawSignal = None
        self._phase = None
        self.spectrometer = None
        self.lockin = None
        self.scanner = None

        # Internal flags
        self._scanSaved = True

        # Initialize QSettings object
        self._settings = QtCore.QSettings()

        # Initialize GUI stuff
        self.initUI()

        # Disable all actions except for configuring the ports,
        # until the instruments are initialized
        self._spectrometerInitilized = False
        self._lockinInitilized = False
        self.updateActions()

        # Initialize the instruments
        if bool(self._settings.value('autoConnect')):
            self.initSpectrometer()
            self.initLockin()

        # Initialize the current instrument values
        sysResPath = self._settings.value('sysResPath')
        self._sysresParser = SimplePLParser(None, sysResPath)

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

    @QtCore.Slot(Exception)
    def scannerException(self, e):
        self.scanner.wait()
        self.updateStatus('Scan failed.')
        raise e

    @QtCore.Slot()
    def spectrometerInitialized(self):
        self._spectrometerInitilized = True
        if self._spectrometerInitilized and self._lockinInitilized:
            self.updateStatus('Idle.')
        self.updateActions()

    @QtCore.Slot()
    def lockinInitialized(self):
        self._lockinInitilized = True
        if self._spectrometerInitilized and self._lockinInitilized:
            self.updateStatus('Idle.')
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

    @QtCore.Slot(str)
    def updateStatus(self, status):
        self.statusLabel.setText(status)

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
        from .resources.icons import logoIcon
        self.setWindowIcon(logoIcon)

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

        self.viewSignal = QtGui.QAction('&Signal', self)
        self.viewSignal.setStatusTip('Plot the signal with system '
                                     'response removed')
        self.viewSignal.setToolTip('Plot the signal with system '
                                   'response removed')
        self.viewSignal.toggled.connect(self.viewSignalToggled)
        self.viewSignal.setCheckable(True)
        self.viewSignal.setChecked(True)

        self.viewRawSignal = QtGui.QAction('&Raw Signal', self)
        self.viewRawSignal.setStatusTip('Plot the raw signal')
        self.viewRawSignal.setToolTip('Plot the raw signal')
        self.viewRawSignal.toggled.connect(self.viewRawSignalToggled)
        self.viewRawSignal.setCheckable(True)
        self.viewRawSignal.setChecked(False)

        self.viewPhase = QtGui.QAction('&Phase', self)
        self.viewPhase.setStatusTip('Plot the phase')
        self.viewPhase.setToolTip('Plot the phase')
        self.viewPhase.toggled.connect(self.viewPhaseToggled)
        self.viewPhase.setCheckable(True)
        self.viewPhase.setChecked(False)

        self.viewClearPlotAction = QtGui.QAction('&Clear Plot', self)
        self.viewClearPlotAction.setStatusTip('Clear the plot')
        self.viewClearPlotAction.setToolTip('Clear the plot')
        self.viewClearPlotAction.triggered.connect(self.clearPlot)

        self.axesWavelengthAction = QtGui.QAction('&Wavelength', self)
        self.axesWavelengthAction.setStatusTip('Plot against Wavelength')
        self.axesWavelengthAction.setToolTip('Plot against Wavelength')
        self.axesWavelengthAction.setShortcut('Ctrl+Shift+W')
        self.axesWavelengthAction.triggered.connect(self.axesWavelength)
        self.axesWavelengthAction.setCheckable(True)
        self.axesWavelengthAction.setChecked(True)

        self.axesEnergyAction = QtGui.QAction('&Energy', self)
        self.axesEnergyAction.setStatusTip('Plot against Energy')
        self.axesEnergyAction.setToolTip('Plot against Energy')
        self.axesEnergyAction.setShortcut('Ctrl+Shift+e')
        self.axesEnergyAction.triggered.connect(self.axesEnergy)
        self.axesEnergyAction.setCheckable(True)

        self.axesSemilogAction = QtGui.QAction('Semi-&log', self)
        self.axesSemilogAction.setStatusTip('Plot the log of the y-axis')
        self.axesSemilogAction.setToolTip('Plot the log of the y-axis')
        self.axesSemilogAction.setShortcut('Ctrl+Shift+L')
        self.axesSemilogAction.changed.connect(self.axesSemilog)
        self.axesSemilogAction.setCheckable(True)
        self.axesSemilogAction.setChecked(False)

        group = QtGui.QActionGroup(self)
        group.addAction(self.axesWavelengthAction)
        group.addAction(self.axesEnergyAction)

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

        self.configInstrumentsAction = QtGui.QAction('&Instruments', self)
        self.configInstrumentsAction.setStatusTip('Configure the instruments')
        self.configInstrumentsAction.setToolTip('Configure the instruments')
        self.configInstrumentsAction.triggered.connect(self.configInstruments)

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

        self.generateVeuszFileAction = QtGui.QAction('Generate &Veusz File',
                                                     self)
        self.generateVeuszFileAction.setStatusTip(
                                        'Generate a Veusz file')
        self.generateVeuszFileAction.setToolTip(
                                        'Generate a Veusz file')
        self.generateVeuszFileAction.triggered.connect(
                                        self.generateVeuszFile)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.closeAction)
        viewMenu = menubar.addMenu('&View')
        viewMenu.addAction(self.viewSignal)
        viewMenu.addAction(self.viewRawSignal)
        viewMenu.addAction(self.viewPhase)
        viewMenu.addSeparator().setText("Spectra")
        viewMenu.addAction(self.viewClearPlotAction)
        axesMenu = menubar.addMenu('A&xes')
        axesMenu.addSeparator().setText("X Axis")
        axesMenu.addAction(self.axesWavelengthAction)
        axesMenu.addAction(self.axesEnergyAction)
        axesMenu.addSeparator().setText("Y Axis")
        axesMenu.addAction(self.axesSemilogAction)
        self.axesSemilogAction.changed.connect(self.axesSemilog)
        scanMenu = menubar.addMenu('&Scan')
        scanMenu.addAction(self.gotoWavelengthAction)
        scanMenu.addAction(self.startScanAction)
        scanMenu.addAction(self.abortScanAction)
        configMenu = menubar.addMenu('&Config')
        configMenu.addAction(self.configInstrumentsAction)
        configMenu.addAction(self.configSysResAction)
        configMenu.addAction(self.configLockinAction)
        configMenu.addAction(self.configDivertersAction)
        configMenu.addAction(self.configGratingsAndFiltersAction)
        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(self.generateVeuszFileAction)
        aboutMenu = menubar.addMenu('&About')
        aboutMenu.addAction(self.aboutAction)

        statusBar = self.statusBar()
        self.statusLabel = QtGui.QLabel('Initializing...')
        self.gratingLabel = QtGui.QLabel('Grating=?')
        self.filterLabel = QtGui.QLabel('Filter=?')
        self.wavelengthLabel = QtGui.QLabel('Wavelength=?')
        self.signalLabel = QtGui.QLabel('Signal=?')
        self.rawSignalLabel = QtGui.QLabel('Raw Signal=?')
        self.phaseLabel = QtGui.QLabel('Phase=?')
        statusBar.addWidget(self.statusLabel, stretch=1)
        statusBar.addWidget(self.gratingLabel, stretch=1)
        statusBar.addWidget(self.filterLabel, stretch=1)
        statusBar.addWidget(self.wavelengthLabel, stretch=1)
        statusBar.addWidget(self.signalLabel, stretch=1)
        statusBar.addWidget(self.rawSignalLabel, stretch=1)
        statusBar.addWidget(self.phaseLabel, stretch=1)

        view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(view)
        self.plot = SpectraPlotItem(xaxis='wavelength')
        self.plot.setSignalEnabled(True)
        self.plot.setRawSignalEnabled(False)
        self.plot.setPhaseEnabled(False)
        view.addItem(self.plot, 0, 0)
        self.setCentralWidget(view)

        self.setWindowTitle('SimplePL')
        self.setMinimumSize(576, 432)
        self.readWindowSettings()

    @QtCore.Slot(bool)
    def viewSignalToggled(self, b):
        if self.plot:
            self.plot.setSignalEnabled(b)

    @QtCore.Slot(bool)
    def viewRawSignalToggled(self, b):
        if self.plot:
            self.plot.setRawSignalEnabled(b)

    @QtCore.Slot(bool)
    def viewPhaseToggled(self, b):
        if self.plot:
            self.plot.setPhaseEnabled(b)

    def clearPlot(self):
        self.plot.clear()

    def axesWavelength(self):
        self.plot.setXAxisView('wavelength')

    def axesEnergy(self):
        self.plot.setXAxisView('energy')

    def setWavelength(self):
        wavelength = SetWavelengthDialog.getWavelength(
                                        spectrometer=self.spectrometer,
                                        wavelength=self._wavelength,
                                        parent=self)
        if wavelength is None:
            return

        self.scanner = GoToer(self.spectrometer, wavelength)
        self.scanner.statusChanged.connect(self.updateStatus)
        self.scanner.started.connect(self.updateActions)
        self.scanner.finished.connect(self.updateActions)
        self.scanner.sigException.connect(self.scannerException)
        self.scanner.start()

    def axesSemilog(self):
        logMode = self.axesSemilogAction.isChecked()
        if self.plot:
            self.plot.setLogMode(None, logMode)

    def updateActions(self):
        spec = self._spectrometerInitilized
        lockin = self._lockinInitilized
        both = spec and lockin
        scanning = bool(self.scanner) and self.scanner.isScanning()
        notScanning = not scanning
        all = both and notScanning
        self.openAction.setEnabled(notScanning)
        self.saveAction.setEnabled(not self._scanSaved and notScanning)
        self.saveAsAction.setEnabled(notScanning and self.spectrum is not None)
        self.gotoWavelengthAction.setEnabled(spec and notScanning)
        self.startScanAction.setEnabled(all)
        self.abortScanAction.setEnabled(scanning)
        self.configInstrumentsAction.setEnabled(not both or notScanning)
        self.configSysResAction.setEnabled(notScanning)
        self.configLockinAction.setEnabled(lockin and notScanning)
        self.configDivertersAction.setEnabled(spec and notScanning)
        self.configGratingsAndFiltersAction.setEnabled(spec and notScanning)

    def startScan(self):
        if self.scanner and self.scanner.isScanning():
            return  # a scan is already running

        if not self._scanSaved:
            self.savePrompt()  # Prompt the user to save the scan
        self._scanSaved = False

        # Get the scan parameters from the user
        params = StartScanDialog.getScanParameters(
                                        spectrometer=self.spectrometer,
                                        parent=self)
        if params is None:
            return  # cancel

        start, stop, step, delay = params

        # Remove the old spectrum from the plot, and add a new one
        if self.spectrum:
            result = QtGui.QMessageBox.question(self,
                                                'Clear plot?',
                                                'Do you want to clear the '
                                                'plot?',
                                                QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                self.clearPlot()
        self.spectrum = ExpandingSpectrum(self._sysresParser)
        self.plot.addSpectrum(self.spectrum)

        self.scanner = Scanner(self.spectrometer, self.lockin, self.spectrum,
                               start, stop, step, delay)
        self.scanner.statusChanged.connect(self.updateStatus)
        self.scanner.started.connect(self.updateActions)
        self.scanner.finished.connect(self.updateActions)
        self.scanner.sigException.connect(self.scannerException)
        self.scanner.start()

    def abortScan(self):
        if not self.scanner.isScanning():
            self.updateActions()
            return
        self.updateStatus('Aborting scan...')
        self.scanner.abort()

    def configDiverters(self):
        # Get the config parameters
        entranceMirror, exitMirror, accepted = (
                DivertersConfigDialog.getDivertersConfig(parent=self))
        if not accepted:
            return

        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def configInstruments(self):
        # Get the ports
        ports = ConfigInstrumentsDialog.getConfig(parent=self)
        if ports is None:
            return

        # Reset the status
        self.updateStatus('Reinitializing...')
        self._lockinInitilized = False
        self._spectrometerInitilized = False
        self.updateActions()

        # Restart the lockin and spectrometer
        if self.lockin:
            self.lockin.thread.quit()
        if self.spectrometer:
            self.spectrometer.thread.quit()

        if self.lockin:
            self.lockin.thread.wait()
        if self.spectrometer:
            self.spectrometer.thread.wait()

        self.initSpectrometer()
        self.initLockin()

    def configSysRes(self):
        sysResPath = self._settings.value('sysResPath', None)
        sysResPath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a system response file',
                                dir=sysResPath)
        if not sysResPath:
            return
        self._settings.setValue('sysResPath', sysResPath)
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
        GratingsAndFiltersConfigDialog.getAdvancedConfig(self.spectrometer,
                                                         parent=self)

    def generateVeuszFile(self):
        GenerateVeuszFileDialog(self).exec_()

    def getSystemResponseFilePath(self):
        sysResPath = self._settings.value('sysResPath', None)
        sysResPath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a system response file',
                                dir=sysResPath)
        return sysResPath

    def openFile(self):
        dirpath = self._settings.value('last_directory', '')
        filepath, _filter = QtGui.QFileDialog.getOpenFileName(parent=self,
                                caption='Open a PL spectrum file',
                                dir=dirpath)
        if not filepath:
            return
        dirpath, filename = os.path.split(filepath)
        self._settings.setValue('last_directory', dirpath)
#         self.setWindowTitle(u'SimplePL - {}'.format(filename))
        spectrum = MeasuredSpectrum.open(filepath)
        # Check if the system response removed is included.
        # If not, ask user to select a system response file.
        if not len(spectrum.getSignal()):
            result = QtGui.QMessageBox.question(self,
                                                'Provide system response?',
                                                'The selected file does not '
                                                'appear to have a system-'
                                                'response-removed column. '
                                                'Would you like to provide a '
                                                'system response?',
                                                QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                sysres_filepath = self.getSystemResponseFilePath()
                if sysres_filepath:
                    spectrum = MeasuredSpectrum.open(filepath, sysres_filepath)

        # remove the previous measured spectrum
        if self.spectrum:
            result = QtGui.QMessageBox.question(self,
                                                'Clear plot?',
                                                'Do you want to clear the '
                                                'plot?',
                                                QtGui.QMessageBox.Yes,
                                                QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                self.clearPlot()

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
        AboutDialog().exec_()

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
            if self.spectrometer:
                self.spectrometer.thread.quit()
            if self.lockin:
                self.lockin.thread.quit()
            if self.spectrometer:
                self.spectrometer.thread.wait()
            if self.lockin:
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
