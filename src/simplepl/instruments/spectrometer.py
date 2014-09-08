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

# local imports


class FilterChanger(QtCore.QObject):
    def __init__(self, targetFilter, filterWheel, lock):
        super(FilterChanger, self).__init__()
        self._targetFilter = targetFilter
        self._filterWheelLock = lock
        self._filterWheel = filterWheel
        self.thread = QtCore.QThread()
        self.thread.started.connect(self._started)
        self.moveToThread(self.thread)

    def _started(self):
        with QtCore.QMutexLocker(self._filterWheelLock):
            self._filterWheel.set_filter(self._targetFilter)
            self.result = self._filterWheel.get_filter()
        self.thread.quit()

    def start(self):
        self.thread.start()

    def wait(self):
        self.thread.wait()


class Spectrometer(QtCore.QObject):
    '''
    Provides an asynchronous interface to the spectrometer.

    Under the hood, this class uses Signals to call functions in another
    thread. The results are emitted in other Signals, which are specified
    in the doc strings.
    '''
    _sigGetGrating = QtCore.Signal()
    _sigSetGrating = QtCore.Signal(int)
    _sigGetFilter = QtCore.Signal()
    _sigSetFilter = QtCore.Signal(int)
    _sigGetWavelength = QtCore.Signal()
    _sigSetWavelength = QtCore.Signal(float)
    _sigSetEntranceMirror = QtCore.Signal(str)
    _sigSetExitMirror = QtCore.Signal(str)

    sigException = QtCore.Signal(Exception)
    sigInitialized = QtCore.Signal()

    sigChangingGrating = QtCore.Signal()
    sigChangingFilter = QtCore.Signal()
    sigChangingWavelength = QtCore.Signal()

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

    def _started(self):
        # Initialize QSettings object
        self._settings = QtCore.QSettings()

        simulate = int(self._settings.value('simulate', False))
        if simulate:
            print "Simulating spectrometer and filter wheel..."
            from drivers.spectra_pro_2500i_sim import SpectraPro2500i
            from drivers.thorlabs_fw102c_sim import FW102C
        else:
            from drivers.spectra_pro_2500i import SpectraPro2500i
            from drivers.thorlabs_fw102c import FW102C

        # Initialize the spectrometer
        spectrometerPort = int(self._settings.value('spectrometer/port', 3))
        with QtCore.QMutexLocker(self._spectrometerLock):
            try:
                self._spectrometer = SpectraPro2500i(port=spectrometerPort)
            except:
                e = IOError('unable to connect to spectrometer at '
                            'port {}'.format(spectrometerPort))
                self.sigException.emit(e)
                return

        # Initialize the filter wheel
        filterWheelPort = int(self._settings.value('filterWheel/port', 3))
        with QtCore.QMutexLocker(self._filterWheelLock):
            try:
                self._filterWheel = FW102C(port=filterWheelPort)
            except:
                e = IOError('unable to connect to filter wheel at '
                            'port {}'.format(filterWheelPort))
                self.sigException.emit(e)
                return

        # Notify the gui that initialization went fine
        self.sigInitialized.emit()

        # Initialize the statusbar
        self._getGrating()
        self._getFilter()
        self._getWavelength()

    def getGratingCount(self):
        return 9

    def getFilterCount(self):
        return 6

    @QtCore.Slot()
    def _getGrating(self):
        if self._spectrometer is None:
            return
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
        if self._spectrometer is None:
            return
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

    @QtCore.Slot(int, int)
    def _setGratingAndFilter(self, grating, filter):
        filterChanger = FilterChanger(filter,
                                      self._filterWheel,
                                      self._filterWheelLock)
        self.sigChangingFilter.emit()
        filterChanger.start()
        self._setGrating(grating)
        filterChanger.wait()
        self._filter = filterChanger.result
        self.sigFilter.emit(filterChanger.result)

    @QtCore.Slot()
    def _getWavelength(self):
        if self._spectrometer is None:
            return
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

    def _getTargetGratingAndFilter(self, wavelength):
        wavelengths, gratings, filters = self.getConfigs()
        if wavelength < wavelengths[0]:
            raise ValueError('wavelengths shorter than {} are not supported'
                             ''.format(wavelengths[0]))
        for i in xrange(len(gratings)):
            if wavelength <= wavelengths[i + 1]:
                return gratings[i], filters[i]
        else:
            raise ValueError('wavelengths longer than {} are not supported'
                             ''.format(wavelengths[i + 1]))

    @QtCore.Slot(float)
    def _setWavelength(self, wavelength):
        # Change the grating and/or filter, if needed
        targetGrating, targetFilter = self._getTargetGratingAndFilter(
                                                                wavelength)

        if self._grating is None:
            self._getGrating()
        if self._filter is None:
            self._getFilter()
        if self._grating != targetGrating and self._filter != targetFilter:
            self._setGratingAndFilter(targetGrating, targetFilter)
        if self._grating != targetGrating:
            self.setGrating(targetGrating)
        if self._filter != targetFilter:
            self.setFilter(targetFilter)

        # Go to the specified target wavelength
        self.sigChangingWavelength.emit()
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer.goto(wavelength)
        self._getWavelength()  # read and emit the resulting wavelength

    def getConfigs(self):
        '''
        Returns
        -------
        wavelengths : list of floats of length N
        gratings : list of ints of length (N - 1)
        filters : list of ints of length (N - 1)
        '''
        wavelengths = []
        gratings = []
        filters = []
        size = self._settings.beginReadArray('spectrometer/configs')
        for i in xrange(size - 1):
            self._settings.setArrayIndex(i)
            wavelengths.append(float(self._settings.value('wavelength')))
            gratings.append(int(self._settings.value('grating')))
            filters.append(int(self._settings.value('filter')))
        self._settings.setArrayIndex(size - 1)
        wavelengths.append(self._settings.value('wavelength'))
        self._settings.endArray()
        return wavelengths, gratings, filters

    def setConfigs(self, wavelengths, gratings, filters):
        '''
        Parameters
        ----------
        wavelengths : list of floats of length N
        gratings : list of ints of length (N - 1)
        filters : list of ints of length (N - 1)
        '''
        assert wavelengths == sorted(wavelengths)
        size = len(wavelengths)
        self._settings.beginWriteArray('spectrometer/configs', size=size)
        for i in xrange(size - 1):
            self._settings.setArrayIndex(i)
            self._settings.setValue('wavelength', wavelengths[i])
            self._settings.setValue('grating', gratings[i])
            self._settings.setValue('filter', filters[i])
        self._settings.setArrayIndex(size - 1)
        self._settings.setValue('wavelength', wavelengths[size - 1])
        self._settings.endArray()
        self._settings.sync()
        return wavelengths, gratings, filters

    def getMinWavelength(self):
        _size = self._settings.beginReadArray('spectrometer/configs')
        self._settings.setArrayIndex(0)
        wavelength = float(self._settings.value('wavelength', 0.))
        self._settings.endArray()
        return wavelength

    def getMaxWavelength(self):
        size = self._settings.beginReadArray('spectrometer/configs')
        self._settings.setArrayIndex(size - 1)
        wavelength = float(self._settings.value('wavelength', 10000.))
        self._settings.endArray()
        return wavelength

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
