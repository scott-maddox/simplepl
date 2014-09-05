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


class Spectrometer(QtCore.QThread):
    '''
    Provides an asynchronous QThread interface to the spectrometer.

    Under the hood, this class uses Signals to call functions in another
    thread. The results are emitted in other Signals, which are specified
    in the doc strings.
    '''
    _sigRequestQuit = QtCore.Signal()
    _sigGetGrating = QtCore.Signal()
    _sigSetGrating = QtCore.Signal(int)
    _sigGetFilter = QtCore.Signal()
    _sigSetFilter = QtCore.Signal(int)
    _sigGetWavelength = QtCore.Signal()
    _sigSetWavelength = QtCore.Signal(float)

    sigChangingGrating = QtCore.Signal()
    sigChangingFilter = QtCore.Signal()

    sigGrating = QtCore.Signal(int)
    sigFilter = QtCore.Signal(int)
    sigWavelength = QtCore.Signal(float)

    def __init__(self):
        super(Spectrometer, self).__init__()
        # Initialize variables
        self._spectrometer = None
        self._filterWheel = None
        self._settings = None
        self._grating = None
        self._filter = None

        # Connect signals/slots for asynchronous methods
        self._sigRequestQuit.connect(self._Quit)
        self._sigGetGrating.connect(self._getGrating)
        self._sigSetGrating.connect(self._setGrating)
        self._sigGetFilter.connect(self._getFilter)
        self._sigSetFilter.connect(self._setFilter)
        self._sigGetWavelength.connect(self._getWavelength)
        self._sigSetWavelength.connect(self._setWavelength)

        # Start the thread
        self.moveToThread(self)
        self.start()

    def run(self):
        # Initialize QSettings object
        self._settings = QtCore.QSettings("LASE", "SimplePL")

        # Initialize the spectrometer
        try:
            from drivers.spectra_pro_2500i import SpectraPro2500i
        except (OSError, ImportError):
            print "Couldn't load spectrometer device driver. Simulating..."
            from drivers.spectra_pro_2500i_sim import SpectraPro2500i
        self._spectrometer = SpectraPro2500i()

        # Initialize the filter wheel
        try:
            from drivers.thorlabs_fw102c import FW102C
        except (OSError, ImportError):
            print "Couldn't load filter wheel device driver. Simulating..."
            from drivers.thorlabs_fw102c_sim import FW102C
        filterWheelPort = int(self._settings.value('filterWheel/port', 3))
        self._filterWheel = FW102C(port=filterWheelPort)

        # Start the event loop
        self.exec_()

    @QtCore.Slot()
    def _Quit(self):
        self.quit()

    def requestQuit(self):
        '''
        Sends a request to the spectrometer thread to quit.

        In order to give it time to quit on close, use the following:
            spectrometer.requestQuit()
            spectrometer.wait()
        '''
        self._sigRequestQuit.emit()

    @QtCore.Slot()
    def _getGrating(self):
        result = self._spectrometer.get_grating()
        self._grating = result
        self.sigGrating.emit(result)
        return result

    def getGrating(self):
        '''
        Gets the current grating index.

        Emits
        -----
            sigGrating(int)
        '''
        self._sigGetGrating.emit()

    @QtCore.Slot(int)
    def _setGrating(self, i):
        self.sigChangingGrating.emit()
        self._spectrometer.set_grating(i)
        self._getGrating()  # read and emit the resulting grating

    def setGrating(self, i):
        '''
        Goes to the specified grating index.

        Emits
        -----
            sigGrating(int)
            sigWavelength(float)
        '''
        self._sigSetGrating.emit(i)

    @QtCore.Slot()
    def _getFilter(self):
        result = self._filterWheel.get_filter()
        self._filter = result
        self.sigFilter.emit(result)
        return result

    def getFilter(self):
        '''
        Gets the current filter index.

        Emits
        -----
            sigFilter(int)
        '''
        self._sigGetFilter.emit()

    @QtCore.Slot(int)
    def _setFilter(self, i):
        self.sigChangingFilter.emit()
        self._filterWheel.set_filter(i)
        self._getFilter()  # read and emit the resulting filter

    def setFilter(self, i):
        '''
        Goes to the specified filter index.

        Emits
        -----
            sigFilter(int)
        '''
        self._sigSetFilter.emit(i)

    @QtCore.Slot()
    def _getWavelength(self):
        result = self._spectrometer.get_wavelength()
        self.sigWavelength.emit(result)
        return result

    def getWavelength(self):
        '''
        Gets the current wavelength in nm.

        Emits
        -----
            sigWavelength(float)
        '''
        self._sigGetWavelength.emit()

    def _getTargetGrating(self, wavelength):
        if wavelength < 800.:
            raise ValueError('wavelengths below 800 nm are not supported')
        elif wavelength <= 1592.:
            return 2  # 1.2 um blaze
        elif wavelength <= 2353.:
            return 3  # 2 um blaze
        elif wavelength <= 5500.:
            return 1  # 4 um blaze
        raise ValueError('wavelengths above 5500 nm are not supported')

    def _getTargetFilter(self, wavelength):
        if wavelength < 800.:
            raise ValueError('wavelengths below 800 nm are not supported')
        elif wavelength <= 1592.:
            return 1  # 800-1500 nm
        elif wavelength <= 2621.:
            return 2  # 1500-3000 nm
        elif wavelength <= 5500.:
            return 3  # 2500-7000 nm
        raise ValueError('wavelengths above 5500 nm are not supported')

    @QtCore.Slot(float)
    def _setWavelength(self, wavelength):
        # Change the grating, if needed
        if self._grating is None:
            self._getGrating()
        targetGrating = self._getTargetGrating(wavelength)
        if self._grating != targetGrating:
            self.setGrating(targetGrating)

        # Change the filter, if needed
        if self._filter is None:
            self._getFilter()
        targetFilter = self._getTargetFilter(wavelength)
        if self._filter != targetFilter:
            self.setFilter(targetFilter)

        # Go to the specified target wavelength
        self._spectrometer.goto(wavelength)
        self._getWavelength()  # read and emit the resulting wavelength

    def setWavelength(self, wavelength):
        '''
        Goes to the specified wavelength in wavelength. Automatically
        sets the grating and filter as configured in the settings.

        Emits
        -----
            sigWavelength(float)
        '''
        self._sigSetWavelength.emit(wavelength)
