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
import visa
import numpy as np

# local imports

DEBUG = False

#TODO: read and store R and Theta?
class Lakeshore330(object):
    def __init__(self, port='GPIB::12'):
        super(Lakeshore330, self).__init__()
        self._inst = visa.instrument(port)
        # device identification
        id = self._ask('*IDN?').split(',')
        if len(id) < 1 or id[1] != 'MODEL330':
            raise RuntimeError('Unexpected instrument ID: %s'%(''.join(id)))
        self._write('TERM 0') # set terminating characters to <CR><LF>
        self._write('CUNI K') # set control units to Kelvin
        self._write('SUNI K') # set control units to Kelvin
        self._write('FILT 0') # disable display filtering
        self._write('RANG 3') # sets heater status to high
        self.set_ramp_rate(10)

    def _read(self):
        r = self._inst.read()
        if DEBUG:
            print "<<", r
        return r

    def _write(self, s):
        if DEBUG:
            print ">>", s
        self._inst.write(s)

    def _ask(self, s):
        self._write(s)
        return self._read()

    def get_temperature(self):
        '''
        Returns the current temperautre in Kelvin.
        '''
        return float(self._ask('SDAT?'))

    def set_temperature(self, t):
        '''
        Changes the setpoint temperature to the given value in Kelvin.
        '''
        self._write('SETP %3.0f'%t)

    def set_ramp_rate(self, r):
        '''
        Set the temperature ramp rate in Kelvin/min, in range [0, 99.9]
        '''
        self._write('RAMPR %2.1f'%r)

    def get_output(self):
        '''
        Returns the current heater output in percentage with a precision of 5%.
        '''
        return float(self._ask('HEAT?'))

if __name__ == "__main__":
    # enable DEBUG output
    logging.basicConfig(level=logging.DEBUG)

    # Test
    tc = Lakeshore330()
    print tc._ask('*STB?')
    print tc.get_temperature()
    print tc.get_output()
    #tc.set_temperature(140)
