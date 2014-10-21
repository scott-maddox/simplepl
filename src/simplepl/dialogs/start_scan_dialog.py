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
from ..wavelength_spin_box import WavelengthSpinBox


class StartScanDialog(QtGui.QDialog):
    def __init__(self, spectrometer, parent=None):
        super(StartScanDialog, self).__init__(parent)
        self.setModal(True)

        minWavelength = spectrometer.getMinWavelength()
        maxWavelength = spectrometer.getMaxWavelength()

        settings = QtCore.QSettings()
        start = float(settings.value('scan/start', minWavelength))
        stop = float(settings.value('scan/stop', maxWavelength))
        step = float(settings.value('scan/step', 10.))
        delay = float(settings.value('scan/delay', 1.5))

        self.startSpinBox = WavelengthSpinBox(value=start)
        self.startSpinBox.setRange(minWavelength, maxWavelength)
        self.stopSpinBox = WavelengthSpinBox(value=stop)
        self.stopSpinBox.setRange(minWavelength, maxWavelength)
        self.startSpinBox.selectAll()

        self.stepSpinBox = WavelengthSpinBox(value=step)
        self.stepSpinBox.setRange(self.stepSpinBox.getPrecision(),
                                  self.stepSpinBox.getMaxWavelength())

        self.delaySpinBox = QtGui.QDoubleSpinBox()
        self.delaySpinBox.setDecimals(1)
        self.delaySpinBox.setRange(0., 100.)
        self.delaySpinBox.setSingleStep(.1)
        self.delaySpinBox.setValue(delay)

        self.timeEstimateLabel = QtGui.QLabel('')
        self._updateTimeEstimate()

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Wavelength Start ({})'
                    ''.format(self.startSpinBox.getUnits()),
                    self.startSpinBox)
        form.addRow('Wavelength Stop ({})'
                    ''.format(self.stopSpinBox.getUnits()),
                    self.stopSpinBox)
        form.addRow('Wavelength Step ({})'
                    ''.format(self.stepSpinBox.getUnits()),
                    self.stepSpinBox)
        form.addRow('Delay (s)', self.delaySpinBox)
        form.addRow('Minimum Scan Time:', self.timeEstimateLabel)
        layout.addLayout(form)

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        layout.addWidget(self.buttons)

        # Connect signals and slots
        self.startSpinBox.valueChanged.connect(self._updateTimeEstimate)
        self.stopSpinBox.valueChanged.connect(self._updateTimeEstimate)
        self.stepSpinBox.valueChanged.connect(self._updateTimeEstimate)
        self.delaySpinBox.valueChanged.connect(self._updateTimeEstimate)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    @QtCore.Slot()
    def _updateTimeEstimate(self):
        start = self.startSpinBox.value()
        stop = self.stopSpinBox.value()
        step = self.stepSpinBox.value()
        delay = self.delaySpinBox.value()
        print start, stop, step, delay

        # Update time estimate
        t = int(abs(float(stop - start) / step * delay))
        print t
        h = t / 3600
        m = (t - h * 3600) / 60
        s = t - h * 3600 - m * 60
        self.timeEstimateLabel.setText('%d h %d m %d s'%(h, m, s))

    @classmethod
    def getScanParameters(cls, spectrometer, parent=None):
        '''
        Returns (start, stop, step, delay) and changes the corresponding
        values in the settings if accepted, or None if not.
        '''
        dialog = cls(spectrometer=spectrometer, parent=parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        if not accepted:
            return

        start = dialog.startSpinBox.value()
        stop = dialog.stopSpinBox.value()
        step = abs(dialog.stepSpinBox.value())
        if start > stop:
            step *= -1
        delay = abs(dialog.delaySpinBox.value())

        # Remember the current values
        settings = QtCore.QSettings()
        settings.setValue('scan/start', start)
        settings.setValue('scan/stop', stop)
        settings.setValue('scan/step', step)
        settings.setValue('scan/delay', delay)
        settings.sync()

        return start, stop, step, delay
