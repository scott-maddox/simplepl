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
from parameters import BoundedFloatParameter

class ParameterLinked(object):
    
    def __init__(self, *args, **kwargs):
        if 'parameter' in kwargs:
            parameter = kwargs.pop('parameter')
            super(ParameterLinked, self).__init__(*args, **kwargs)
        elif len(args):
            parameter = args[0]
            super(ParameterLinked, self).__init__(*args[1:], **kwargs)
        
        assert isinstance(parameter, BoundedFloatParameter)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self._handleParameterChanged)
    
    def _getEnergy(self):
        return self._parameter
    
    def _setEnergy(self, parameter):
        assert isinstance(parameter, BoundedFloatParameter)
        self._parameter.sigChanged.disconnect(self._handleParameterChanged)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self._handleParameterChanged)
        self._handleParameterChanged()
    
    parameter = property(_getEnergy, _setEnergy)
 
    def _handleParameterChanged(self):
        raise NotImplementedError()

class ParameterSharer(ParameterLinked):
    '''
    Has a list of objects that it shares it's parameter with when it gains
    focus.
    '''
    def __init__(self, *args, **kwargs):
        if 'sharers' in kwargs:
            self.sharers = kwargs.pop('sharers')
        super(ParameterSharer, self).__init__(*args, **kwargs)
    
    def shareParameter(self):
        for sharer in self.sharers:
            sharer.parameter = self.parameter

class BoundedFloatParameterSlider(ParameterSharer, QtGui.QSlider):
    def __init__(self, *args, **kwargs):
        self._ignoreParameterChanged = False
        super(BoundedFloatParameterSlider, self).__init__(*args, **kwargs)
        self.setMaximum(1000)
        
        self.valueChanged.connect(self._handleSliderChanged)
        self._handleParameterChanged() # initialize the slider position
    
    @QtCore.Slot(int)
    def _handleSliderChanged(self, pos):
        pos_min = self.minimum()
        pos_range = self.maximum() - pos_min
        value_min = self._parameter.min
        value_range = self._parameter.max - value_min
        
        pos_frac = float(pos - pos_min) / pos_range
        value = pos_frac * value_range + value_min
        
        self._ignoreParameterChanged = True
        self._parameter.value = value
        self._ignoreParameterChanged = False
 
    def _handleParameterChanged(self):
        if self._ignoreParameterChanged:
            return # prevent callback loops
        
        pos_min = self.minimum()
        pos_range = self.maximum() - pos_min
        value_min = self._parameter.min
        value_range = self._parameter.max - value_min
        if value_range == 0:
            self.setSliderPosition(0)
            return
        
        value_frac = float(self._parameter.value - value_min) / value_range
        pos = value_frac * pos_range + pos_min
        self.setSliderPosition(int(pos + 0.5))

class BoundedFloatParameterEdit(ParameterLinked, QtGui.QWidget):

    def __init__(self, format='%G', *args, **kwargs):
        # Extract arguments before passing to parent constructor
        if 'format' in kwargs:
            self.format = kwargs.pop('format')
        else:
            self.format = '%G'
        
        if '_orientation' in kwargs:
            self._orientation = kwargs.pop('_orientation')
        else:
            self._orientation = QtCore.Qt.Vertical
        
        # Call constructor
        super(BoundedFloatParameterEdit, self).__init__(*args, **kwargs)
        
        # Instantiate widgets
        self.valueLabel = QtGui.QLabel('Value')
        self.minLabel = QtGui.QLabel('Min')
        self.maxLabel = QtGui.QLabel('Max')
        
        self.valueEdit = QtGui.QLineEdit()
        self.minEdit = QtGui.QLineEdit()
        self.maxEdit = QtGui.QLineEdit()
        
        self.valueEdit.setMinimumWidth(70)
        self.minEdit.setMinimumWidth(70)
        self.maxEdit.setMinimumWidth(70)
        
        self.valueEdit.setValidator(QtGui.QDoubleValidator())
        self.minEdit.setValidator(QtGui.QDoubleValidator())
        self.maxEdit.setValidator(QtGui.QDoubleValidator())
        
        # Layout
        layout = QtGui.QGridLayout()
        if self._orientation == QtCore.Qt.Vertical:
            layout.addWidget(self.maxLabel, 0, 0, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.maxEdit, 0, 1, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.valueLabel, 1, 0, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.valueEdit, 1, 1, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.minLabel, 2, 0, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.minEdit, 2, 1, alignment=QtCore.Qt.AlignCenter)
        else:
            layout.addWidget(self.minLabel, 0, 0, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.minEdit, 1, 0, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.valueLabel, 0, 1, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.valueEdit, 1, 1, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.maxLabel, 0, 2, alignment=QtCore.Qt.AlignCenter)
            layout.addWidget(self.maxEdit, 1, 2, alignment=QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        
        # Connect signals and slots
        self.valueEdit.editingFinished.connect(self._handleValueChanged)
        self.minEdit.editingFinished.connect(self._handleMinChanged)
        self.maxEdit.editingFinished.connect(self._handleMaxChanged)
        
        # Initialize values
        self._handleParameterChanged()

    @QtCore.Slot()
    def _handleValueChanged(self):
        self._parameter.value = float(self.valueEdit.text())
 
    @QtCore.Slot()
    def _handleMinChanged(self):
        self._parameter.min = float(self.minEdit.text())
 
    @QtCore.Slot()
    def _handleMaxChanged(self):
        self._parameter.max = float(self.maxEdit.text())
 
    def _handleParameterChanged(self):
        self.valueEdit.setText(self.format%self._parameter.value)
        self.minEdit.setText(self.format%self._parameter.min)
        self.maxEdit.setText(self.format%self._parameter.max)

class SingleParameterControl(ParameterLinked, QtGui.QWidget):
    
    def __init__(self, *args, **kwargs):
        # Extract arguments before passing to parent constructor
        if '_orientation' in kwargs:
            self._orientation = kwargs.pop('_orientation')
        else:
            self._orientation = QtCore.Qt.Vertical
        
        # Call constructor
        super(SingleParameterControl, self).__init__(*args, **kwargs)
        
        self.parameterSlider = BoundedFloatParameterSlider(
                                   orientation=self._orientation,
                                   parameter=self.parameter)
        self.parameterEdit = BoundedFloatParameterEdit(
                                   orientation=self._orientation,
                                   parameter=self.parameter)
        
        if self._orientation == QtCore.Qt.Vertical:
            layout = QtGui.QHBoxLayout()
        else:
            layout = QtGui.QVBoxLayout()
        layout.addWidget(self.parameterEdit)
        layout.addWidget(self.parameterSlider)
        layout.addStretch()
        self.setLayout(layout)
    
    def _getEnergy(self):
        return super(SingleParameterControl, self)._getEnergy()
    
    def _setEnergy(self, p):
        super(SingleParameterControl, self)._setEnergy(p)
        self.parameterSlider.parameter = self.parameter
        self.parameterEdit.parameter = self.parameter
    
    parameter = property(_getEnergy, _setEnergy)
 
    def _handleParameterChanged(self):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    p1 = BoundedFloatParameter()
    p2 = BoundedFloatParameter()
    w1 = SingleParameterControl(parameter=p1, orientation=QtCore.Qt.Horizontal)
    w2 = SingleParameterControl(parameter=p1)
    b = QtGui.QPushButton('Split Parameters')
    def changeParameters():
        w1.parameter = p2
        print "Parameters split."
    b.clicked.connect(changeParameters)

    layout = QtGui.QHBoxLayout()
    layout.addWidget(w1)
    layout.addWidget(w2)
    layout.addWidget(b)
    w.setLayout(layout)
    w.show()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()