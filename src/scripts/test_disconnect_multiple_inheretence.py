from PySide import QtCore

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

class Parent2(QtCore.QObject):
    pass

class Child(Parent, Parent2):
    def __init__(self, s, *args, **kwargs):
        Parent.__init__(self, s)
        Parent2.__init__(self, *args, **kwargs)

    def f(self):
        print 'child'

s = Sig()
p = Parent(s)
c = Child(s)
s.sig.emit()

p._disconnect()
c._disconnect()
s.sig.emit()