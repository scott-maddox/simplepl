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
import logging
log = logging.getLogger(__name__)
import random

# third party imports
import numpy as np
#import visa

# Serial Poll Status Byte bits
# The status bits are set to 1 when the event or state described in the
# tables below has occurred or is present.
# 
# bit     name    usage
# 
# 0       SCN     No scan in progress (Stop or Done). A Paused scan is
#                 considered to be in progress.
#                 
# 1       IFC     No command execution in progress.
# 
# 2       ERR     An enabled bit in the error status byte has been set.
# 
# 3       LIA     An enabled bit in the LIA status byte has been set.
# 
# 4       MAV     The interface output buffer is non-empty.
# 
# 5       ESB     An enabled bit in the standard status byte has
#                 been set.
#                 
# 6       SRQ     SRQ (service request) has occurred.
# 
# 7       Unused
STB_SCN = 1 << 0
STB_IFC = 1 << 1
STB_ERR = 1 << 2
STB_LIA = 1 << 3
STB_MAV = 1 << 4
STB_ESB = 1 << 4
STB_SRQ = 1 << 4

#TODO: read and store R and Theta?
class SR830(object):
    time_constant_labels = (u'10 \u03Bcs', u'30 \u03Bcs',
                            u'100 \u03Bcs', u'300 \u03Bcs',
                            u'1 ms', u'3 ms',
                            u'10 ms', u'30 ms',
                            u'100 ms', u'300 ms',
                            u'1 s', u'3 s',
                            u'10 s', u'30 s',
                            u'100 s', u'300 s',
                            u'1 ks', u'3 ks',
                            u'10 ks', u'30 ks')
    time_constant_seconds = np.array((1e-5, 3e-5,
                                      1e-4, 3e-4,
                                      1e-3, 3e-3,
                                      1e-2, 3e-2,
                                      1e-1, 3e-1,
                                      1e0, 3e0,
                                      1e1, 3e1,
                                      1e2, 3e2,
                                      1e3, 3e3,
                                      1e4, 3e4))
    sensitivity_labels = (u'2 nV/fA',
                          u'5 nV/fA',
                          u'10 nV/fA',
                          u'20 nV/fA',
                          u'50 nV/fA',
                          u'100 nV/fA',
                          u'200 nV/fA',
                          u'500 nV/fA',
                          u'1 \u03BcV/pA',
                          u'2 \u03BcV/pA',
                          u'5 \u03BcV/pA',
                          u'10 \u03BcV/pA',
                          u'20 \u03BcV/pA',
                          u'50 \u03BcV/pA',
                          u'100 \u03BcV/pA',
                          u'200 \u03BcV/pA',
                          u'500 \u03BcV/pA',
                          u'1 mV/nA',
                          u'2 mV/nA',
                          u'5 mV/nA',
                          u'10 mV/nA',
                          u'20 mV/nA',
                          u'50 mV/nA',
                          u'100 mV/nA',
                          u'200 mV/nA',
                          u'500 mV/nA',
                          u'1 V/\u03BcA')
    sensitivity_voltages = np.array((2.e-9, 5.e-9,
                                     1.e-8, 2.e-8, 5.e-8,
                                     1.e-7, 2.e-7, 5.e-7,
                                     1.e-6, 2.e-6, 5.e-6,
                                     1.e-5, 2.e-5, 5.e-5,
                                     1.e-4, 2.e-4, 5.e-4,
                                     1.e-3, 2.e-3, 5.e-3,
                                     1.e-2, 2.e-2, 5.e-2,
                                     1.e-1, 2.e-1, 5.e-1,
                                     1.))
    sensitivity_currents = np.array((2.e-15, 5.e-15,
                                     1.e-14, 2.e-14, 5.e-14,
                                     1.e-13, 2.e-13, 5.e-13,
                                     1.e-12, 2.e-12, 5.e-12,
                                     1.e-11, 2.e-11, 5.e-11,
                                     1.e-10, 2.e-10, 5.e-10,
                                     1.e-9, 2.e-9, 5.e-9,
                                     1.e-8, 2.e-8, 5.e-8,
                                     1.e-7, 2.e-7, 5.e-7,
                                     1.e-6))

    def __init__(self, port='GPIB::8'):
        super(SR830, self).__init__()
        self.init_output_generator()
        self.sensitivity = 10
        self.time_constant = 0

        #self._inst = visa.instrument(port)

        self._clear()
        #log.debug('STB: %d'%self._inst.stb)

        # Check device identification
        #id = self._ask('*IDN?').split(',')
        #if len(id) < 1 or id[1] != 'SR830':
        #    log.error('Unexpected instrument ID: %s'%(''.join(id)))
        #    raise RuntimeError('Unexpected instrument ID: %s'%(''.join(id)))

    def init_output_generator(self):
        self.output_index = 0
        N = 100
        R_noise = np.abs(np.random.normal(1e-6, 1e-7, N))
        self.R = 1e-4*np.exp(-np.linspace(-5, 5, N)**2) + R_noise
        self.theta = (np.random.random_sample(N)*1e-3/self.R+180.)%360.-180.

    #TODO: add checks for the event and error status bytes to
    # _read and _write, and handle events appropriately
    def _read(self):
        #r = self._inst.read()
        r = ''
        log.debug("_read: return '%s'", r)
        return r

    def _write(self, s):
        log.debug("_write: write('%s')", s)
        #self._inst.write(s)

    def _ask(self, s):
        log.debug("_ask: ask('%s')", s)
        #r = self._inst.ask(s)
        r = ''
        log.debug("_ask: return '%s'", r)
        return r

    def _clear(self):
        '''
        Clears the status registers and output buffers.
        '''
        log.debug("_clear: clearing...")
        #self._inst.clear()

    def set_output(self, i):
        '''
        Sets the output interface.
            i=0 : RS232
            i=1 : GPIB
        '''
        self._write('OUTX %d'%i)
    def set_rs232_output(self):
        self.set_output(0)
    def set_gpib_output(self):
        self.set_output(1)

    # Reference and Phase commands
    def set_phase_shift(self, v):
        self._write('PHAS %.2f'%v)
    def get_phase_shift(self):
        #return float(self._ask('PHAS?'))
        return 0.

    def set_reference_source(self, i):
        '''
            Sets the reference source.
            i=1 : internal
            i=0 : external
        '''
        if not i in [0, 1]:
            raise ValueError('i must be 0 for external, or 1 for internal')
        self._write('FMOD %d'%i)
    def get_reference_source(self):
        '''
            Gets the reference source.
            i=1 : internal
            i=0 : external
        '''
        #return int(self._ask('FMOD?'))
        return 0

    def get_reference_frequency(self):
        '''
        Gets the current reference frequency of the internal oscillator.
        '''
        #return float(self._ask('FREQ?'))
        return 1000.
    def set_reference_frequency(self, f):
        '''
        Sets the reference frequency (in Hz) of the internal oscillator.
        This command is allowed only if the reference source is internal.

        The value of f is limited to the range [0.001, 102000], and will be
        rounded to 5 digits or 0.0001 Hz (whichever is greater).
        '''
        self._write('FREQ %G'%f)

#TODO: Test functions below here

    def get_reference_trigger(self):
        '''
        Gets the reference trigger when using the external reference mode.
            i=0 : sine zero crossing
            i=1 : TTL rising edge
            i=2 : TTL falling edge
        '''
        #return int(self._ask('RSLP?'))
        return 2
    def set_reference_trigger(self, i):
        '''
        Sets the reference trigger when using the external reference mode.
            i=0 : sine zero crossing
            i=1 : TTL rising edge
            i=2 : TTL falling edge

        At frequencies below 1 Ha, a TTL reference must be used.
        '''
        self._write('RSLP %d'%i)

    def get_detection_harmonic(self):
        '''
        Gets the detection harmonic. This parameter is an integer from 1 to
        19999, which configures the lock-in to detect at the corresponding
        harmonic of the reference frequency. The resulting harmonic frequency
        must be less than 102 kHz.
        '''
        #return float(self._ask('HARM?'))
        return 1
    def set_detection_harmonic(self, i):
        '''
        Sets the detection harmonic. This parameter is an integer from 1 to
        19999, which configures the lock-in to detect at the corresponding
        harmonic of the reference frequency. The resulting harmonic frequency
        must be less than 102 kHz.
        '''
        self._write('HARM %d'%i)

    def get_sine_output_amplitude(self):
        '''
        Gets the amplitude of the sine output in voltage. The value is limited
        to the range [0.004, 5.000], and is rounded to 0.002 V.
        '''
        #return float(self._ask('SLVL?'))
        return 1.
    def set_sine_output_amplitude(self, v):
        '''
        Sets the amplitude of the sine output in voltage. The value is limited
        to the range [0.004, 5.000], and is rounded to 0.002 V.
        '''
        self._write('SLVL %f'%v)

    # Input filter commands
    def get_input_configuration(self):
        '''
        Gets the input configuration.
            i=0 : A
            i=1 : A-B
            i=2 : I (1 MOhm)
            i=3 : I (100 MOhm)
        '''
        #return int(self._ask('ISRC?'))
        return 0
    def set_input_configuration(self, i):
        '''
        Sets the input configuration.
            i=0 : A
            i=1 : A-B
            i=2 : I (1 MOhm)
            i=3 : I (100 MOhm)

        Changing the current gain does not change the instrument sensitivity.
        Sensitivites above 10 nA require a current gain of 1 MOhm. Sensitivities
        between 20 nA and 1 uA automatically select the 1 MOhm current gain. At
        sensitivities below 20 nA, changing the sensitivity does not change the
        current gain.
        '''
        self._write('ISRC %d'%i)

    def get_input_shield_grounding(self):
        '''
        Gets the input shield grounding.
            i=0 : float
            i=1 : ground
        '''
        #return int(self._ask('IGND?'))
        return 1
    def set_input_shield_grounding(self, i):
        '''
        Sets the input shield grounding.
            i=0 : float
            i=1 : ground
        '''
        self._write('IGND %d'%i)

    def get_input_coupling(self):
        '''
        Gets the input coupling.
            i=0 : AC
            i=1 : DC
        '''
        #return int(self._ask('ICPL?'))
        return 0
    def set_input_coupling(self, i):
        '''
        Sets the input coupling.
            i=0 : AC
            i=1 : DC
        '''
        self._write('ICPL %d'%i)

    def get_input_line_filter(self):
        '''
        Gets the input line notch filter status.
            i=0 : no filters
            i=1 : line notch filter
            i=2 : 2x line notch filter
            i=3 : both notch filters
        '''
        #return int(self._ask('ILIN?'))
        return 3
    def set_input_line_filter(self, i):
        '''
        Sets the input line notch filter status.
            i=0 : no filters
            i=1 : line notch filter
            i=2 : 2x line notch filter
            i=3 : both notch filters
        '''
        self._write('ILIN %d'%i)

    # Gain and Time constant commands
    def get_sensitivity_index(self):
        '''
        Get the current sensitivity index.
            i=0  : 2 nV/fA
            i=1  : 5 nV/fA
            i=2  : 10 nV/fA
            i=3  : 20 nV/fA
            i=4  : 50 nV/fA
            i=5  : 100 nV/fA
            i=6  : 200 nV/fA
            i=7  : 500 nV/fA
            i=8  : 1 uV/pA
            i=9  : 2 uV/pA
            i=10 : 5 uV/pA
            i=11 : 10 uV/pA
            i=12 : 20 uV/pA
            i=13 : 50 uV/pA
            i=14 : 100 uV/pA
            i=15 : 200 uV/pA
            i=16 : 500 uV/pA
            i=17 : 1 mV/nA
            i=18 : 2 mV/nA
            i=19 : 5 mV/nA
            i=20 : 10 mV/nA
            i=21 : 20 mV/nA
            i=22 : 50 mV/nA
            i=23 : 100 mV/nA
            i=24 : 200 mV/nA
            i=25 : 500 mV/nA
            i=26 : 1 V/uA
        '''
        #return int(self._ask('SENS?'))
        return self.sensitivity

    def get_sensitivity_voltage(self):
        '''
        Get the current sensitivity voltage as a float.
        '''
        return self.sensitivity_voltages[self.get_sensitivity_index()]

    def get_sensitivity_current(self):
        '''
        Get the current sensitivity current as a float.
        '''
        return self.sensitivity_currents[self.get_sensitivity_index()]

    def set_sensitivity_index(self, i):
        '''
        Set the current sensitivity index.
            i=0  : 2 nV/fA
            i=1  : 5 nV/fA
            i=2  : 10 nV/fA
            i=3  : 20 nV/fA
            i=4  : 50 nV/fA
            i=5  : 100 nV/fA
            i=6  : 200 nV/fA
            i=7  : 500 nV/fA
            i=8  : 1 uV/pA
            i=9  : 2 uV/pA
            i=10 : 5 uV/pA
            i=11 : 10 uV/pA
            i=12 : 20 uV/pA
            i=13 : 50 uV/pA
            i=14 : 100 uV/pA
            i=15 : 200 uV/pA
            i=16 : 500 uV/pA
            i=17 : 1 mV/nA
            i=18 : 2 mV/nA
            i=19 : 5 mV/nA
            i=20 : 10 mV/nA
            i=21 : 20 mV/nA
            i=22 : 50 mV/nA
            i=23 : 100 mV/nA
            i=24 : 200 mV/nA
            i=25 : 500 mV/nA
            i=26 : 1 V/uA
        '''
        i = int(i)
        if i < 0 or i > 26:
            raise ValueError('Invalid sensitivity index: %d'%i)
        self._write('SENS %d'%i)
        self.sensitivity = i

    def set_sensitivity_voltage(self, V):
        '''
        Set the sensitivity for detection of the given voltage (in Volts).
        '''
        i = np.searchsorted(self.sensitivity_voltages, V*1.2)
        self.set_sensitivity_index(i)

    def set_sensitivity_current(self, I):
        '''
        Set the sensitivity for detection of the given current (in Amps).
        '''
        i = np.searchsorted(self.sensitivity_currents, I*1.2)
        self.set_sensitivity_index(i)

    #TODO: fix this to not use the built-in auto gain because it sucks
    # it results in kinks at the transitions.
    def auto_adjust_sensitivity(self):
        '''
        Auto-adjusts the sensitivity.
        '''
        # Store the current time constant
        ti = self.get_time_constant_index()
        tchanged = False
        # If the current time constant is greater than 1 second,
        # drop it down to 1 second for auto gain adjust
        if ti > 10:
            self.set_time_constant_index(10)
            tchanged = True
        # Run the auto gain adjust, and wait for it to finish
        self._write('AGAN')
        self.sensitivity = 10
        # Now wait for it to finish. Simply checking the serial poll
        # status byte seems to have this effect.
        self._ask('*STB?')
        # Restore the time constant, if it was changed
        if tchanged:
            self.set_time_constant_index(ti)

    def increment_sensitivity(self):
        self.set_sensitivity_index(self.get_sensitivity_index()+1)

    def decrement_sensitivity(self):
        self.set_sensitivity_index(self.get_sensitivity_index()-1)

    def get_reserve_mode(self):
        '''
        Gets the current reserve mode.
            i=0 : High Reserve
            i=1 : Normal
            i=2 : Low Noise (minimum)
        '''
        #return int(self._ask('RMOD?'))
        return 0
    def set_reserve_mode(self, i):
        '''
        Sets the reserve mode.
            i=0 : High Reserve
            i=1 : Normal
            i=2 : Low Noise (minimum)
        '''
        self._write('RMOD %d'%i)

    def get_time_constant_index(self):
        '''
        Gets the current time constant index.
            i=0 : 10 us
            i=1 : 30 us
            i=2 : 100 us
            i=3 : 300 us
            i=4 : 1 ms
            i=5 : 3 ms
            i=6 : 10 ms
            i=7 : 30 ms
            i=8 : 100 ms
            i=9 : 300 ms
            i=10 : 1 s
            i=11 : 3 s
            i=12 : 10 s
            i=13 : 30 s
            i=14 : 100 s
            i=15 : 300 s
            i=16 : 1 ks
            i=17 : 3 ks
            i=18 : 10 ks
            i=19 : 30 ks
        '''
        #return int(self._ask('OFLT?'))
        return self.time_constant
    def set_time_constant_index(self, i):
        '''
        Gets the current time constant index.
            i=0 : 10 us
            i=1 : 30 us
            i=2 : 100 us
            i=3 : 300 us
            i=4 : 1 ms
            i=5 : 3 ms
            i=6 : 10 ms
            i=7 : 30 ms
            i=8 : 100 ms
            i=9 : 300 ms
            i=10 : 1 s
            i=11 : 3 s
            i=12 : 10 s
            i=13 : 30 s
            i=14 : 100 s
            i=15 : 300 s
            i=16 : 1 ks
            i=17 : 3 ks
            i=18 : 10 ks
            i=19 : 30 ks
        '''
        i = int(i)
        if i < 0 or i > 19:
            raise ValueError('Invalid time constant index: %d'%i)
        self._write('OFLT %d'%i)
        self.time_constant = i

    def get_time_constant_seconds(self):
        return self.time_constant_seconds[self.get_time_constant_index()]
    def set_time_constant_seconds(self, s):
        i = np.searchsorted(self.time_constant_seconds, s)
        self.set_time_constant_index(i)

    def get_filter_slope(self):
        '''
        Gets the low pass filter slope.
            i=0 :  6 dB/oct
            i=1 : 12 dB/oct
            i=2 : 18 dB/oct
            i=3 : 24 dB/oct
        '''
        #return int(self._ask('OFSL?'))
        return 3
    def set_filter_slope(self, i):
        '''
        Sets the low pass filter slope.
            i=0 :  6 dB/oct
            i=1 : 12 dB/oct
            i=2 : 18 dB/oct
            i=3 : 24 dB/oct
        '''
        i = int(i)
        if i < 0 or i > 3:
            raise ValueError('Invalid filter slope index: %d'%i)
        self._write('OFSL %d'%i)

    #TODO: test these to see if 24 db/oct really takes twice
    # as long to settle. Simply goto the PL peak, block the laser
    # until the signal compeltely dies, then start plotting and
    # unblock the laser. Then watch how long it takes to reach a
    # steady value. Try this for 6 db/oct and 24 db/oct to see if the
    # settle time is really 2x. If it is, then we know that you really
    # should wait 10 time constants.
    def get_suggested_delay(self):
        '''
        Gets the suggested delay to reach 99% of actual value, based on the
        current time constant and filter slope.
        '''
        t = self.get_time_constant_seconds()
        i = self.get_filter_slope()
        if i == 0:
            return t*5
        elif i == 1:
            return t*7
        elif i == 2:
            return t*9
        elif i == 3:
            return t*10
        else:
            raise RuntimeError('unexpected execution path')

    # Data Transfer commands
    def get_outputs(self):
        #R, theta = self._ask('SNAP?3,4').split(',')
        #return float(R), float(theta)
        R = self.R[self.output_index]
        theta = self.theta[self.output_index]
        self.output_index += 1
        self.output_index %= self.R.size
        return float(R), float(theta)

    def adjust_and_get_outputs(self, delay=None):
        '''
        Use this to take care of sensitivity adjustments during a scan.
        If delay is none, the suggested value based on the current
        time constant and filter slope is used.
        
        Example usage:
        
            delay = sr830.get_time_constant_seconds()*5
            for wavelength in wavelengths:
                spectrometer.goto(wavelength)
                R, theta = sr830.adjust_and_get_outputs(delay)
                output(wavelenth, R, theta)
        '''
        if delay is None:
            delay = self.get_suggested_delay()
        time.sleep(delay/5) # quick adjust
        R, theta = self.get_outputs()
        i = self.get_sensitivity_index()
        if self.get_input_configuration() < 2:
            # voltage mode
            if i > 1 and R < self.sensitivity_voltages[i-1]*.65:
                self.set_sensitivity_index(i-1)
                return self.adjust_and_get_outputs(delay)
            if i < len(self.sensitivity_voltages) and R > self.sensitivity_voltages[i]*.75:
                self.set_sensitivity_index(i+1)
                return self.adjust_and_get_outputs(delay)
        else:
            # current mode
            if i > 1 and R < self.sensitivity_currents[i-1]*.65:
                self.set_sensitivity_index(i-1)
                return self.adjust_and_get_outputs(delay)
            if i < len(self.sensitivity_currents) and R > self.sensitivity_currents[i]*.75:
                self.set_sensitivity_index(i+1)
                return self.adjust_and_get_outputs(delay)

        # helps remove kinks
        time.sleep(delay)
        log.debug('get_outputs: return %g, %g'%(R, theta))
        return R, theta

    def get_noise(self):
        raise NotImplementedError() #TODO

if __name__ == "__main__":
    # enable DEBUG output
    logging.basicConfig(level=logging.DEBUG)

    # run tests
    sr830 = SR830()
