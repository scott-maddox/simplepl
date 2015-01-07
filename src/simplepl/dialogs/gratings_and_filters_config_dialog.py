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
from itertools import izip

# third party imports
from PySide import QtGui, QtCore

# local imports
from ..wavelength_spin_box import WavelengthSpinBox
from ..vertical_scroll_area import VerticalScrollArea


class GratingComboBox(QtGui.QComboBox):
    def __init__(self, spectrometer, grating=None, parent=None):
        super(GratingComboBox, self).__init__(parent)
        for i in xrange(spectrometer.getGratingCount()):
            self.addItem(str(i + 1))
        if grating is not None:
            self.setGrating(grating)

    def setGrating(self, v):
        self.setCurrentIndex(v - 1)


class FilterComboBox(QtGui.QComboBox):
    def __init__(self, spectrometer, filter=None, parent=None):
        super(FilterComboBox, self).__init__(parent)
        for i in xrange(spectrometer.getFilterCount()):
            self.addItem(str(i + 1))
        if filter is not None:
            self.setFilter(filter)

    def setFilter(self, v):
        self.setCurrentIndex(v - 1)


class IndexedPushButton(QtGui.QPushButton):
    indexClicked = QtCore.Signal(int)

    def __init__(self, index, text, parent=None):
        super(IndexedPushButton, self).__init__(text, parent=None)
        self.index = index
        self.clicked.connect(self._clicked)
        self.setMaximumSize(30, 30)

    def _clicked(self):
        self.indexClicked.emit(self.index)


class GratingsAndFiltersConfigDialog(QtGui.QDialog):
    def __init__(self, spectrometer, parent=None):
        super(GratingsAndFiltersConfigDialog, self).__init__(parent)
        self.setModal(True)

        self.spectrometer = spectrometer

        # OK and Cancel buttons
        self.buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)

        # Scroll area for the SpectrumWidgets
        scrollWidget = QtGui.QWidget()
        scroll = VerticalScrollArea()
        scroll.setWidget(scrollWidget)

        # SpinBoxes and ComboBoxes
        self.grid = QtGui.QGridLayout(scrollWidget)
        self.grid.addWidget(QtGui.QLabel('Wavelength (nm)'), 0, 0, 1, 1)
        self.grid.addWidget(QtGui.QLabel('Grating'), 0, 1, 1, 1)
        self.grid.addWidget(QtGui.QLabel('Filter'), 0, 2, 1, 1)
        self.rowCount = 1
        self.index = 0

        self.wavelengthSpinBoxes = []
        self.insertRowButtons = []
        self.removeRowButtons = []
        self.gratingComboBoxes = []
        self.filterComboBoxes = []

        wavelengths, gratings, filters = spectrometer.getConfigs()

        self.appendWavelengthRow(wavelengths[0])
        for wavelength, grating, filter in izip(wavelengths[1:], gratings,
                                                filters):
            self.appendGratingRow(grating, filter)
            self.appendWavelengthRow(wavelength)
        self.wavelengthSpinBoxes[0].selectAll()

        # Connect buttons
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        # Layout
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(scroll, stretch=1)
        layout.addWidget(self.buttons)

    def appendWavelengthRow(self, wavelength):
        wavelengthSpinBox = WavelengthSpinBox(wavelength)
        insertRowButton = IndexedPushButton(self.index, '+')
        removeRowButton = IndexedPushButton(self.index, '-')
        insertRowButton.indexClicked.connect(self.insertRow)
        removeRowButton.indexClicked.connect(self.removeRow)
        self.wavelengthSpinBoxes.append(wavelengthSpinBox)
        self.insertRowButtons.append(insertRowButton)
        self.removeRowButtons.append(removeRowButton)
        self.grid.addWidget(wavelengthSpinBox, self.rowCount, 0, 2, 1)
        self.grid.addWidget(insertRowButton, self.rowCount, 3, 2, 1)
        self.grid.addWidget(removeRowButton, self.rowCount, 4, 2, 1)
        self.rowCount += 1
        self.updateEnabled()

    def appendGratingRow(self, grating, filter):
        gratingComboBox = GratingComboBox(spectrometer=self.spectrometer,
                                          grating=grating)
        filterComboBox = FilterComboBox(spectrometer=self.spectrometer,
                                        filter=filter)
        self.gratingComboBoxes.append(gratingComboBox)
        self.filterComboBoxes.append(filterComboBox)
        self.grid.addWidget(gratingComboBox, self.rowCount, 1, 2, 1)
        self.grid.addWidget(filterComboBox, self.rowCount, 2, 2, 1)
        self.rowCount += 1
        self.index += 1

    def popWavelengthRow(self):
        wavelengthSpinBox = self.wavelengthSpinBoxes.pop()
        insertRowButton = self.insertRowButtons.pop()
        removeRowButton = self.removeRowButtons.pop()
        insertRowButton.indexClicked.disconnect(self.insertRow)
        removeRowButton.indexClicked.disconnect(self.removeRow)
        self.grid.removeWidget(wavelengthSpinBox)
        self.grid.removeWidget(insertRowButton)
        self.grid.removeWidget(removeRowButton)
        wavelengthSpinBox.hide()
        insertRowButton.hide()
        removeRowButton.hide()
        self.rowCount -= 1
        self.updateEnabled()

    def popGratingRow(self):
        gratingComboBox = self.gratingComboBoxes.pop()
        filterComboBox = self.filterComboBoxes.pop()
        self.grid.removeWidget(gratingComboBox)
        self.grid.removeWidget(filterComboBox)
        gratingComboBox.hide()
        filterComboBox.hide()
        self.rowCount -= 1
        self.index -= 1

    def updateEnabled(self):
        enabled = len(self.wavelengthSpinBoxes) > 2
        for removeRowButton in self.removeRowButtons:
            removeRowButton.setEnabled(enabled)

    @QtCore.Slot(int)
    def insertRow(self, index):
        wavelengths = [spinBox.value() for spinBox in
                       self.wavelengthSpinBoxes]
        gratings = [comboBox.currentIndex() + 1 for comboBox in
                    self.gratingComboBoxes]
        filters = [comboBox.currentIndex() + 1 for comboBox in
                   self.filterComboBoxes]
        wavelengths.insert(index, wavelengths[index])
        gratings.insert(index, 1)
        filters.insert(index, 1)

        # Update the rows
        for wavelength, wavelengthSpinBox in izip(wavelengths,
                                                  self.wavelengthSpinBoxes):
            wavelengthSpinBox.setValue(wavelength)
        for grating, gratingComboBox in izip(gratings,
                                                  self.gratingComboBoxes):
            gratingComboBox.setGrating(grating)
        for filter, filterComboBox in izip(filters,
                                                  self.filterComboBoxes):
            filterComboBox.setFilter(filter)

        # Add the last row
        self.appendGratingRow(gratings[-1], filters[-1])
        self.appendWavelengthRow(wavelengths[-1])

    @QtCore.Slot(int)
    def removeRow(self, index):
        wavelengths = [spinBox.value() for spinBox in
                       self.wavelengthSpinBoxes]
        gratings = [comboBox.currentIndex() + 1 for comboBox in
                    self.gratingComboBoxes]
        filters = [comboBox.currentIndex() + 1 for comboBox in
                   self.filterComboBoxes]
        wavelengths.pop(index)
        if index >= len(gratings):
            gratings.pop()
            filters.pop()
        else:
            gratings.pop(index)
            filters.pop(index)

        # Update the rows
        for wavelength, wavelengthSpinBox in izip(wavelengths,
                                                  self.wavelengthSpinBoxes):
            wavelengthSpinBox.setValue(wavelength)
        for grating, gratingComboBox in izip(gratings,
                                                  self.gratingComboBoxes):
            gratingComboBox.setGrating(grating)
        for filter, filterComboBox in izip(filters,
                                                  self.filterComboBoxes):
            filterComboBox.setFilter(filter)

        # Remove the last row
        self.popWavelengthRow()
        self.popGratingRow()

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
        while True:
            result = dialog.exec_()
            accepted = (result == QtGui.QDialog.Accepted)

            if not accepted:
                return

            wavelengths = [spinBox.value() for spinBox in
                           dialog.wavelengthSpinBoxes]

            if wavelengths == sorted(wavelengths):
                break
            else:
                QtGui.QMessageBox.warning(dialog, 'Wrong order',
                                          'Please write the wavelengths in '
                                          'ascending order, from top to '
                                          'bottom.')

        gratings = [comboBox.currentIndex() + 1 for comboBox in
                    dialog.gratingComboBoxes]
        filters = [comboBox.currentIndex() + 1 for comboBox in
                    dialog.filterComboBoxes]

        spectrometer.setConfigs(wavelengths, gratings, filters)

        return wavelengths, gratings, filters

if __name__ == '__main__':
    app = QtGui.QApplication([])
    class FakeSpectrometer(object):
        def getGratingCount(self):
            return 9
        def getFilterCount(self):
            return 9
    s = FakeSpectrometer()
    GratingsAndFiltersConfigDialog.getAdvancedConfig(self.spectrometer)
    app.exec_()