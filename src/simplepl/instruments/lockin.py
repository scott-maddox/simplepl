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


class Lockin(QtCore.QObject):
    '''
    Provides an asynchronous QThread interface to the lockin amplifier.

    Under the hood, this class uses Signals to call functions in another
    thread. The results are emitted in other Signals, which are specified
    in the doc strings.
    '''

    sigException = QtCore.Signal(Exception)
    sigInitialized = QtCore.Signal()

    sigRawSignal = QtCore.Signal(float)
    sigPhase = QtCore.Signal(float)

    sigTimeConstantIndex = QtCore.Signal(int)
    sigTimeConstantSeconds = QtCore.Signal(float)

    def __init__(self):
        super(Lockin, self).__init__()
        self._instLock = QtCore.QMutex()
        self._inst = None

        # Start the thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._init)
        self.thread.start()

    def _init(self):
        settings = QtCore.QSettings()
        simulate = int(settings.value('simulate', False))
        if simulate:
            print "Simulating lock-in..."
            from drivers.srs_sr830_sim import SR830
        else:
            from drivers.srs_sr830 import SR830

        lockinPort = settings.value('lockin/port', 'GPIB::8')
        with QtCore.QMutexLocker(self._instLock):
            try:
                self._inst = SR830(port=lockinPort)
            except:
                e = IOError('Unable to connect to lock-in at port {}'
                            ''.format(lockinPort))
                self.sigException.emit(e)
                return

        # Notify the gui that initialization went fine
        self.sigInitialized.emit()

    def getTimeConstantLabelsList(self):
        with QtCore.QMutexLocker(self._instLock):
            return self._inst.time_constant_labels

    def getTimeConstantSecondsList(self):
        with QtCore.QMutexLocker(self._instLock):
            return self._inst.time_constant_seconds

    @QtCore.Slot()
    def getTimeConstantIndex(self):
        '''
        Blocking

        Emits
        -----
        sigTimeConstantIndex
        '''
        with QtCore.QMutexLocker(self._instLock):
            i = self._inst.get_time_constant_index()
        self.sigTimeConstantIndex.emit(i)
        return i

    @QtCore.Slot()
    def getTimeConstantSeconds(self):
        '''
        Returns the time constant in seconds.

        Emits
        -----
        sigTimeConstantSeconds
        '''
        i = self.getTimeConstantIndex()
        seconds = self.getTimeConstantSecondsList()[i]
        self.sigTimeConstantSeconds.emit(seconds)
        return seconds

    @QtCore.Slot(int)
    def setTimeConstantIndex(self, i):
        with QtCore.QMutexLocker(self._instLock):
            self._inst.set_time_constant_index(i)

    @QtCore.Slot(int)
    def setReserveModeIndex(self, i):
        with QtCore.QMutexLocker(self._instLock):
            self._inst.set_reserve_mode(i)

    @QtCore.Slot(int)
    def setInputLineFilterIndex(self, i):
        with QtCore.QMutexLocker(self._instLock):
            self._inst.set_input_line_filter(i)

    @QtCore.Slot(float)
    def adjustAndGetOutputs(self, delay):
        '''
        Adjust the sensitivity and returns the rawSignal and phase.

        Params
        ------
        delay : float
            The delay time in seconds. A delay of 5x the time constant is
            recommended.

        Emits
        -----
        sigRawSignal(float)
        sigPhase(float)
        '''
        with QtCore.QMutexLocker(self._instLock):
            rawSignal, phase = self._inst.adjust_and_get_outputs(delay)
        self.sigRawSignal.emit(rawSignal)
        self.sigPhase.emit(phase)
        return rawSignal, phase
