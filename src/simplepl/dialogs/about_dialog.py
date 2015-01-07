#
#   Copyright (c) 2013-2014, Scott J Maddox
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

# local imports
from ..version import __version__


class AboutDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setModal(True)
        
        label = QtGui.QLabel(
            '''
            SimplePL<br>
            Version {}
            <p>
            Copyright (c) 2013-2014, Scott J Maddox
            </p>
            <p>
            A simple python gui for taking photoluminescence (PL) spectra.
            </p>
            <p>
            The <a href="http://github.com/scott-maddox/simplepl">source
            code</a> and <a href="http://scott-maddox.github.io/simplepl">
            documentation (coming soon)</a> are graciously hosted by GitHub.
            </p>
            <p>
            SimplePL is free software: you can redistribute it and/or modify
            it under the terms of the GNU Affero General Public License as
            published by the Free Software Foundation, either version 3 of the
            License, or (at your option) any later version.
            </p>
            <p>
            SimplePL is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
            GNU Affero General Public License for more details.
            </p>
            <p>
            You should have received a copy of the GNU Affero General Public
            License along with SimplePL.  If not, see
            <a href="http://www.gnu.org/licenses/">
            http://www.gnu.org/licenses/</a>.
            </p>
            '''.format(__version__))
        label.setTextFormat(QtCore.Qt.RichText)
        label.setWordWrap(True)
        label.setOpenExternalLinks(True)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(label)

        # OK button
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)
        
        # Connect buttons
        self.buttons.accepted.connect(self.accept)
