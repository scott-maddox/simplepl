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

# third party imports
from PySide import QtGui, QtCore


class PortsConfigDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(PortsConfigDialog, self).__init__(parent)
        self.setModal(True)

        settings = QtCore.QSettings()
        lockinPort = settings.value('lockin/port', 'GPIB::8')
        spectrometerPort = int(settings.value('spectrometer/port', 3))
        filterWheelPort = int(settings.value('filterWheel/port', 3))

        self.lockinPortLineEdit = QtGui.QLineEdit()
        self.lockinPortLineEdit.setText(lockinPort)
        self.spectrometerPortSpinBox = QtGui.QSpinBox()
        self.spectrometerPortSpinBox.setValue(spectrometerPort)
        self.filterWheelPortSpinBox = QtGui.QSpinBox()
        self.filterWheelPortSpinBox.setValue(filterWheelPort)

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Lock-in Port', self.lockinPortLineEdit)
        form.addRow('Spectrometer Port', self.spectrometerPortSpinBox)
        form.addRow('Filter Wheel Port', self.filterWheelPortSpinBox)
        layout.addLayout(form)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect buttons
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @classmethod
    def getPortsConfig(cls, parent=None):
        '''
        If accepted, returns (lockinPort, spectrometerPort, filterWheelPort),
        and changes the corresponding values in the settings. Otherwise,
        returns None.
        '''
        dialog = cls(parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        if not accepted:
            return

        lockinPort = dialog.lockinPortLineEdit.text()
        spectrometerPort = dialog.spectrometerPortSpinBox.value()
        filterWheelPort = dialog.filterWheelPortSpinBox.value()

        settings = QtCore.QSettings()
        settings.setValue('lockin/port', lockinPort)
        settings.setValue('spectrometer/port', spectrometerPort)
        settings.setValue('filterWheel/port', filterWheelPort)
        settings.sync()

        return lockinPort, spectrometerPort, filterWheelPort
