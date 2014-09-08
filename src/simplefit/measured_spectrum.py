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
from simplepl.simple_pl_parser import SimplePLParser

class MeasuredSpectrum(AbstractSpectrum):
    
    def __init__(self, wavelength, intensity):
        super(MeasuredSpectrum, self).__init__()
        self.wavelength = wavelength
        self.intensity = intensity
    
    def _getEnergy(self):
        '''Returns the energy array'''
        return 1239.842/self.wavelength
    
    energy = QtCore.Property(np.ndarray, _getEnergy)

def openMeasuredSpectrum(filepath, sysres_filepath=None):
    parser = SimplePLParser(filepath, sysres_filepath)
    parser.parse()
    return MeasuredSpectrum(parser.wavelength, parser.signal)