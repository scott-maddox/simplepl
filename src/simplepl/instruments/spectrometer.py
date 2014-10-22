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
        self.thread.started.connect(self._init)
        self.moveToThread(self.thread)

    def _init(self):
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

        # Initialized cached values
        self._grating = None
        self._filter = None
        self._wavelength = None

        # Start the thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._init)

    def _init(self):
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
        self.getGrating()
        self.getFilter()
        self.getWavelength()

    def getGratingCount(self):
        return 9

    def getFilterCount(self):
        return 6

    @QtCore.Slot()
    def getGrating(self):
        if self._spectrometer is None:
            return
        if self._grating is not None:
            return self._grating
        with QtCore.QMutexLocker(self._spectrometerLock):
            result = self._spectrometer.get_grating()
        self._grating = result
        self.sigGrating.emit(result)
        return result

    @QtCore.Slot(int)
    def setGrating(self, i):
        self._grating = None
        self.sigChangingGrating.emit()
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer.set_grating(i)
        self.getGrating()  # read and emit the resulting grating

    @QtCore.Slot()
    def getFilter(self):
        if self._spectrometer is None:
            return
        if self._filter is not None:
            return self._filter
        with QtCore.QMutexLocker(self._filterWheelLock):
            result = self._filterWheel.get_filter()
        self._filter = result
        self.sigFilter.emit(result)
        return result

    @QtCore.Slot(int)
    def setFilter(self, i):
        self._filter = None
        self.sigChangingFilter.emit()
        with QtCore.QMutexLocker(self._filterWheelLock):
            self._filterWheel.set_filter(i)
        self.getFilter()  # read and emit the resulting filter

    @QtCore.Slot(int, int)
    def setGratingAndFilter(self, grating, filter):
        self._filter = None
        filterChanger = FilterChanger(filter,
                                      self._filterWheel,
                                      self._filterWheelLock)
        self.sigChangingFilter.emit()
        filterChanger.start()
        self.setGrating(grating)
        filterChanger.wait()
        self._filter = filterChanger.result
        self.sigFilter.emit(filterChanger.result)

    @QtCore.Slot()
    def getWavelength(self):
        '''
        Returns the current wavelength in nm.

        Emits
        -----
            sigWavelength(float)
        '''
        if self._spectrometer is None:
            return
        if self._wavelength is not None:
            return self._wavelength
        with QtCore.QMutexLocker(self._spectrometerLock):
            result = self._spectrometer.get_wavelength()
        self._wavelength = result
        self.sigWavelength.emit(result)
        return result

    @QtCore.Slot(float)
    def setWavelength(self, wavelength):
        self._wavelength = None
        self.sigChangingWavelength.emit()

        # Change the grating and/or filter, if needed
        targetGrating, targetFilter = self._getTargetGratingAndFilter(
                                                                wavelength)
        if self.getGrating() != targetGrating:
            if self.getFilter() != targetFilter:
                self.setGratingAndFilter(targetGrating, targetFilter)
            else:
                self.setGrating(targetGrating)
        elif self.getFilter() != targetFilter:
            self.setFilter(targetFilter)

        # Go to the specified target wavelength
        with QtCore.QMutexLocker(self._spectrometerLock):
            self._spectrometer.goto(wavelength)
        self.getWavelength()  # read and emit the resulting wavelength

    def _getTargetGratingAndFilter(self, wavelength):
        '''
        Gets the target grating and filter for a given wavelength from
        the config.
        '''
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

    def setEntranceMirror(self, s):
        if s == 'Front':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_entrance_mirror_front()
        elif s == 'Side':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_entrance_mirror_side()
        else:
            raise ValueError('Unkown entrance mirror position: {}'.format(s))

    def setExitMirror(self, s):
        if s == 'Front':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_exit_mirror_front()
        elif s == 'Side':
            with QtCore.QMutexLocker(self._spectrometerLock):
                self._spectrometer.set_exit_mirror_side()
        else:
            raise ValueError('Unkown exit mirror position: {}'.format(s))
