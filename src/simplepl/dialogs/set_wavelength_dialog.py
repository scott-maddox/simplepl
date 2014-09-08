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


class SetWavelengthDialog(QtGui.QDialog):
    def __init__(self, spectrometer, wavelength=None, parent=None):
        super(SetWavelengthDialog, self).__init__(parent)
        self.setModal(True)

        minWavelength = spectrometer.getMinWavelength()
        maxWavelength = spectrometer.getMaxWavelength()

        self.wavelengthSpinBox = WavelengthSpinBox(value=wavelength)
        self.wavelengthSpinBox.setRange(minWavelength, maxWavelength)
        self.wavelengthSpinBox.selectAll()

        layout = QtGui.QVBoxLayout(self)
        form = QtGui.QFormLayout()
        form.addRow('Wavelength ({})'
                    ''.format(self.wavelengthSpinBox.getUnits()),
                              self.wavelengthSpinBox)
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
    def getWavelength(cls, spectrometer, wavelength=None, parent=None):
        '''
        Returns the wavelength if accepted, or None if not.
        '''
        dialog = cls(spectrometer=spectrometer,
                     wavelength=wavelength, parent=parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        if not accepted:
            return

        return dialog.wavelengthSpinBox.value()
