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
import logging
log = logging.getLogger(__name__)

# third party imports
import numpy as np


class SimplePLParser(object):
    def __init__(self, filepath=None, sysresFilepath=None):
        '''
        filepath : string
            the PL filepath
        sysresFilepath : string
            the system response filepath. If this is provided it overrides
            the system response used in the saved file (if possible).
        '''
        self.filepath = filepath
        self.sysresFilepath = sysresFilepath
        self._sysresParser = None
        if sysresFilepath is not None:
            self._sysresParser = SimplePLParser(sysresFilepath)
            try:
                self._sysresParser.parse()
                log.debug('Opened system response file: {}'
                          ''.format(sysresFilepath))
            except:
                log.debug('Unable to open system response file: {}'
                          ''.format(sysresFilepath))
                self._sysresParser = None

    def getSysRes(self, wavelength):
        if self._sysresParser is None:
            return np.nan
        i = np.searchsorted(self._sysresParser.wavelength, wavelength)
        return self._sysresParser.rawSignal[i]

    def parse(self):
        self.wavelength = []
        self.rawSignal = []
        self.phase = []
        self.signal = []
        with open(self.filepath, 'rU') as f:
            first_line = f.readline()
            if first_line.startswith('**\tSample ID:'):
                self._parseLabVIEW(first_line, f)
            elif first_line.startswith('Wavelength\tRawSignal'):
                self._parseWavelengthRawSignal(first_line, f)
            elif first_line.startswith('Wavelength\tRaw_Signal'):
                self._parseWavelengthRawSignal(first_line, f)
            elif first_line.startswith('Wavelength\tRawSignal\tPhase'):
                self._parseWavelengthRawSignalPhase(first_line, f)
            elif first_line.startswith('Wavelength\tRaw_Signal\tPhase'):
                self._parseWavelengthRawSignalPhase(first_line, f)
            elif first_line.startswith('Wavelength\tSysResRem'):
                self._parseWavelengthSysResRem(first_line, f)
            elif first_line.startswith('Wavelength\tSignal\tRawSignal\tPhase'):
                self._parseWavelengthSignalRawSignalPhase(first_line, f)
            elif first_line.startswith(
                                    'Wavelength\tSignal\tRaw_Signal\tPhase'):
                self._parseWavelengthSignalRawSignalPhase(first_line, f)
            else:
                raise NotImplementedError()
        if self.wavelength:
            self.wavelength = np.array(self.wavelength, dtype=np.double)
            self.energy = 1239.842 / self.wavelength
        else:
            self.wavelength = None
            self.energy = None
        if self.signal:
            self.signal = np.array(self.signal, dtype=np.double)
        else:
            self.signal = None
        if self.rawSignal:
            self.rawSignal = np.array(self.rawSignal, dtype=np.double)
        else:
            self.rawSignal = None
        if self.phase:
            self.phase = np.array(self.phase, dtype=np.double)
        else:
            self.phase = None

    def _parseLabVIEW(self, first_line, f):
        self.sample_id = first_line[len('**\tSample ID:')].strip()
        self.laser_power = f.readline()[len('**\tLaser Power:')].strip()
        self.measurement_type = f.readline()[
                                        len('**\tMeasurement Type:')].strip()
        self.datetime_str = f.readline()[len('**\t')].strip()
        f.readline()  # grating (doesn't work properly)
        self.time_constant = f.readline()[len('**\tTime Constant:')].strip()
        self.notes = f.readline()[len('**\tNotes:')].strip()
        f.readline()  # blank
        f.readline()  # column headers
        f.readline()  # astrisks
        while True:
            line = f.readline()
            if not line:
                break  # end of file
            values = line.split()
            self.wavelength.append(float(values[0]))
            self.rawSignal.append(float(values[1]))
            self.signal.append(float(values[2]))

    def _parseWavelengthRawSignal(self, first_line, f):
        # first_line is the column headers
        while True:
            line = f.readline()
            if not line:
                break  # end of file
            values = line.split()
            wavelength = float(values[0])
            raw = float(values[1])
            self.wavelength.append(wavelength)
            self.rawSignal.append(raw)
            if self.sysresFilepath is not None:
                sysres = self.getSysRes(wavelength)
                sysresrem = raw / sysres
                self.signal.append(sysresrem)

    def _parseWavelengthRawSignalPhase(self, first_line, f):
        # first_line is the column headers
        while True:
            line = f.readline()
            if not line:
                break  # end of file
            values = line.split()
            wavelength = float(values[0])
            raw = float(values[1])
            phase = float(values[2])
            self.wavelength.append(wavelength)
            self.rawSignal.append(raw)
            self.phase.append(phase)
            if self.sysresFilepath is not None:
                sysres = self.getSysRes(wavelength)
                signal = raw / sysres
                self.signal.append(signal)

    def _parseWavelengthSysResRem(self, first_line, f):
        if self.sysresFilepath is not None:
            log.warn("Ignoring the provided system response file")
        # first_line is the column headers
        while True:
            line = f.readline()
            if not line:
                break  # end of file
            values = line.split()
            wavelength = float(values[0])
            signal = float(values[1])
            self.wavelength.append(wavelength)
            self.signal.append(signal)

    def _parseWavelengthSignalRawSignalPhase(self, first_line, f):
        if self.sysresFilepath is not None:
            log.warn("Ignoring the signal column")
        # first_line is the column headers
        while True:
            line = f.readline()
            if not line:
                break  # end of file
            values = line.split()
            self.wavelength.append(float(values[0]))
            self.rawSignal.append(float(values[2]))
            self.phase.append(float(values[3]))
            if self.sysresFilepath is not None:
                sysres = self.getSysRes(self.wavelength[-1])
                signal = self.rawSignal[-1] / sysres
                self.signal.append(signal)
            else:
                self.signal.append(float(values[1]))
