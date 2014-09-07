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
from itertools import izip

# third party imports
from PySide import QtGui, QtCore

# local imports
from ..wavelength_spin_box import WavelengthSpinBox


class GratingComboBox(QtGui.QComboBox):
    def __init__(self, spectrometer, grating=None, parent=None):
        super(GratingComboBox, self).__init__(parent)
        for i in xrange(spectrometer.getGratingCount()):
            self.addItem(str(i + 1))
        if grating is not None:
            self.setCurrentIndex(grating - 1)


class FilterComboBox(QtGui.QComboBox):
    def __init__(self, spectrometer, filter=None, parent=None):
        super(FilterComboBox, self).__init__(parent)
        for i in xrange(spectrometer.getFilterCount()):
            self.addItem(str(i + 1))
        if filter is not None:
            self.setCurrentIndex(filter - 1)


class GratingsAndFiltersConfigDialog(QtGui.QDialog):
    def __init__(self, spectrometer, parent=None):
        super(GratingsAndFiltersConfigDialog, self).__init__(parent)
        self.setModal(True)

        self.spectrometer = spectrometer

        # OK and Cancel buttons
        self.addRowButton = QtGui.QPushButton('Add Row')
        self.removeRowButton = QtGui.QPushButton('Remove Row')
        self.removeRowButton.setEnabled(False)
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        # SpinBoxes and ComboBoxes
        self.grid = QtGui.QGridLayout()
        self.grid.addWidget(QtGui.QLabel('Wavelength (nm)'), 0, 0, 1, 1)
        self.grid.addWidget(QtGui.QLabel('Grating'), 0, 1, 1, 1)
        self.grid.addWidget(QtGui.QLabel('Filter'), 0, 2, 1, 1)
        self.rowCount = 1

        self.wavelengthSpinBoxes = []
        self.gratingComboBoxes = []
        self.filterComboBoxes = []

        wavelengths, gratings, filters = spectrometer.getConfigs()
        wavelengthSpinBox = WavelengthSpinBox(wavelengths[0])
        wavelengthSpinBox.selectAll()
        self.wavelengthSpinBoxes.append(wavelengthSpinBox)
        self.grid.addWidget(wavelengthSpinBox, self.rowCount, 0, 2, 1)
        self.rowCount += 2
        for wavelength, grating, filter in izip(wavelengths[1:], gratings,
                                                filters):
            self.addRow(wavelength, grating, filter)

        # Connect buttons
        self.addRowButton.clicked.connect(self.addRow)
        self.removeRowButton.clicked.connect(self.removeRow)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Layout
        layout = QtGui.QVBoxLayout(self)
        layout.addLayout(self.grid)
        layout.addWidget(self.addRowButton)
        layout.addWidget(self.removeRowButton)
        layout.addWidget(self.buttons)

    def addRow(self, wavelength=None, grating=None, filter=None):
        wavelengthSpinBox = WavelengthSpinBox(wavelength)
        gratingComboBox = GratingComboBox(spectrometer=self.spectrometer,
                                          grating=grating)
        filterComboBox = FilterComboBox(spectrometer=self.spectrometer,
                                        filter=filter)

        self.wavelengthSpinBoxes.append(wavelengthSpinBox)
        self.gratingComboBoxes.append(gratingComboBox)
        self.filterComboBoxes.append(filterComboBox)

        self.grid.addWidget(wavelengthSpinBox, self.rowCount, 0, 2, 1)
        self.grid.addWidget(gratingComboBox, self.rowCount - 1, 1, 2, 1)
        self.grid.addWidget(filterComboBox, self.rowCount - 1, 2, 2, 1)
        self.rowCount += 2
        self.removeRowButton.setEnabled(True)

    def removeRow(self):
        wavelengthSpinBox = self.wavelengthSpinBoxes.pop()
        gratingComboBox = self.gratingComboBoxes.pop()
        filterComboBox = self.filterComboBoxes.pop()

        self.grid.removeWidget(wavelengthSpinBox)
        self.grid.removeWidget(gratingComboBox)
        self.grid.removeWidget(filterComboBox)

        wavelengthSpinBox.deleteLater()
        gratingComboBox.deleteLater()
        filterComboBox.deleteLater()
        self.rowCount -= 2
        if self.rowCount == 3:
            self.removeRowButton.setEnabled(False)

    @classmethod
    def getAdvancedConfig(cls, spectrometer, parent=None):
        '''
        If the dialog is accepted, returns (wavelengths, gratings, filters)
        and changes the corresponding values in the settings. Otherwise,
        returns None.

        Returns
        -------
        wavelengths : list of floats of length N
        gratings : list of ints of length (N - 1)
        filters : list of ints of length (N - 1)
        '''
        dialog = cls(spectrometer=spectrometer, parent=parent)
        result = dialog.exec_()
        accepted = (result == QtGui.QDialog.Accepted)

        if not accepted:
            return

        wavelengths = [spinBox.value() for spinBox in
                       dialog.wavelengthSpinBoxes]
        gratings = [comboBox.currentIndex() + 1 for comboBox in
                    dialog.gratingComboBoxes]
        filters = [comboBox.currentIndex() + 1 for comboBox in
                    dialog.filterComboBoxes]

        spectrometer.setConfigs(wavelengths, gratings, filters)

        return wavelengths, gratings, filters
