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


class LockinConfigDialog(QtGui.QDialog):
    def __init__(self, lockin, parent=None):
        super(LockinConfigDialog, self).__init__(parent)
        self.setModal(True)

        settings = QtCore.QSettings()
        timeConstantIndex = int(settings.value('lockin/time_constant_index',
                                               9))  # 300 ms default
        reserveModeIndex = int(settings.value('lockin/reserve_mode_index',
                                              0))  # High reserve default
        inputLineFilterIndex = int(settings.value('lockin/input_line_filter_index',
                                                  3))  # both filters default

        self.timeConstantComboBox = QtGui.QComboBox()
        for text in lockin.getTimeConstantLabelsList():
            self.timeConstantComboBox.addItem(text)
        self.timeConstantComboBox.setCurrentIndex(timeConstantIndex)

        self.reserveModeComboBox = QtGui.QComboBox()
        self.reserveModeComboBox.addItem('High Reserve')
        self.reserveModeComboBox.addItem('Normal')
        self.reserveModeComboBox.addItem('Low Noise (minimum)')
        self.reserveModeComboBox.setCurrentIndex(reserveModeIndex)

        self.inputLineFilterComboBox = QtGui.QComboBox()
        self.inputLineFilterComboBox.addItem('no filters')
        self.inputLineFilterComboBox.addItem('line notch filter')
        self.inputLineFilterComboBox.addItem('2x line notch filter')
        self.inputLineFilterComboBox.addItem('both notch filters')
        self.inputLineFilterComboBox.setCurrentIndex(inputLineFilterIndex)

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Time Constant', self.timeConstantComboBox)
        form.addRow('Reserve Mode', self.reserveModeComboBox)
        form.addRow('Input Line Filter', self.inputLineFilterComboBox)
        layout.addLayout(form)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect buttons
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @staticmethod
    def getLockinConfig(lockin, parent=None):
        '''
        Returns (timeConstantIndex, reserveModeIndex, inputLineFilterIndex,
        accepted), and changes the corresponding values in the settings.
        '''
        dialog = LockinConfigDialog(lockin, parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        timeConstantIndex = dialog.timeConstantComboBox.currentIndex()
        reserveModeIndex = dialog.reserveModeComboBox.currentIndex()
        inputLineFilterIndex = dialog.inputLineFilterComboBox.currentIndex()

        settings = QtCore.QSettings()
        settings.setValue('lockin/time_constant_index', timeConstantIndex)
        settings.setValue('lockin/reserve_mode_index', reserveModeIndex)
        settings.setValue('lockin/input_line_filter_index',
                          inputLineFilterIndex)
        settings.sync()

        return timeConstantIndex, reserveModeIndex, \
            inputLineFilterIndex, accepted
