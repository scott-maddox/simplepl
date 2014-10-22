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
import threading

# third party imports
from PySide import QtCore


class BaseScanner(QtCore.QObject):

    started = QtCore.Signal()
    finished = QtCore.Signal()
    statusChanged = QtCore.Signal(str)

    def __init__(self):
        super(BaseScanner, self).__init__()
        self.wantsAbort = threading.Event()
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._started)
        self.thread.finished.connect(self.finished)

    def _started(self):
        self.started.emit()
        self._scan()
        self.thread.quit()

    def start(self):
        self.thread.start()

    def abort(self):
        self.wantsAbort.set()

    def wait(self):
        self.thread.wait()

    def isScanning(self):
        return self.thread.isRunning()


class GoToer(BaseScanner):

    def __init__(self, spectrometer, wavelength):
        super(GoToer, self).__init__()
        self.spectrometer = spectrometer
        self.wavelength = wavelength

    def _scan(self):
        self.statusChanged.emit('Changing wavelength...')
        self.spectrometer.setWavelength(self.wavelength)
        self.statusChanged.emit('Idle.')


class Scanner(BaseScanner):

    def __init__(self, spectrometer, lockin, spectrum,
                 start, stop, step, delay):
        super(Scanner, self).__init__()
        self.spectrometer = spectrometer
        self.lockin = lockin
        self.spectrum = spectrum
        self._start = start
        self._stop = stop
        self._step = step
        self._delay = delay

        self.settings = QtCore.QSettings()

    def _scan(self):
        # Apply the spectrometer and lockin config's
        self.statusChanged.emit('Configuring Diverters...')
        self._applyDivertersConfig()
        self.statusChanged.emit('Configuring Lock-in...')
        self._applyLockinConfig()

        # Start the scan
        self.statusChanged.emit('Scanning...')
        target_wavelength = self._start
        last_grating = self.spectrometer.getGrating()
        last_filter = self.spectrometer.getFilter()
        while True:
            # Check for abort
            if self.wantsAbort.isSet():
                # Abort the scan
                self.statusChanged.emit('Scan aborted.')
                return

            # Move the spectrometer
            self.spectrometer.setWavelength(target_wavelength)

            # Check if the grating or filter changed
            new_grating = self.spectrometer.getGrating()
            new_filter = self.spectrometer.getFilter()
            if new_grating != last_grating or new_filter != last_filter:
                # Grating or filter switched. Wait 5 time constants
                # before continuing the scan.
                self.thread.sleep(self.lockin.getTimeConstantSeconds() * 5)
            last_grating = new_grating
            last_filter = new_filter

            # Take a measurement
            wavelength = self.spectrometer.getWavelength()
            rawSignal, phase = self.lockin.adjustAndGetOutputs(self._delay)

            # Append to the spectrum
            self.spectrum.append(wavelength, rawSignal, phase)

            # Check if we're done
            target_wavelength += self._step
            if target_wavelength > self._stop:
                break

        # The scan is finished.
        self.statusChanged.emit('Scan finished.')

    def _applyDivertersConfig(self):
        entranceMirror = self.settings.value('spectrometer/entrance_mirror',
                                             'Front')
        exitMirror = self.settings.value('spectrometer/exit_mirror',
                                         'Side')
        self.spectrometer.setEntranceMirror(entranceMirror)
        self.spectrometer.setExitMirror(exitMirror)

    def _applyLockinConfig(self):
        timeConstantIndex = int(self.settings.value(
                                            'lockin/time_constant_index',
                                            9))  # 300 ms default
        reserveModeIndex = int(self.settings.value(
                                            'lockin/reserve_mode_index',
                                            0))  # High reserve default
        inputLineFilterIndex = int(self.settings.value(
                                            'lockin/input_line_filter_index',
                                            3))  # both filters default
        self.lockin.setTimeConstantIndex(timeConstantIndex)
        self.lockin.setReserveModeIndex(reserveModeIndex)
        self.lockin.setInputLineFilterIndex(inputLineFilterIndex)
