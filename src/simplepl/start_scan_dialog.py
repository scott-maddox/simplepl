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
from math import floor, log10

# third party imports
from PySide import QtGui, QtCore


class StartScanDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(StartScanDialog, self).__init__(parent)
        self.setModal(True)

        self._settings = QtCore.QSettings("LASE", "SimplePL")
        wlmin = float(self._settings.value('wavelength/min', 800.))
        wlmax = float(self._settings.value('wavelength/max', 5500.))
        precision = float(self._settings.value(
                                             'wavelength/precision', 0.1))
        decimals = floor(-log10(precision))
        if decimals < 0:
            decimals = 0
        start = float(self._settings.value('scan/start', wlmin))
        stop = float(self._settings.value('scan/stop', wlmax))
        step = float(self._settings.value('scan/step', 10.))
        delay = float(self._settings.value('scan/delay', 1.5))

        self.startSpinBox = QtGui.QDoubleSpinBox()
        self.startSpinBox.setDecimals(decimals)
        self.startSpinBox.setRange(wlmin, wlmax)
        self.startSpinBox.setSingleStep(precision)
        self.startSpinBox.setValue(start)

        self.stopSpinBox = QtGui.QDoubleSpinBox()
        self.stopSpinBox.setDecimals(decimals)
        self.stopSpinBox.setRange(wlmin, wlmax)
        self.stopSpinBox.setSingleStep(precision)
        self.stopSpinBox.setValue(stop)

        self.stepSpinBox = QtGui.QDoubleSpinBox()
        self.stepSpinBox.setDecimals(decimals)
        self.stepSpinBox.setRange(precision, 1000.)
        self.stepSpinBox.setSingleStep(precision)
        self.stepSpinBox.setValue(step)

        self.delaySpinBox = QtGui.QDoubleSpinBox()
        self.delaySpinBox.setDecimals(1)
        self.delaySpinBox.setRange(0., 100.)
        self.delaySpinBox.setSingleStep(.1)
        self.delaySpinBox.setValue(delay)

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Wavelength Start (nm)', self.startSpinBox)
        form.addRow('Wavelength Stop (nm)', self.stopSpinBox)
        form.addRow('Wavelength Step (nm)', self.stepSpinBox)
        form.addRow('Delay (s)', self.delaySpinBox)
        layout.addLayout(form)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect buttongs
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @staticmethod
    def getScanParameters(parent=None):
        '''
        Returns (start, stop, step, delay, accepted), and changes the
        corresponding values in the settings.
        '''
        dialog = StartScanDialog(parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        start = dialog.startSpinBox.value()
        stop = dialog.stopSpinBox.value()
        step = dialog.stepSpinBox.value()
        delay = dialog.delaySpinBox.value()

        _settings = QtCore.QSettings("LASE", "SimplePL")
        _settings.setValue('scan/start', start)
        _settings.setValue('scan/stop', stop)
        _settings.setValue('scan/step', step)
        _settings.setValue('scan/delay', delay)
        _settings.sync()

        return start, stop, step, delay, accepted
