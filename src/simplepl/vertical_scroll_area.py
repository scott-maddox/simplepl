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
#   License along with SimplePL.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#######################################################################

# third party imports
from PySide import QtGui, QtCore


class VerticalScrollArea(QtGui.QScrollArea):
    def __init__(self, *args, **kwargs):
        super(VerticalScrollArea, self).__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

    def eventFilter(self, o, e):
        # This works because QScrollArea::setWidget installs an eventFilter
        # on the widget
        if o and o is self.widget() and isinstance(e, QtGui.QResizeEvent):
            self.setMinimumWidth(self.widget().minimumSizeHint().width() +
                                 self.verticalScrollBar().width())

        return super(VerticalScrollArea, self).eventFilter(o, e)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    layout = QtGui.QVBoxLayout(w)
    hbox = QtGui.QHBoxLayout()
    hbox.addWidget(QtGui.QLabel('test'))
    hbox.addStretch(1)
    hbox.addWidget(QtGui.QLabel('test'))
    layout.addLayout(hbox)
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addWidget(QtGui.QLabel('test'))
    layout.addStretch(1)
    # w.show()
    # w.raise_()
    scroll = VerticalScrollArea()
    scroll.setWidget(w)
    scroll.show()
    scroll.raise_()

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
