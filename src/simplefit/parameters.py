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
import numpy

# local imports


class Parameter(QtCore.QObject):
    sigChanged = QtCore.Signal(QtCore.QObject)
    sigLabelChanged = QtCore.Signal(unicode)
    sigValueChanged = QtCore.Signal(object)
    def __init__(self, value=None, label=u'', stddev=None, **kwargs):
        super(Parameter, self).__init__()
        self._value = value
        self._label = label
        self._stddev = stddev
    
    def _getLabel(self):
        return self._label
    
    def _setLabel(self, label):
        self._label = label
        self.sigLabelChanged.emit(self._label)
        self.sigChanged.emit(self)
    
    label = QtCore.Property(unicode, _getLabel, _setLabel)

    def _getValue(self):
        return self._value

    def _setValue(self, value):
        self._value = value
        self.sigValueChanged.emit(self._value)
        self.sigChanged.emit(self)
        
    value = QtCore.Property(object, _getValue, _setValue)

    def _getStddev(self):
        return self._stddev

    def _setStddev(self, stddev):
        self._stddev = stddev
        self.sigValueChanged.emit(self._stddev)
        self.sigChanged.emit(self)
        
    stddev = QtCore.Property(object, _getStddev, _setStddev)


class BoundedFloatParameter(Parameter):
    sigValueChanged = QtCore.Signal(float)
    sigMinChanged = QtCore.Signal(float)
    sigMaxChanged = QtCore.Signal(float)
    
    def __init__(self, value=0., min=0., max=1., label=u'', **kwargs):
        super(BoundedFloatParameter, self).__init__(value=value,
                                                    label=label, **kwargs)
        self._min = min
        self._max = max
    
    def _getValue(self):
        return self._value

    def _setValue(self, value):
        '''
        Sets the value.
        If the given value is less than min, value is set equal to min.
        If the given value is greater than max, value is set equal to max.
        '''
        if value < self.min:
            super(BoundedFloatParameter, self)._setValue(self.min)
        elif value > self.max:
            super(BoundedFloatParameter, self)._setValue(self.max)
        else:
            super(BoundedFloatParameter, self)._setValue(value)
    
    value = QtCore.Property(float, _getValue, _setValue)

    def _getMin(self):
        return self._min

    def _setMin(self, min):
        '''
        Sets the minimum allowed value (the lower bound).
        If the given min is less than max, max is set equal to min.
        '''
        if min > self.max:
            self.max = min
        if min > self.value:
            self.value = min
        self._min = min
        self.sigMinChanged.emit(self._min)
        self.sigChanged.emit(self)
    
    min = QtCore.Property(float, _getMin, _setMin)

    def _getMax(self):
        return self._max

    def _setMax(self, max):
        '''
        Sets the maximum allowed value (the upper bound).
        If the given max is less than min, min is set equal to max.
        '''
        if max < self.min:
            self.min = max
        if max < self.value:
            self.value = max
        self._max = max
        self.sigMaxChanged.emit(self._max)
        self.sigChanged.emit(self)
    
    max = QtCore.Property(float, _getMax, _setMax)


class ArrayParameter(Parameter):
    sigValueChanged = QtCore.Signal(numpy.ndarray)

    def _getValue(self):
        return self._value

    def _setValue(self, value):
        self._value = value
        self.sigValueChanged.emit(self._value)
        self.sigChanged.emit(self)
        
    value = QtCore.Property(numpy.ndarray, _getValue, _setValue)


class HasParameter(QtCore.QObject):
    '''
    Provides subclasses with a `parameter` Qt Property of type `Parameter`
    that is automatically initialized if not provided to the constructor.
    If `parameter` is changed, or if the parameter emits it's `sigChanged`
    signal, then the `sigParameterChanged` signal is emitted.
    
    Note: this does not appear to work with multiple inheritance. In those
    situations, it's easiest to simply copy the code into the desired class.
    '''
    
    sigParameterChanged = QtCore.Signal()
    
    def _getParameter(self):
        if not hasattr(self, '_parameter'):
            self.parameter = Parameter()
        return self._parameter
    
    def _setParameter(self, parameter):
        if hasattr(self, '_parameter') and self._parameter:
            self._parameter.sigChanged.disconnect(self.sigParameterChanged)
        self._parameter = parameter
        self._parameter.sigChanged.connect(self.sigParameterChanged)
        self.sigParameterChanged.emit()
    
    parameter = QtCore.Property(Parameter, _getParameter, _setParameter)


class HasBoundedFloatParameter(HasParameter):
    '''
    Provides subclasses with a `parameter` Qt Property of type
    `BoundedFloatParameter` that is automatically initialized if not
    provided to the constructor.
    
    Note: this does not appear to work with multiple inheritance. In those
    situations, it's easiest to simply copy the code into the desired class.
    '''
    
    sigParameterChanged = QtCore.Signal()
    
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

#class ParameterReference(QtCore.QObject):
#    '''
#    Used when you want to change the parameter that a widget is linked
#    to and have the widget reflect the change.
#    '''
#    # emitted if there is a change to which parameter is being referenced,
#    # OR if the referenced parameter is changed
#    sigChanged = QtCore.Signal()
#    
#    # emitted if there is a change to which parameter is being referenced
#    sigReferenceChanged = QtCore.Signal(Parameter)
#    
#    def __init__(self, parameter):
#        self._parameter = parameter
#        self._parameter.sigChanged.connect(self.sigChanged)
#        self.sigReferenceChanged.connect(self.sigChanged)
#    
#    def __call__(self, parameter=None):
#        if parameter is not None:
#            self.set(parameter)
#        return self.get()
#    
#    def get(self):
#        return self._parameter
#    
#    def set(self, parameter):
#        self._parameter = parameter
#        self.sigReferenceChanged.emit(self._parameter)
#    
#    parameter = property(get, set)

if __name__ == '__main__':
    app = QtCore.QCoreApplication([])
    p = Parameter(value=1., label='test')
    print p, p.value, p.label
    p = Parameter(value=QtCore.QObject(), label='test')
    print p, p.value, p.label
    p = BoundedFloatParameter(value=1., min=0., max=2., label='test')
    print p, p.value, p.min, p.max, p.label
    def echo(v):
        print v
    p.sigValueChanged.connect(echo)
    p.sigMinChanged.connect(echo)
    p.sigMaxChanged.connect(echo)
    p.sigLabelChanged.connect(echo)
    p.value = 3
    p.max = 4
    p.value = 2