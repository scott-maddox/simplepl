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

# std lib imports
import sys

# third party imports
from PySide import QtGui, QtCore


class ConfigInstrumentsDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(ConfigInstrumentsDialog, self).__init__(parent)
        self.setModal(True)

        settings = QtCore.QSettings()
        autoConnect = bool(settings.value('autoConnect'))
        lockinPort = settings.value('lockin/port', 'GPIB::8')
        spectrometerPort = int(settings.value('spectrometer/port', 3))
        filterWheelPort = int(settings.value('filterWheel/port', 3))

        self.autoConnectCheckBox = QtGui.QCheckBox()
        if autoConnect:
            self.autoConnectCheckBox.setCheckState(QtCore.Qt.Checked)
        self.lockinPortLineEdit = QtGui.QLineEdit()
        self.lockinPortLineEdit.setText(lockinPort)
        self.spectrometerPortSpinBox = QtGui.QSpinBox()
        self.spectrometerPortSpinBox.setValue(spectrometerPort)
        self.filterWheelPortSpinBox = QtGui.QSpinBox()
        self.filterWheelPortSpinBox.setValue(filterWheelPort)
        connectButton = QtGui.QPushButton('Connect')
        cancelButton = QtGui.QPushButton('Cancel')

        # Layout
        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Auto connect on startup', self.autoConnectCheckBox)
        form.addRow('Lock-in Port', self.lockinPortLineEdit)
        form.addRow('Spectrometer Port', self.spectrometerPortSpinBox)
        form.addRow('Filter Wheel Port', self.filterWheelPortSpinBox)
        layout.addLayout(form)

        # OK and Cancel buttons
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
        if sys.platform == 'darwin':
            buttonsLayout.addWidget(cancelButton)
            buttonsLayout.addWidget(connectButton)
        else:
            buttonsLayout.addWidget(connectButton)
            buttonsLayout.addWidget(cancelButton)
        layout.addLayout(buttonsLayout)

        # Connect buttons
        connectButton.clicked.connect(self.accept)
        cancelButton.clicked.connect(self.reject)

    @classmethod
    def getConfig(cls, parent=None):
        '''
        If accepted, returns (autoConnect, lockinPort, spectrometerPort,
        filterWheelPort), and changes the corresponding values in the
        settings. Otherwise, returns None.
        '''
        dialog = cls(parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        if not accepted:
            return

        autoConnect = dialog.autoConnectCheckBox.checkState()
        lockinPort = dialog.lockinPortLineEdit.text()
        spectrometerPort = dialog.spectrometerPortSpinBox.value()
        filterWheelPort = dialog.filterWheelPortSpinBox.value()

        settings = QtCore.QSettings()
        settings.setValue('autoConnect', autoConnect)
        settings.setValue('lockin/port', lockinPort)
        settings.setValue('spectrometer/port', spectrometerPort)
        settings.setValue('filterWheel/port', filterWheelPort)
        settings.sync()

        return autoConnect, lockinPort, spectrometerPort, filterWheelPort

if __name__ == '__main__':
    app = QtGui.QApplication([])
    ConfigInstrumentsDialog().exec_()
