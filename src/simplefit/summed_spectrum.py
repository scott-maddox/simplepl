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

class SummedSpectrum(AbstractSpectrum):
    def __init__(self, *spectra, **kwargs):
        super(SummedSpectrum, self).__init__(**kwargs)
        self._spectra = []
        for spectrum in spectra:
            self.addSpectrum(spectrum)

    def addSpectrum(self, spectrum):
        self._spectra.append(spectrum)
        spectrum.sigChanged.connect(self.sigChanged)
        self.sigChanged.emit()
    
    def removeSpectrum(self, spectrum):
        self._spectra.remove(spectrum)
        spectrum.sigChanged.disconnect(self.sigChanged)
        self.sigChanged.emit()
    
    def getIntensity(self):
        if not self._spectra:
            return

        for spectrum in self._spectra:
            if spectrum.intensity is None:
                return

        sum = self._spectra[0].intensity
        for spectrum in self._spectra[1:]:
            sum += spectrum.intensity
        return sum
    
    intensity = QtCore.Property(np.ndarray, getIntensity)