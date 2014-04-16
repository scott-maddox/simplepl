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

# I would like to use multiple inheritence here and just inherit
# from HasBoundedFloatParameter, but it causes python to crash.
# Thus, I'm copy/pasting the code.
class BoundedFloatParameterSlider(QtGui.QSlider):
    '''
    A BoundedFloatParameter slider for changing the value anywhere from
    min to max.
    '''
    sigSliderMoved = QtCore.Signal(QtGui.QSlider)
    sigParameterChanged = QtCore.Signal(QtCore.QObject)
    #sigFocusIn = QtCore.Signal()
    #sigFocusOut = QtCore.Signal()
    
    def __init__(self, *args, **kwargs):
        super(BoundedFloatParameterSlider, self).__init__(*args, **kwargs)
        
        # Initialize the slider
        self.setMaximum(1000) # increase the default precision
        self.setTracking(True) # enable tracking by default
        self.sliderMoved.connect(self._emitSigSliderMoved)
        self._handleParameterChanged() # initialize the slider position
        if self.orientation() == QtCore.Qt.Vertical:
            self.setMinimumHeight(100)
        else:
            self.setMinimumWidth(100)
        
        # enable receiving click and keyboard focus
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Connect signals and slots
        self.valueChanged.connect(self._handleSliderChanged)
        self.sigParameterChanged.connect(self._handleParameterChanged)
    
    def _emitSigSliderMoved(self):
        self.sigSliderMoved.emit(self)

    def wheelEvent(self, e):
        e.ignore()
    
#    def focusOutEvent(self, e):
#        self.sigFocusOut.emit()
#    
#    def focusInEvent(self, e):
#        self.sigFocusIn.emit()
    
    def _getParameter(self):
        if not hasattr(self, '_parameter'):
            self.parameter = BoundedFloatParameter()
        return self._parameter
    
    def _setParameter(self, parameter):
        if hasattr(self, '_parameter') and self._parameter:
            self._parameter.sigChanged.disconnect(self.sigParameterChanged)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self.sigParameterChanged)
        self.sigParameterChanged.emit(self._parameter)
    
    parameter = QtCore.Property(BoundedFloatParameter,
                                _getParameter, _setParameter)
    
    @QtCore.Slot(int)
    def _handleSliderChanged(self, pos):
        pos_min = self.minimum()
        pos_range = self.maximum() - pos_min
        value_min = self.parameter.min
        value_range = self.parameter.max - value_min
        
        pos_frac = float(pos - pos_min) / pos_range
        value = pos_frac * value_range + value_min
        
        # prevent signal loops by disconnecting and reconnecting
        self.sigParameterChanged.disconnect(self._handleParameterChanged)
        self.parameter.value = value
        self.sigParameterChanged.connect(self._handleParameterChanged)
 
    def _handleParameterChanged(self):
        pos_min = self.minimum()
        pos_range = self.maximum() - pos_min
        value_min = self.parameter.min
        value_range = self.parameter.max - value_min
        if value_range == 0:
            self.setSliderPosition(0)
            return
        
        value_frac = float(self.parameter.value - value_min) / value_range
        pos = value_frac * pos_range + pos_min
        self.setSliderPosition(int(pos + 0.5))

class FloatEdit(QtGui.QLineEdit):
    
    def __init__(self, format='%G', *args, **kwargs):
        super(FloatEdit, self).__init__(*args, **kwargs)
        self.setMinimumWidth(70)

class BoundedFloatParameterEdit(QtGui.QWidget):
    '''
    A BoundedFloatParameter editor.
    Has a labeled QLineEdit for each of value, min, and max.
    '''
    
    sigParameterChanged = QtCore.Signal()

    def __init__(self, orientation=QtCore.Qt.Vertical, format='%G',
                 *args, **kwargs):
        super(BoundedFloatParameterEdit, self).__init__(*args, **kwargs)
        self._orientation = orientation
        self.format = format
        
        # Instantiate widgets
        self.valueLabel = QtGui.QLabel('Value')
        self.minLabel = QtGui.QLabel('Min')
        self.maxLabel = QtGui.QLabel('Max')
        
        self.valueEdit = FloatEdit(format=format)
        self.minEdit = FloatEdit(format=format)
        self.maxEdit = FloatEdit(format=format)
        
        self.valueEdit.setValidator(QtGui.QDoubleValidator())
        self.minEdit.setValidator(QtGui.QDoubleValidator())
        self.maxEdit.setValidator(QtGui.QDoubleValidator())
        
        # Initialize values
        self._handleParameterChanged()
        
        # Layout
        layout = QtGui.QGridLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        align = QtCore.Qt.AlignCenter
        if self._orientation == QtCore.Qt.Vertical:
            layout.addWidget(self.maxLabel, 0, 0, alignment=align)
            layout.addWidget(self.maxEdit, 0, 1, alignment=align)
            layout.addWidget(self.valueLabel, 1, 0, alignment=align)
            layout.addWidget(self.valueEdit, 1, 1, alignment=align)
            layout.addWidget(self.minLabel, 2, 0, alignment=align)
            layout.addWidget(self.minEdit, 2, 1, alignment=align)
        else:
            layout.addWidget(self.minLabel, 0, 0, alignment=align)
            layout.addWidget(self.minEdit, 1, 0, alignment=align)
            layout.addWidget(self.valueLabel, 0, 1, alignment=align)
            layout.addWidget(self.valueEdit, 1, 1, alignment=align)
            layout.addWidget(self.maxLabel, 0, 2, alignment=align)
            layout.addWidget(self.maxEdit, 1, 2, alignment=align)
        self.setLayout(layout)
        
        # Connect signals and slots
        self.sigParameterChanged.connect(self._handleParameterChanged)
        self.valueEdit.editingFinished.connect(self._handleValueChanged)
        self.minEdit.editingFinished.connect(self._handleMinChanged)
        self.maxEdit.editingFinished.connect(self._handleMaxChanged)
    
    def _getParameter(self):
        if not hasattr(self, '_parameter'):
            self.parameter = BoundedFloatParameter()
        return self._parameter
    
    def _setParameter(self, parameter):
        if hasattr(self, '_parameter') and self._parameter:
            self._parameter.sigChanged.disconnect(self.sigParameterChanged)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self.sigParameterChanged)
        self.sigParameterChanged.emit()
    
    parameter = QtCore.Property(BoundedFloatParameter,
                                _getParameter, _setParameter)

    @QtCore.Slot()
    def _handleValueChanged(self):
        self.parameter.value = float(self.valueEdit.text())
 
    @QtCore.Slot()
    def _handleMinChanged(self):
        self.parameter.min = float(self.minEdit.text())
 
    @QtCore.Slot()
    def _handleMaxChanged(self):
        self.parameter.max = float(self.maxEdit.text())
 
    @QtCore.Slot()
    def _handleParameterChanged(self):
        self.valueEdit.setText(self.format%self.parameter.value)
        self.minEdit.setText(self.format%self.parameter.min)
        self.maxEdit.setText(self.format%self.parameter.max)

class BoundedFloatParameterControl(QtGui.QWidget):
    
    sigParameterChanged = QtCore.Signal()

    def __init__(self, orientation=QtCore.Qt.Vertical, format='%G',
                 *args, **kwargs):
        if 'parameter' in kwargs:
            self._parameter = kwargs.pop('parameter')
        else:
            self._parameter = BoundedFloatParameter()
        super(BoundedFloatParameterControl, self).__init__(*args, **kwargs)
        self._orientation = orientation
        self.format = format
        edit = BoundedFloatParameterEdit(parameter=self.parameter,
                                         orientation=self._orientation)
        #edit.hide() # start hidden
        slider = BoundedFloatParameterSlider(parameter=self.parameter,
                                         orientation=self._orientation)
        
        # Layout
        if self._orientation == QtCore.Qt.Vertical:
            layout = QtGui.QHBoxLayout(self)
        else:
            layout = QtGui.QVBoxLayout(self)
        layout.addWidget(edit)
        layout.addWidget(slider)
        
        # Connect signals and slots
        #slider.sigFocusIn.connect(edit.show)
        #slider.sigFocusOut.connect(edit.hide)
        self._parameter.sigChanged.connect(self.sigParameterChanged)
    
    def _getParameter(self):
        if not hasattr(self, '_parameter'):
            self.parameter = BoundedFloatParameter()
        return self._parameter
    
    def _setParameter(self, parameter):
        if hasattr(self, '_parameter') and self._parameter:
            self._parameter.sigChanged.disconnect(self.sigParameterChanged)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self.sigParameterChanged)
        self.sigParameterChanged.emit()
    
    parameter = QtCore.Property(BoundedFloatParameter,
                                _getParameter, _setParameter)

if __name__ == '__main__':
    from parameters import BoundedFloatParameter
    app = QtGui.QApplication([])
#    p = BoundedFloatParameter()
#    w = QtGui.QWidget()
#    s1 = BoundedFloatParameterSlider(parameter=p)
#    e1 = BoundedFloatParameterEdit(parameter=p)
#    
#    s2 = BoundedFloatParameterSlider(parameter=p,
#                                     orientation=QtCore.Qt.Horizontal)
#    e2 = BoundedFloatParameterEdit(parameter=p,
#                                   orientation=QtCore.Qt.Horizontal)
#    b = QtGui.QPushButton('Split Parameters')
#    def changeParameters():
#        p = BoundedFloatParameter()
#        s1.parameter = p
#        e1.parameter = p
#        print "Parameters split."
#    b.clicked.connect(changeParameters)
#
#    layout = QtGui.QHBoxLayout()
#    box1 = QtGui.QHBoxLayout()
#    box1.addWidget(s1)
#    box1.addWidget(e1)
#    box2 = QtGui.QVBoxLayout()
#    box2.addWidget(s2)
#    box2.addWidget(e2)
#    layout.addLayout(box1)
#    layout.addLayout(box2)
#    layout.addWidget(b)
#    w.setLayout(layout)
#    w.show()
#    w.raise_()
    w = QtGui.QWidget()
    layout = QtGui.QHBoxLayout(w)
    layout.addWidget(BoundedFloatParameterControl())
    layout.addWidget(BoundedFloatParameterControl(
                                orientation=QtCore.Qt.Horizontal))
    w.show()
    w.raise_()
    
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()