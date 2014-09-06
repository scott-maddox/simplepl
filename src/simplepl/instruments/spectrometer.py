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

# local imports


class Spectrometer(QtCore.QObject):
    '''
    Provides an asynchronous interface to the spectrometer.

    Under the hood, this class uses Signals to call functions in another
    thread. The results are emitted in other Signals, which are specified
    in the doc strings.
    '''
    _sigRequestQuit = QtCore.Signal()
    _sigGetGrating = QtCore.Signal()
    _sigSetGrating = QtCore.Signal(int)
    _sigGetFilter = QtCore.Signal()
    _sigSetFilter = QtCore.Signal(int)
    _sigGetWavelength = QtCore.Signal()
    _sigSetWavelength = QtCore.Signal(float)
    _sigSetEntranceMirror = QtCore.Signal(str)
    _sigSetExitMirror = QtCore.Signal(str)

    sigChangingGrating = QtCore.Signal()
    sigChangingFilter = QtCore.Signal()

    sigGrating = QtCore.Signal(int)
    sigFilter = QtCore.Signal(int)
    sigWavelength = QtCore.Signal(float)

    def __init__(self):
        super(Spectrometer, self).__init__()
        # Initialize variables
        self._spectrometerLock = QtCore.QMutex()
        self._spectrometer = None
        self._filterWheelLock = QtCore.QMutex()
        self._filterWheel = None
        self._settings = None
        self._grating = None
        self._filter = None

        # Connect signals/slots for asynchronous methods
        self._sigRequestQuit.connect(self.quit)
        self._sigGetGrating.connect(self._getGrating)
        self._sigSetGrating.connect(self._setGrating)
        self._sigGetFilter.connect(self._getFilter)
        self._sigSetFilter.connect(self._setFilter)
        self._sigGetWavelength.connect(self._getWavelength)
        self._sigSetWavelength.connect(self._setWavelength)
        self._sigSetEntranceMirror.connect(self._setEntranceMirror)
        self._sigSetExitMirror.connect(self._setExitMirror)

        # Start the thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._started)
        self.thread.start()

    def _started(self):
        # Initialize QSettings object
        self._settings = QtCore.QSettings()

        simulate = self._settings.value('simulate', False)
        if simulate:
            print "Simulating spectrometer and filter wheel..."
            from drivers.spectra_pro_2500i_sim import SpectraPro2500i
            from drivers.thorlabs_fw102c_sim import FW102C
        else:
            from drivers.spectra_pro_2500i import SpectraPro2500i
            from drivers.thorlabs_fw102c import FW102C

        # Initialize the spectrometer
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer = SpectraPro2500i()

        # Initialize the filter wheel
        filterWheelPort = int(self._settings.value('filterWheel/port', 3))
        with QtCore.QMutexLocker(self._filterWheelLock):
            self._filterWheel = FW102C(port=filterWheelPort)

    @QtCore.Slot()
    def quit(self):
        self.thread.quit()

    def requestQuit(self):
        '''
        Sends a request to the spectrometer thread to quit.

        In order to give it time to quit on close, use the following:
            spectrometer.requestQuit()
            spectrometer.wait()
        '''
        self._sigRequestQuit.emit()

    @QtCore.Slot()
    def _getGrating(self):
        with QtCore.QMutexLocker(self._spectrometerLock):
            result = self._spectrometer.get_grating()
        self._grating = result
        self.sigGrating.emit(result)
        return result

    def getGrating(self):
        '''
        Gets the current grating index.

        Emits
        -----
            sigGrating(int)
        '''
        self._sigGetGrating.emit()

    @QtCore.Slot(int)
    def _setGrating(self, i):
        self.sigChangingGrating.emit()
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer.set_grating(i)
        self._getGrating()  # read and emit the resulting grating

    def setGrating(self, i):
        '''
        Goes to the specified grating index.

        Emits
        -----
            sigGrating(int)
            sigWavelength(float)
        '''
        self._sigSetGrating.emit(i)

    @QtCore.Slot()
    def _getFilter(self):
        with QtCore.QMutexLocker(self._filterWheelLock):
            result = self._filterWheel.get_filter()
        self._filter = result
        self.sigFilter.emit(result)
        return result

    def getFilter(self):
        '''
        Gets the current filter index.

        Emits
        -----
            sigFilter(int)
        '''
        self._sigGetFilter.emit()

    @QtCore.Slot(int)
    def _setFilter(self, i):
        self.sigChangingFilter.emit()
        with QtCore.QMutexLocker(self._filterWheelLock):
            self._filterWheel.set_filter(i)
        self._getFilter()  # read and emit the resulting filter

    def setFilter(self, i):
        '''
        Goes to the specified filter index.

        Emits
        -----
            sigFilter(int)
        '''
        self._sigSetFilter.emit(i)

    @QtCore.Slot()
    def _getWavelength(self):
        with QtCore.QMutexLocker(self._spectrometerLock):
            result = self._spectrometer.get_wavelength()
        self.sigWavelength.emit(result)
        return result

    def getWavelength(self):
        '''
        Gets the current wavelength in nm.

        Emits
        -----
            sigWavelength(float)
        '''
        self._sigGetWavelength.emit()

    def _getTargetGrating(self, wavelength):
        wlmin = float(self._settings.value(
                                    'spectrometer/grating/1/wavelength/min',
                                     2353.))
        wlmax = float(self._settings.value(
                                    'spectrometer/grating/1/wavelength/max',
                                     5500.01))
        if wavelength >= wlmin and wavelength < wlmax:
            return 1  # 4 um blaze

        wlmin = float(self._settings.value(
                                    'spectrometer/grating/2/wavelength/min',
                                     800.))
        wlmax = float(self._settings.value(
                                    'spectrometer/grating/2/wavelength/max',
                                     1592.))
        if wavelength >= wlmin and wavelength < wlmax:
            return 2  # 1.2 um blaze

        wlmin = float(self._settings.value(
                                    'spectrometer/grating/3/wavelength/min',
                                     1592.))
        wlmax = float(self._settings.value(
                                    'spectrometer/grating/3/wavelength/max',
                                     2353.))
        if wavelength >= wlmin and wavelength < wlmax:
            return 3  # 2 um blaze

        raise ValueError('wavelength not supported: {}'
                         ''.format(wavelength))

    def _getTargetFilter(self, wavelength):
        wlmin = float(self._settings.value(
                                    'spectrometer/filter/1/wavelength/min',
                                     800))
        wlmax = float(self._settings.value(
                                    'spectrometer/filter/1/wavelength/max',
                                     1592.))
        if wavelength >= wlmin and wavelength < wlmax:
            return 1  # 4 um blaze

        wlmin = float(self._settings.value(
                                    'spectrometer/filter/2/wavelength/min',
                                     1592.))
        wlmax = float(self._settings.value(
                                    'spectrometer/filter/2/wavelength/max',
                                     2621.))
        if wavelength >= wlmin and wavelength < wlmax:
            return 2  # 1.2 um blaze

        wlmin = float(self._settings.value(
                                    'spectrometer/filter/3/wavelength/min',
                                     2621.))
        wlmax = float(self._settings.value(
                                    'spectrometer/filter/3/wavelength/max',
                                     5500.01))
        if wavelength >= wlmin and wavelength < wlmax:
            return 3  # 2 um blaze

        raise ValueError('wavelength not supported: {}'
                         ''.format(wavelength))

    @QtCore.Slot(float)
    def _setWavelength(self, wavelength):
        # Change the grating, if needed
        if self._grating is None:
            self._getGrating()
        targetGrating = self._getTargetGrating(wavelength)
        if self._grating != targetGrating:
            self.setGrating(targetGrating)

        # Change the filter, if needed
        if self._filter is None:
            self._getFilter()
        targetFilter = self._getTargetFilter(wavelength)
        if self._filter != targetFilter:
            self.setFilter(targetFilter)

        # Go to the specified target wavelength
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer.goto(wavelength)
        self._getWavelength()  # read and emit the resulting wavelength

    def setWavelength(self, wavelength):
        '''
        Goes to the specified wavelength in wavelength. Automatically
        sets the grating and filter as configured in the settings.

        Emits
        -----
            sigWavelength(float)
        '''
        self._sigSetWavelength.emit(wavelength)

    def _setEntranceMirror(self, s):
        if s == 'Front':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_entrance_mirror_front()
        elif s == 'Side':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_entrance_mirror_side()
        else:
            raise ValueError('Unkown entrance mirror position: {}'.format(s))

    def _setExitMirror(self, s):
        if s == 'Front':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_exit_mirror_front()
        elif s == 'Side':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_exit_mirror_side()
        else:
            raise ValueError('Unkown exit mirror position: {}'.format(s))

    def setEntranceMirror(self, s):
        self._sigSetEntranceMirror.emit(s)

    def setExitMirror(self, s):
        self._sigSetExitMirror.emit(s)
