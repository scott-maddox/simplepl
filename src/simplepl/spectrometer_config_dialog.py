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


class SpectrometerConfigDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SpectrometerConfigDialog, self).__init__(parent)
        self.setModal(True)

        settings = QtCore.QSettings()
        entranceMirror = settings.value('spectrometer/entrance_mirror',
                                        'Front')
        exitMirror = settings.value('spectrometer/exit_mirror',
                                    'Side')

        self.entranceMirrorComboBox = QtGui.QComboBox()
        self.entranceMirrorComboBox.addItem('Front')
        self.entranceMirrorComboBox.addItem('Side')
        if entranceMirror == 'Front':
            self.entranceMirrorComboBox.setCurrentIndex(0)
        else:
            self.entranceMirrorComboBox.setCurrentIndex(1)

        self.exitMirrorComboBox = QtGui.QComboBox()
        self.exitMirrorComboBox.addItem('Front')
        self.exitMirrorComboBox.addItem('Side')
        if exitMirror == 'Front':
            self.exitMirrorComboBox.setCurrentIndex(0)
        else:
            self.exitMirrorComboBox.setCurrentIndex(1)

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Entrance Mirror', self.entranceMirrorComboBox)
        form.addRow('Exit Mirror', self.exitMirrorComboBox)
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
    def getSpectrometerConfig(parent=None):
        '''
        Returns (entranceMirror, exitMirror, accepted), and changes the
        corresponding values in the settings.
        '''
        dialog = SpectrometerConfigDialog(parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        entranceMirror = dialog.entranceMirrorComboBox.currentText()
        exitMirror = dialog.exitMirrorComboBox.currentText()

        settings = QtCore.QSettings()
        settings.setValue('spectrometer/entrance_mirror',
                                        entranceMirror)
        settings.setValue('spectrometer/exit_mirror',
                                    exitMirror)
        settings.sync()

        return entranceMirror, exitMirror, accepted
