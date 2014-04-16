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
from parameter_widgets import (BoundedFloatParameterSlider,
                               BoundedFloatParameterEdit)

class MultiParameterControl(QtGui.QWidget):
    
    def __init__(self, *args, **kwargs):
        # Extract arguments before passing to parent constructor
        if 'orientation' in kwargs:
            self._orientation = kwargs.pop('orientation')
        else:
            self._orientation = QtCore.Qt.Vertical
        
        if 'parameters' in kwargs:
            self.parameters = kwargs.pop('parameters')
            if not self.parameters:
                raise ValueError('"parameters" is empty')
        else:
            raise TypeError('missing required keyword argument "parameters"')
        
        # Call constructor
        super(MultiParameterControl, self).__init__(*args, **kwargs)
        
        self.parameterEdit = BoundedFloatParameterEdit(
                                   orientation=self._orientation,
                                   parameter=self.parameters[0])
        self.parameterSliders = []
        for parameter in self.parameters:
            slider = BoundedFloatParameterSlider(orientation=self._orientation,
                                     parameter=parameter,
                                     sharers=[self.parameterEdit])
            slider.sliderPressed.connect(slider.shareParameter)
            self.parameterSliders.append(slider)
        
        layout = QtGui.QGridLayout()
        if self._orientation == QtCore.Qt.Vertical:
            layout.addWidget(self.parameterEdit, 1, 0)
            for i, slider in enumerate(self.parameterSliders):
                layout.addWidget(slider, 1, 1+i,
                                 alignment=QtCore.Qt.AlignHCenter)
            for i, parameter in enumerate(self.parameters):
                qlabel = QtGui.QLabel(parameter.label)
                parameter.sigLabelChanged.connect(qlabel.setText)
                layout.addWidget(qlabel, 0, 1+i,
                                 alignment=QtCore.Qt.AlignHCenter)
        else: # Horizontal
            layout.addWidget(self.parameterEdit, 0, 1)
            for i, slider in enumerate(self.parameterSliders):
                layout.addWidget(slider, 1+i, 1,
                                 alignment=QtCore.Qt.AlignVCenter)
            for i, parameter in enumerate(self.parameters):
                qlabel = QtGui.QLabel(parameter.label)
                parameter.sigLabelChanged.connect(qlabel.setText)
                layout.addWidget(qlabel, 1+i, 0,
                                 alignment=QtCore.Qt.AlignVCenter)
        self.setLayout(layout)
    
    def _getParameter(self):
        return super(MultiParameterControl, self)._getParameter()
    
    def _setParameter(self, p):
        super(MultiParameterControl, self)._setParameter(p)
        self.parameterSlider.parameter = self.parameter
        self.parameterEdit.parameter = self.parameter
    
    parameter = property(_getParameter, _setParameter)
 
    def _handleParameterChanged(self):
        pass

if __name__ == '__main__':
    from parameter import FloatParameter
    app = QtGui.QApplication([])
    ps = [FloatParameter(str(i)*10) for i in xrange(5)]
    w1 = MultiParameterControl(parameters=ps, orientation=QtCore.Qt.Vertical)
    w1.show()
    #ps[0].label = 0
    w2 = MultiParameterControl(parameters=ps, orientation=QtCore.Qt.Horizontal)
    w2.show()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()