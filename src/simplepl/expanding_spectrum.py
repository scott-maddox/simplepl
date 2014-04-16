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
from measured_spectrum import MeasuredSpectrum
from expanding_buffer import ExpandingBuffer

class ExpandingSpectrum(MeasuredSpectrum):
    def __init__(self, sysresParser=None):
        super(MeasuredSpectrum, self).__init__()
        self.sysresParser = sysresParser
        self._wavelength = ExpandingBuffer()
        self._energy = ExpandingBuffer()
        self._raw = ExpandingBuffer()
        self._phase = ExpandingBuffer()
        self._sysresrem = ExpandingBuffer()
    
    def append(self, wavelength, raw, phase):
        if self.sysresParser is None:
            sysresrem = raw
        else:
            i = np.searchsorted(self.sysresParser.wavelength, wavelength)
            sysresrem = raw / self.sysresParser.raw[i]
        self._wavelength.append(wavelength)
        self._energy.append(1239.842/wavelength)
        self._raw.append(raw)
        self._phase.append(phase)
        self._sysresrem.append(sysresrem)
        self.sigChanged.emit()
    
    def _getWavelength(self):
        return self._wavelength.get()
    
    def _getRaw(self):
        return self._raw.get()
    
    def _getPhase(self):
        return self._phase.get()
    
    def _getIntensity(self):
        return self._sysresrem.get()
    
    def _getEnergy(self):
        return self._energy.get()
    
    wavelength = QtCore.Property(np.ndarray, _getWavelength)
    raw = QtCore.Property(np.ndarray, _getRaw)
    phase = QtCore.Property(np.ndarray, _getPhase)
    intensity = QtCore.Property(np.ndarray, _getIntensity)
    energy = QtCore.Property(np.ndarray, _getEnergy)
    
    def save(self, filepath):
        wavelength = self._wavelength.get()
        raw = self._raw.get()
        sysresrem = self._sysresrem.get()
        with open(filepath, 'w') as f:
            f.write('Wavelength\tRaw\tSysResRem\n')
            for i in xrange(wavelength.size):
                f.write('%.1f\t%E\t%E\n'%(wavelength[i], raw[i],
                                          sysresrem[i]))