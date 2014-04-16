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

# local imports

class Sig(QtCore.QObject):
    sig = QtCore.Signal()

class Parent(object):
    def __init__(self, s):
        self._s = s
        self._s.sig.connect(self.f)
    
    def f(self):
        print 'parent'
    
    def _disconnect(self):
        print 'disconnecting'
        self._s.sig.disconnect(self.f)

class Child(Parent):
    def __init__(self, s):
        Parent.__init__(self, s)

    def f(self):
        print 'child'

s = Sig()
p = Parent(s)
c = Child(s)
s.sig.emit()

p._disconnect()
c._disconnect()
s.sig.emit()