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
import numpy as np

# local imports
from abstract_spectrum import AbstractSpectrum
from simple_pl_parser import SimplePLParser


class MeasuredSpectrum(AbstractSpectrum):

    def __init__(self, wavelength, signal=None, rawSignal=None, phase=None):
        super(MeasuredSpectrum, self).__init__()
        self._wavelength = wavelength
        self._signal = signal
        self._rawSignal = rawSignal
        self._phase = phase

    def getWavelength(self):
        return self._wavelength

    def getSignal(self):
        return self._signal

    def getRawSignal(self):
        return self._rawSignal

    def getPhase(self):
        return self._phase

    def getEnergy(self):
        return 1239.842 / self.getWavelength()

    @classmethod
    def open(cls, filepath, sysres_filepath=None):
        parser = SimplePLParser(filepath, sysres_filepath)
        parser.parse()
        return cls(wavelength=parser.wavelength,
                   signal=parser.signal,
                   rawSignal=parser.rawSignal,
                   phase=parser.phase)

    def save(self, filepath):
        wavelengths = self.getWavelength()
        signals = self.getSignal()
        rawSignals = self.getRawSignal()
        phases = self.getPhase()
        with open(filepath, 'w') as f:
            f.write('Wavelength\tSignal\tRaw_Signal\tPhase\n')
            for i in xrange(wavelengths.size):
                if wavelengths is not None:
                    wavelength = wavelengths[i]
                else:
                    wavelength = np.nan
                if signals is not None:
                    signal = signals[i]
                else:
                    signal = np.nan
                if rawSignals is not None:
                    rawSignal = rawSignals[i]
                else:
                    rawSignal = np.nan
                if phases is not None:
                    phase = phases[i]
                else:
                    phase = np.nan
                f.write('%.1f\t%E\t%E\t%.1f\n' % (wavelength,
                                                  signal,
                                                  rawSignal,
                                                  phase))
