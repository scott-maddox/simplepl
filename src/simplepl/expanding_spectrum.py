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
import logging
log = logging.getLogger(__name__)
from PySide import QtCore
import numpy as np

# local imports
from measured_spectrum import MeasuredSpectrum
from expanding_buffer import ExpandingBuffer


class ExpandingSpectrum(MeasuredSpectrum):

    def __init__(self, sysresParser=None):
        super(MeasuredSpectrum, self).__init__()
        self.sysresParser = sysresParser
        self._wavelength = ExpandingBuffer()
        self._energy = ExpandingBuffer()
        self._rawSignal = ExpandingBuffer()
        self._phase = ExpandingBuffer()
        self._signal = ExpandingBuffer()

    def append(self, wavelength, rawSignal, phase):
        if self.sysresParser is None:
            log.warning("No sysrem response provided. Using raw value.")
            signal = rawSignal
        else:
            sysres = self.sysresParser.getSysRes(wavelength)
            signal = rawSignal / sysres
        self._wavelength.append(wavelength)
        self._signal.append(signal)
        self._rawSignal.append(rawSignal)
        self._phase.append(phase)
        self._energy.append(1239.842 / wavelength)
        self.sigChanged.emit()

    def getWavelength(self):
        return self._wavelength.get()

    def getSignal(self):
        return self._signal.get()

    def getRawSignal(self):
        return self._rawSignal.get()

    def getPhase(self):
        return self._phase.get()

    def getEnergy(self):
        return self._energy.get()
