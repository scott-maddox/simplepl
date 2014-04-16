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
from PySide import QtGui, QtCore

# local imports
from spectrum.calculated_spectrum import ConstantSpectrum

class ConstantSpectrumWidget(QtGui.QWidget):
    def __init__(self, spectrum):
        super(ConstantSpectrumWidget, self).__init__()
        assert isinstance(spectrum, ConstantSpectrum)
        self.spectrum = spectrum
        
        self.constantSlider = QtGui.Slider(QtCore.Qt.Horizontal)
        self.constantSlider.valueChanged.connect(self.update)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.constantSlider)
        self.setLayout(layout)
    
    def update(self):
        self.spectrum.setConstant(self.constantSlider.value())

# I want this to allow adding and removing of spectra to and from a
# SummedSpectrum, and to allow individual control of each parameter.
class SummedSpectrumWidget(QtGui.QWidget):
    def __init__(self, *spectra):
        super(SummedSpectrumWidget, self).__init__()
        self.widgets = []
        for spectrum in spectra:
            assert isinstance(spectrum, AbstractSpectrum)
            spectrum.sigChanged.connect(self.update)
        self.spectra = spectra
        
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.update()
    
    def update(self):
        raise NotImplementedError()
            