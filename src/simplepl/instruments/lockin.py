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


class Lockin(QtCore.QObject):
    '''
    Provides an asynchronous QThread interface to the lockin amplifier.

    Under the hood, this class uses Signals to call functions in another
    thread. The results are emitted in other Signals, which are specified
    in the doc strings.
    '''
    _sigRequestQuit = QtCore.Signal()
    _sigAdjustAndGetOutputs = QtCore.Signal(float)

    sigRawSignal = QtCore.Signal(float)
    sigPhase = QtCore.Signal(float)
    sigAdjustAndGetOutputsFinished = QtCore.Signal(float, float)

    def __init__(self):
        super(Lockin, self).__init__()
        self._inst = None
        self._sigRequestQuit.connect(self.quit)
        self._sigAdjustAndGetOutputs.connect(self._adjustAndGetOutputs)

        # Start the thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self._started)
        self.thread.start()

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

    def _started(self):
        settings = QtCore.QSettings()
        simulate = settings.value('simulate', False)
        if simulate:
            print "Simulating lock-in..."
            from drivers.srs_sr830_sim import SR830
        else:
            from drivers.srs_sr830 import SR830
        self._inst = SR830()

    @QtCore.Slot(float)
    def _adjustAndGetOutputs(self, delay):
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
