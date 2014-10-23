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
from PySide import QtCore


class AbstractSpectrum(QtCore.QObject):
    sigChanged = QtCore.Signal()

    def __init__(self, **kwargs):
        super(AbstractSpectrum, self).__init__()
        self._color = kwargs.get('color', None)

    def getWavelength(self):
        raise NotImplementedError()

    def getSignal(self):
        raise NotImplementedError()

    def getRawSignal(self):
        raise NotImplementedError()

    def getPhase(self):
        raise NotImplementedError()

    def getEnergy(self):
        raise NotImplementedError()

    def setColor(self, color):
        self._color = color

    def getColor(self):
        return self._color
