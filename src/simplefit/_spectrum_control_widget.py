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
from parameter_widgets import (BoundedFloatParameterControl)
from simulated_spectrum import (ConstantSpectrum, GaussianSpectrum,
                                LorentzianSpectrum)

class SpectrumControlWidget(QtGui.QWidget):
    '''
    Provides a BoundedFloatParameterSlider and labels for each parameter in a
    simulated spectrum.
    '''
    def __init__(self, spectrum, *args, **kwargs):
        super(SpectrumControlWidget, self).__init__(*args, **kwargs)
        controls = [BoundedFloatParameterControl(parameter=p,
                   orientation=QtCore.Qt.Horizontal)
                   for p in spectrum.parameters]
        
        self.label = self._getSpectrumLabel(spectrum)
        
        # Layout
        layout = QtGui.QVBoxLayout(self)
        grid = QtGui.QGridLayout()
        for i, (p, s) in enumerate(zip(spectrum.parameters, controls)):
            grid.addWidget(QtGui.QLabel(p.label), i, 0)
            grid.addWidget(s, i, 1)
        layout.addLayout(grid)
        layout.addStretch(1)
    
    def _getSpectrumLabel(self, spectrum):
        if isinstance(spectrum, ConstantSpectrum):
            return 'Constant'
        elif isinstance(spectrum, GaussianSpectrum):
            return 'Gaussian'
        elif isinstance(spectrum, LorentzianSpectrum):
            return 'Lorentzian'
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
    sc2 = SpectrumControlWidget(s2)
    sc3 = SpectrumControlWidget(s3)
    layout = QtGui.QVBoxLayout(w)
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