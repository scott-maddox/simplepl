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
    _sigAdjustAndGetOutputs = QtCore.Signal(float)

    sigException = QtCore.Signal(Exception)
    sigInitialized = QtCore.Signal()

    sigRawSignal = QtCore.Signal(float)
    sigPhase = QtCore.Signal(float)
    sigAdjustAndGetOutputsFinished = QtCore.Signal(float, float)

    sigTimeConstantIndex = QtCore.Signal(int)
    sigTimeConstantSeconds = QtCore.Signal(float)

    def __init__(self):
        super(Lockin, self).__init__()
        self._instLock = QtCore.QMutex()
        self._inst = None
        self._sigAdjustAndGetOutputs.connect(self._adjustAndGetOutputs)

        # Start the thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._started)
        self.thread.start()

    def _started(self):
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

    def getTimeConstantOptions(self):
        return self._inst.time_constant_labels

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

    def requestTimeConstantIndex(self):
        '''
        Non-blocking

        Emits
        -----
        sigTimeConstantIndex
        '''
        QtCore.QTimer.singleShot(0, self.getTimeConstantIndex)

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
    def _adjustAndGetOutputs(self, delay):
        with QtCore.QMutexLocker(self._instLock):
            raw_signal, phase = self._inst.adjust_and_get_outputs(delay)
        self.sigRawSignal.emit(raw_signal)
        self.sigPhase.emit(phase)
        self.sigAdjustAndGetOutputsFinished.emit(raw_signal, phase)

    def adjustAndGetOutputs(self, delay):
        '''
        Adjust the sensitivity and gets the signal and phase.

        Params
        ------
        delay : float
            The delay time in seconds. A delay of 5x the time constant is
            strongly recommended.

        Emits
        -----
        sigAdjustAndGetOutputsFinished(float, float)
        '''
        self._sigAdjustAndGetOutputs.emit(delay)
