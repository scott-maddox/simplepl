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
from parameter_widgets import (BoundedFloatParameterSlider)
from abstract_spectrum import AbstractSpectrum
from simulated_spectrum import (ConstantSpectrum, GaussianSpectrum,
                                LorentzianSpectrum,
                                AsymmetricGaussianSpectrum,
                                WaveVectorConservingPLSpectrum,
                                WaveVectorNonConservingPLSpectrum)

class SpectrumControlWidget(QtGui.QWidget):
    '''
    Provides a BoundedFloatParameterSlider and labels for each parameter in a
    simulated spectrum.
    '''
    sigRemoveClicked = QtCore.Signal(AbstractSpectrum)
    sigParameterChanged = QtCore.Signal(QtCore.QObject)
    
    def __init__(self, spectrum, *args, **kwargs):
        super(SpectrumControlWidget, self).__init__(*args, **kwargs)
        self.spectrum = spectrum
        self.sliders = []
        self.lockFitCheckBoxes = []
        
        self.label = QtGui.QLabel(self._getSpectrumLabel(spectrum))
        removeButton = QtGui.QPushButton('Remove')
        removeButton.resize(removeButton.sizeHint().width(),
                            removeButton.sizeHint().height())
        removeButton.clicked.connect(self._emitSigRemoveClicked)
        
        # Layout
        layout = QtGui.QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QtGui.QHBoxLayout()
        layout.addLayout(header)
        header.addWidget(self.label)
        header.addStretch(1)
        header.addWidget(removeButton)
        grid = QtGui.QGridLayout()
        layout.addLayout(grid)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        for i, p in enumerate(spectrum.parameters):
            grid.addWidget(QtGui.QLabel(p.label), i+1, 0)
            slider = BoundedFloatParameterSlider(parameter=p,
                                    orientation=QtCore.Qt.Horizontal)
            slider.sigParameterChanged.connect(self.sigParameterChanged)
            self.sliders.append(slider)
            grid.addWidget(slider, i+1, 1)
            lockFitCheckBox = QtGui.QCheckBox()
            self.lockFitCheckBoxes.append(lockFitCheckBox)
            grid.addWidget(lockFitCheckBox, i+1, 2)
        grid.setRowStretch(grid.rowCount(), 1)
    
    def _emitSigRemoveClicked(self):
        self.sigRemoveClicked.emit(self.spectrum)
    
    def _getSpectrumLabel(self, spectrum):
        if isinstance(spectrum, ConstantSpectrum):
            return 'Constant'
        elif isinstance(spectrum, GaussianSpectrum):
            return 'Gaussian'
        elif isinstance(spectrum, LorentzianSpectrum):
            return 'Lorentzian'
        elif isinstance(spectrum, AsymmetricGaussianSpectrum):
            return 'Asymmetric Gaussian'
        elif isinstance(spectrum, WaveVectorConservingPLSpectrum):
            return 'Wave vector conserving PL'
        elif isinstance(spectrum, WaveVectorNonConservingPLSpectrum):
            return 'Wave vector non-conserving PL'
        else:
            raise TypeError('unknown spectrum type: %s'%type(spectrum))

if __name__ == '__main__':
    from vertical_scroll_area import VerticalScrollArea
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    s1 = ConstantSpectrum()
    s2 = GaussianSpectrum()
    s3 = LorentzianSpectrum()
    sc1 = SpectrumControlWidget(s1)
    #sc1.setStyleSheet("QObject { background-color: blue; }")
    sc2 = SpectrumControlWidget(s2)
    #sc2.setStyleSheet("QObject { background-color: red; }")
    sc3 = SpectrumControlWidget(s3)
    #sc3.setStyleSheet("QObject { background-color: green; }")
    layout = QtGui.QVBoxLayout(w)
    #layout.setSpacing(0)
    #layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(sc1)
    layout.addWidget(sc2)
    layout.addWidget(sc3)
    layout.addStretch(1)
    #w.show()
    #w.raise_()
    scroll = VerticalScrollArea()
    scroll.setWidget(w)
    scroll.show()
    scroll.raise_()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()