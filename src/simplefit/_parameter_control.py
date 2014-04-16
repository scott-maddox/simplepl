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

#class ResettingParameterSlider(QtGui.QSlider):
#    def __init__(self, parameter):
#        super(ResettingParameterSlider, self).__init__()
#        assert isinstance(parameter, BoundedFloatParameter)
#        self._parameter = parameter
#        self._state = 'center'
#        self._value = None
#        
#        self.slider = QtGui.QSlider(QtCore.Qt.Vertical)
#        self.slider.setTickPosition(QtGui.QSlider.TicksLeft)
#        self.slider.setTickInterval(100)
#        
#        self.slider.sliderPressed.connect(self._pressed)
#        self.slider.sliderMoved.connect(self._moved)
#        self.slider.sliderReleased.connect(self._released)
#    
#    @QtCore.Slot()
#    def _pressed(self):
#        self._value = self._parameter.value
#    
#    @QtCore.Slot()
#    def _released(self):
#        if self._parameter.value == self._parameter.min:
#            self._state = 'min'
#            self.slider.setRange(0, 400)
#            self.slider.setValue(0)
#        elif self._parameter.value == self._parameter.max:
#            self._state = 'max'
#            self.slider.setRange(0, 400)
#            self.slider.setValue(400)
#        else:
#            self._state = 'center'
#            self.slider.setRange(-200, 200)
#            self.slider.setValue(0)
#    
#    @QtCore.Slot(int)
#    def _moved(self, pos):
#        if not self.isSliderDown():
#            # _parameter.pos was changed directly. Update the slider view
#            # and then return.
#            self._released()
#            return
#        
#        max = self._parameter.max
#        min = self._parameter.min
#        range = max - min
#        if self.state == 'min' or self.state == 'max':
#            self._parameter.value = range / 400. * pos + min
#        elif self.state == 'max':
#            self._parameter.value = range / 400. * pos + min
#        else:
#            if pos == 0:
#                self._parameter.value = self._value
#            elif pos > 0:
#                if pos <= 100:
#                    self._parameter.value *= self._value * pos / 100.
#            elif pos < 0:
#                if pos >= -100:
#                    self._parameter.value *= self._value * pos / 100.

class AbstractParameterLinkedObject(object):
    
    def __init__(self, parameter):
        assert isinstance(parameter, BoundedFloatParameter)
        self._parameter = parameter
        self._connect()
    
    def _connect(self):
        self._parameter.sigChanged.connect(self._handleParameterChanged)
    
    def _disconnect(self):
        self._parameter.sigChanged.disconnect(self._handleParameterChanged)
    
    def _getParameter(self):
        return self._parameter
    
    def _setParameter(self, parameter):
        assert isinstance(parameter, BoundedFloatParameter)
        self._disconnect()
        self._parameter = parameter
        self._connect()
        self._handleParameterChanged()
    
    parameter = property(_getParameter, _setParameter)
 
    def _handleParameterChanged(self):
        raise NotImplementedError()

class BoundedFloatParameterSlider(AbstractParameterLinkedObject, QtGui.QSlider):
    def __init__(self, parameter, *args, **kwargs):
        self._ignoreParameterChanged = False
        AbstractParameterLinkedObject.__init__(self, parameter)
        QtGui.QSlider.__init__(self, *args, **kwargs)
        
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

class BoundedFloatParameterEdit(AbstractParameterLinkedObject, QtGui.QWidget):
    def __init__(self, parameter, format='%G'):
        AbstractParameterLinkedObject.__init__(self, parameter)
        QtGui.QWidget.__init__(self)
        self.format = format
        
        self.valueEdit = QtGui.QLineEdit()
        self.minEdit = QtGui.QLineEdit()
        self.maxEdit = QtGui.QLineEdit()
        
        self.valueEdit.setValidator(QtGui.QDoubleValidator())
        self.minEdit.setValidator(QtGui.QDoubleValidator())
        self.maxEdit.setValidator(QtGui.QDoubleValidator())
        
        layout = QtGui.QFormLayout()
        layout.addRow('Max', self.maxEdit)
        layout.addRow('Value', self.valueEdit)
        layout.addRow('Min', self.minEdit)
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

class SingleParameterControl(AbstractParameterLinkedObject, QtGui.QWidget):
    
    def __init__(self, parameter):
        AbstractParameterLinkedObject.__init__(self, parameter)
        QtGui.QWidget.__init__(self)
        
        self.parameterSlider = BoundedFloatParameterSlider(parameter, QtCore.Qt.Vertical)
        self.parameterEdit = BoundedFloatParameterEdit(parameter)
        #self.parameterSlider.setTickPosition(QtGui.QSlider.TicksLeft)
        #self.parameterSlider.setRange(0, 1000)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.parameterSlider)
        layout.addWidget(self.parameterEdit)
        self.setLayout(layout)
    
    def _setParameter(self, p):
        super(SingleParameterControl, self)._setParameter(p)
        self.parameterSlider.parameter = self.parameter
        self.parameterEdit = self.parameter
 
    def _handleParameterChanged(self):
        pass

if __name__ == '__main__':
    app = QtGui.QApplication([])
    p1 = BoundedFloatParameter()
    p2 = BoundedFloatParameter()
    w = SingleParameterControl(p1)
    w.parameter = p2
    w.show()
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()