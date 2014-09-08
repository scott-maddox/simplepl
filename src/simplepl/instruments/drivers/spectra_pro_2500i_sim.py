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
import time
import string
import logging
log = logging.getLogger(__name__)

# third party imports
#import serial

SLEEP_TIME = 0.01

class TimeoutException(Exception):
    pass

#TODO: make sure the asked for nm is available on the given grating?
class SpectraPro2500i(object):
    def __init__(self, port=0, timeout=5.):
        self.nm = 0.
        self.grating = 1
        #self._inst = serial.Serial(port,
        #                           baudrate=9600,
        #                           bytesize=serial.EIGHTBITS,
        #                           parity=serial.PARITY_NONE,
        #                           stopbits=serial.STOPBITS_ONE,
        #                           timeout=timeout)

    def __read(self):
        '''
        Returns a full response from the instrument.
        Raises a TimeoutException if the operation times out.
        '''
        #r = self._inst.readline()
        r = 'CMD OK DATA'
        if not r:
            raise TimeoutException()
        log.debug("__read: return '%s'", r)
        return r

    def _read(self):
        '''
        Returns an OK-stripped response from the instrument.
        Raises a TimeoutException if the operation times out.
        '''
        r = self.__read()
        r = string.join(r.split()[1:-1]) # strip command echo and "ok"
        log.debug("_read: return '%s'", r)
        return r

    def __write(self, s):
        log.debug("__write: write('%s')", s)
        #self._inst.write(s+"\r")

    def _write(self, s):
        '''Writes to the instrument, and waits for an OK response'''
        self.__write(s)
        #while True:
        #    if self.__read()[-4:] == "ok\r\n":
        #        log.debug("_write: self.__read()[-4:] == 'ok\r\n'")
        #        break
        #    log.debug("_write: time.sleep(%g)", SLEEP_TIME)
        #    time.sleep(SLEEP_TIME)

    def _ask(self, s):
        '''Writes to the instrument, and returns the OK-stripped response'''
        log.debug("__ask: __write('%s')", s)
        self.__write(s)
        return self._read()

    # Wavelength movement commands

    def wait_until_done(self):
        '''
        Waits until the current scanto operation is done
        '''
        raise NotImplementedError()
        while True:
            if int(self._ask("MONO-?DONE")):
                break
            time.sleep(SLEEP_TIME)
        #TODO: implement a simulated scan, with timed increments

    def wait_until_above(self, nm):
        '''
        Waits until the current wavelength position is above the specified
        position in nm. This should only be used during a scanto operation.
        '''
        raise NotImplementedError()
        while True:
            pos = self.get_position()
            if pos > nm:
                break
            time.sleep(SLEEP_TIME)
        #TODO: implement a simulated scan, with timed increments

    def wait_until_below(self, nm):
        '''
        Waits until the current wavelength position is below the specified
        position in nm. This should only be used during a scanto operation.
        '''
        raise NotImplementedError()
        while True:
            pos = self.get_position()
            if pos < nm:
                break
            time.sleep(SLEEP_TIME)
        #TODO: implement a simulated scan, with timed increments

    def get_position(self):
        '''Returns the current wavelength position in nm'''
        #return float(self._ask("?nm").split()[0])
        return self.nm

    def get_wavelength(self):
        '''Returns the current wavelength position in nm'''
        return self.get_position()

    def goto(self, nm, wait=True):
        '''
        Goes to the destination wavelength at maximum motor speed.
        The maximum accepted wavelength precision is 0.001 nm.
        The experimentally acheivable precision will vary.
        '''
        self._write("%.3f GOTO"%nm)
        delta = abs(self.nm - nm)
        self.nm = nm
        time.sleep(delta/1000.)

    def scanto(self, nm, nm_per_min=None):
        '''
        Scans to the destination wavelength (in nm)
         at the specified rate (in nm/min)
        The maximum accepted wavelength precision is 0.001 nm.
        The maximum accepted rate precision is 0.01 nm/min.
        The experimentally acheivable precisions will vary.
        '''
        if nm_per_min is not None:
            self._write("%.2f NM/MIN"%nm_per_min)
        self._write("%.3f >NM"%nm)
        self.nm = nm
        #TODO: implement a simulated scan, with timed increments

    def abort_scan(self):
        self._write("MONO-STOP")

    # Grating control commands

    def set_grating(self, i):
        '''Set grating to number 1 through 9'''
        if i < 1 or i > 9 or not isinstance(i, int):
            raise ValueError("i must be an integer from 1 to 9")
        self._write("%d GRATING"%i)
        if self.grating != i:
            time.sleep(5)
        self.grating = i

    def get_grating(self):
        #return self._ask("?GRATING")
        return self.grating

    def get_grating_list(self):
        '''Returns a list of the gratings'''
        self.__write("?GRATINGS")
        #TODO: Take an actual output sample and replace this with it
        gratings = [
        '->1 Bla bla',
        '  2 Bla bla',
        '  3 Bla bla',
        '  4 Bla bla',
        '  5 Bla bla',
        '  6 Bla bla',
        '  7 Bla bla',
        '  8 Bla bla',
        '  9 Bla bla',
        ]
        #self.__read() # trash the first blank line
        #for i in xrange(9):
        #    gratings.append(string.join(self.__read().split()[1:]))
        #self.__read() # trash the extra "ok" line
        return gratings

    def set_turret(self, i):
        if i < 1 or i > 3 or not isinstance(i, int):
            raise ValueError("i must be an integer from 1 to 3")
        self._write("%d TURRET"%i)

    def get_turret(self):
        #return self._ask("?TURRET")
        return 1

    # Diverter control commands

    def set_exit_mirror_front(self):
        self._write("EXIT-MIRROR FRONT")

    def set_exit_mirror_side(self):
        self._write("EXIT-MIRROR SIDE")

    def set_entrance_mirror_front(self):
        self._write("ENT-MIRROR FRONT")

    def set_entrance_mirror_side(self):
        self._write("ENT-MIRROR SIDE")

    # Misc. commands

    def get_model(self):
        '''Returns the model number of the SpectraPro monochromator'''
        #return self._ask("MODEL")
        return 'SP-2500i'

    def get_serial(self):
        '''Returns the 7 digit serial number of the SpectraPro monochromator'''
        #return self._ask("SERIAL")
        return '1234567'

    def close(self):
        '''Close the serial connection to the instrument'''
        log.debug("close: self._inst.close()")
        #self._inst.close()

if __name__ == "__main__":
    # enable DEBUG output
    logging.basicConfig(level=logging.DEBUG)

    # run tests
    spec = SpectraPro2500i(port=0)
    print 'Get the model:'
    print spec.get_model()
    print 'Get the serial:'
    print spec.get_serial()
    time.sleep(1)
    print 'Get the grating list:'
    print spec.get_grating_list()
    print 'Closing the serial port...'
    spec.close()
    print 'Done!'
    spec.set_grating(1)
    spec.goto(5000)
    print 'done!'
    spec.goto(2600)
    print 'done!'
    #spec.scanto(2700, 1200)
    #print 'done?'
    #spec.wait_until_above(2610)
    #spec.wait_until_done()
    #print spec.get_position()
    #print 'done!'
    #spec.goto(2700)
    #spec.scanto(2600, 1200)
    #print spec.get_position()
    #print 'sleeping'
    #for i in xrange(4):
    #    time.sleep(1)
    #    print spec.get_position()
    #print 'aborting'
    #spec.abort_scan()
    print 'done!'
    print 'position = %.3f nm'%spec.get_position()
    print 'Changing grating to 1'
    spec.set_grating(1)
    print 'done!'
    print 'grating: ', spec.get_grating()
    print 'Changing grating to 2'
    spec.set_grating(2)
    print 'done!'
    print 'grating: ', spec.get_grating()
    print 'gratings:\n', spec.get_grating_list()
    print 'turret: ', spec.get_turret()
    print 'Changing turret to 1'
    spec.set_turret(1)
    print 'turret: ', spec.get_turret()
    print 'Setting exit mirror to front'
    spec.set_exit_mirror_front()
    time.sleep(1)
    print 'Setting exit mirror to side'
    spec.set_exit_mirror_side()
    time.sleep(1)
    print 'Setting entrance mirror to side'
    spec.set_entrance_mirror_side()
    time.sleep(1)
    print 'Setting entrance mirror to front'
    spec.set_entrance_mirror_front()
    time.sleep(1)
