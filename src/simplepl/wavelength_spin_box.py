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
from math import floor, log10

# third party imports
from PySide import QtGui, QtCore


class WavelengthSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self, value=None, parent=None):
        super(WavelengthSpinBox, self).__init__(parent)
        self._settings = QtCore.QSettings()
        wlmin = self.getMinWavelength()
        wlmax = self.getMaxWavelength()
        precision = self.getPrecision()
        decimals = floor(-log10(precision))
        if decimals < 0:
            decimals = 0

        self.setDecimals(decimals)
        self.setRange(wlmin, wlmax)
        self.setSingleStep(precision)
        if value is not None:
            self.setValue(float(value))

    def getMinWavelength(self):
        return float(self._settings.value('WavelengthSpinBox/min', 0.1))

    def getMaxWavelength(self):
        return float(self._settings.value('WavelengthSpinBox/max', 10000.))

    def getPrecision(self):
        return float(self._settings.value('WavelengthSpinBox/precision', 0.1))

    def getUnits(self):
        return self._settings.value('WavelengthSpinBox/units', 'nm')

    def getLabel(self):
        return 'Wavelength ({})'.format(self.getUnits())
