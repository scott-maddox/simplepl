#
#   Copyright (c) 2013-2014, Scott J Maddox
#
#   This file is part of Semicontrol.
#
#   Semicontrol is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   Semicontrol is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with Semicontrol.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#########################################################################

# third party imports
from PySide import QtCore, QtGui

if __name__ == '__main__':
    app = QtGui.QApplication([])

logoIcon = QtGui.QIcon()
for i in [16, 32, 64, 128, 256, 512, 1024]:
    logoIcon.addFile('icon_{}.png'.format(i), QtCore.QSize(i, i))

if __name__ == '__main__':
    win = QtGui.QMainWindow()
    l = QtGui.QLabel()
    p = logoIcon.pixmap(256, 256)
    l.setPixmap(p)
    win.setCentralWidget(l)
    win.show()
    win.raise_()
    app.exec_()
