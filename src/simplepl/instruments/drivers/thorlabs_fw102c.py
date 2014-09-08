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
import string

# third party imports
import serial

# local imports


#TODO: make sure the asked for nm is available on the given grating?
class FW102C(object):
    '''
    Device driver for ThorLabs FW102C Motorized Filter Wheel.
    '''
    def __init__(self, port, timeout=5.):
        self._inst = serial.Serial(port,
                                   baudrate=115200,
                                   bytesize=serial.EIGHTBITS,
                                   parity=serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE,
                                   timeout=timeout)
        while self.__read(): # clear the filter's output buffer
            pass
        while True:
            id = self.get_id()
            if id != "Command error":
                break
            while self.__read(): # clear the filter's output buffer
                pass
        if id != "THORLABS FW102C/FW212C Filter Wheel version 1.01":
            raise RuntimeError('Wrong instrument id: %s'%id)
            

    def __read(self):
        r = self._inst.readline()
        log.debug('__read: return "%s"', r)
        return r

    def _read(self):
        r = self.__read()
        r = string.join(r.split()[1:-1]) # strip command echo and "ok"
        log.debug('_read: return "%s"', r)
        return r

    def __write(self, s):
        log.debug('__write: _inst.write("%s")', s)
        self._inst.write(s+"\r")

    def _write(self, s):
        self.__write(s)
        self._read() # command echo

    def _ask(self, s):
        self.__write(s)
        return self._read()

    def get_id(self):
        return self._ask('*idn?')

    #TODO: check how it confirms pos=1, if at all, and compensate
    def set_filter(self, i):
        '''
        Sets the filter wheel position to the given index
        '''
        if not isinstance(i, int) or i < 1 or i > 6:
            raise ValueError('i must be an integer in the range [1, 6]')
        self._write('pos=%d'%i)

    def get_filter(self):
        return int(self._ask('pos?'))

if __name__ == "__main__":
    # enable DEBUG output
    logging.basicConfig(level=logging.DEBUG)

    # Test
    fw = FW102C(port=3)
    print fw.get_id()
    print fw.get_filter()
    fw.set_filter(1)
    print fw.get_filter()
    fw.set_filter(2)
    print fw.get_filter()
