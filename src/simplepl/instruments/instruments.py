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
import logging
log = logging.getLogger(__name__)

# third party imports
from PySide import QtCore

# local imports
from ..utils.connected_process import ConnectedProcess, ConnectedQObject


def InstrumentsProcess(ConnectedProcess):
    def init(self):
        super(InstrumentsProcess, self).init()


def InstrumentsConnection(ConnectedQObject):

    sigWavelengthChanging = QtCore.Signal()
    sigWavelengthChanged = QtCore.Signal(float)

    def init(self):
        super(InstrumentsConnection, self).init()

        # register commands
        self.register_command('wavelengthChanging', self._wavelengthChanging)
        self.register_command('wavelengthChanged', self._wavelengthChanged)

    def _wavelengthChanging(self):
        self.sigWavelengthChanging.emit()

    def _wavelengthChanged(self, v):
        self.sigWavelengthChanging.emit(v)
