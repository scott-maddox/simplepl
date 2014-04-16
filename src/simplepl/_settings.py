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

# third party imports
from PySide import QtCore

# local imports

_settings = QtCore.QSettings("LASE", "SimplePL")

def getWavelengthMin():
    if _settings.contains('wavelength/min'):
        return 
    else:
        _settings.setValue('wavelength/min', 800.)
        return 800.

def getWavelengthMax():
    if _settings.contains('wavelength/max'):
        return float(_settings.value('wavelength/max'))
    else:
        _settings.setValue('wavelength/max', 5500.)
        return 5500.

def getWavelengthPrecision():
    if _settings.contains('wavelength/precision'):
        return float(_settings.value('wavelength/precision'))
    else:
        _settings.setValue('wavelength/precision', 0.1)
        return 0.1

def getLockinDelay():
    if _settings.contains('lockin/delay'):
        return float(_settings.value('lockin/delay'))
    else:
        _settings.setValue('lockin/delay', 0.5)
        return 0.5