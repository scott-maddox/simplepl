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
import numpy as np
from scipy.integrate import quad

# local imports
from abstract_spectrum import AbstractSpectrum
from parameters import BoundedFloatParameter

kB = 8.6173324e-5 # eV / K

class AbstractSimulatedSpectrum(AbstractSpectrum):
    def __init__(self, *args, **kwargs):
        super(AbstractSimulatedSpectrum, self).__init__(*args, **kwargs)
        self.parameters = []
        self._energy = kwargs.get('energy', None)
    
    def _getEnergy(self):
        return self._energy
    
    def _setEnergy(self, energy):
        self._energy = energy
        self.sigChanged.emit()
    
    energy = QtCore.Property(np.ndarray, _getEnergy, _setEnergy)
    
    def _getWavelength(self):
        if self.energy is None:
            return None
        return 1239.842/self.energy
    
    def _setWavelength(self, wavelength):
        self._energy = 1239.842/wavelength
        self.sigChanged.emit()
    
    wavelength = QtCore.Property(np.ndarray, _getWavelength, _setWavelength)
    
    def _getIntensity(self):
        if self.energy is None:
            return None
        return self._calculateIntensity()
    
    intensity = QtCore.Property(np.ndarray, _getIntensity)
    
    def _calculateIntensity(self):
        raise NotImplementedError()

class ConstantSpectrum(AbstractSimulatedSpectrum):
    def __init__(self, *args, **kwargs):
        super(ConstantSpectrum, self).__init__(*args, **kwargs)
        self.constant = BoundedFloatParameter(label='A')
        self.parameters.append(self.constant)
        
        # Connect signals and slots
        self.constant.sigChanged.connect(self.sigChanged)
    
    @staticmethod
    def function(energy, c):
        return energy * 0. + c
    
    def getIntegral(self):
        return 0. # the background shouldn't contribute

    def _calculateIntensity(self):
        return self.function(self.energy, self.constant.value)

class AbstractPeakSpectrum(AbstractSimulatedSpectrum):
    def __init__(self, *args, **kwargs):
        super(AbstractPeakSpectrum, self).__init__(*args, **kwargs)
        
        #TODO: implement an absolute minimum that the user cannot change
        self.amplitude = BoundedFloatParameter(value=1., min=0., max=1.,
                                               label='A')
        self.center = BoundedFloatParameter(value=0., min=-1., max=1.,
                                            label='C')
        self.fwhm = BoundedFloatParameter(value=1., min=0., max=1.,
                                          label='W')
        
        self.parameters.append(self.amplitude)
        self.parameters.append(self.center)
        self.parameters.append(self.fwhm)
        
        # Connect signals and slots
        self.amplitude.sigChanged.connect(self.sigChanged)
        self.center.sigChanged.connect(self.sigChanged)
        self.fwhm.sigChanged.connect(self.sigChanged)
    
    def _calculateIntensity(self):
        return self.function(self.energy, self.amplitude.value,
                             self.center.value, self.fwhm.value)

class GaussianSpectrum(AbstractPeakSpectrum):
    @staticmethod
    def function(energy, a, c, w):
        return ( a * np.exp( -(energy - c)**2. / ( 2.* (w / 2.35482)**2. ) ) )
    
    def getIntegral(self):
        return self.amplitude.value * self.fwhm.value * np.sqrt(np.pi)

class LorentzianSpectrum(AbstractPeakSpectrum):
    @staticmethod
    def function(energy, a, c, w):
        return ( a / ( 1. + ( 2. * (energy - c) / w )**2. ) )
    
    def getIntegral(self):
        return self.amplitude.value * self.fwhm.value * np.pi / 2.

#        return ( self.amplitude.value / 
#                 ( 1. + ( 2. * (self.energy - self.center.value)
#                          / self.fwhm.value )**2. ) )

class AsymmetricGaussianSpectrum(AbstractSimulatedSpectrum):
    def __init__(self, *args, **kwargs):
        super(AsymmetricGaussianSpectrum, self).__init__(*args, **kwargs)
        
        #TODO: implement an absolute minimum that the user cannot change
        self.amplitude = BoundedFloatParameter(value=1., min=0., max=1.,
                                               label='A')
        self.center = BoundedFloatParameter(value=0., min=-1., max=1.,
                                            label='C')
        self.hwhm1 = BoundedFloatParameter(value=1., min=0., max=1.,
                                          label='W1')
        self.hwhm2 = BoundedFloatParameter(value=1., min=0., max=1.,
                                          label='W2')
        
        self.parameters.append(self.amplitude)
        self.parameters.append(self.center)
        self.parameters.append(self.hwhm1)
        self.parameters.append(self.hwhm2)
        
        # Connect signals and slots
        self.amplitude.sigChanged.connect(self.sigChanged)
        self.center.sigChanged.connect(self.sigChanged)
        self.hwhm1.sigChanged.connect(self.sigChanged)
        self.hwhm2.sigChanged.connect(self.sigChanged)
    
    def _calculateIntensity(self):
        return self.function(self.energy, self.amplitude.value,
                             self.center.value,
                             self.hwhm1.value, self.hwhm2.value)
    
    @staticmethod
    def function(energy, a, c, w1, w2):
        '''
        Assumes energy is a numpy array.
        '''
        # I want exp( - x**2 ) as x --> 0
        # and exp( - x ) as x --> -oo, oo
        def f(energy):
            if energy < c:
                return ( a * np.exp( -(energy - c)**2. / ( 2.* (2* w1 / 2.35482)**2. ) ) )
            else:
                return ( a * np.exp( -(energy - c)**2. / ( 2.* (2* w2 / 2.35482)**2. ) ) )
        result = np.empty_like(energy)
        for i in xrange(energy.size):
            result[i] = f(energy[i])
        return result
    
    def getIntegral(self):
        return self.amplitude.value * (self.hwhm1.value + self.hwhm2.value) * np.sqrt(np.pi)

class AbstractPLSpectrum(AbstractSimulatedSpectrum):
    def __init__(self, *args, **kwargs):
        super(AbstractPLSpectrum, self).__init__(*args, **kwargs)
        self.amplitude = BoundedFloatParameter(value=1., min=0., max=1.,
                                               label='A')
        self.bandgap = BoundedFloatParameter(value=0., min=-1., max=1.,
                                            label='Eg')
        self.temperature = BoundedFloatParameter(value=1., min=0., max=1.,
                                          label='T')
        
        self.parameters.append(self.amplitude)
        self.parameters.append(self.bandgap)
        self.parameters.append(self.temperature)
        
        # Connect signals and slots
        self.amplitude.sigChanged.connect(self.sigChanged)
        self.bandgap.sigChanged.connect(self.sigChanged)
        self.temperature.sigChanged.connect(self.sigChanged)
    
    def _calculateIntensity(self):
        return self.function(self.energy, self.amplitude.value,
                             self.bandgap.value, self.temperature.value)
    
    def getIntegral(self):
        return quad(self.function, self.bandgap.value, np.inf,
                    (self.amplitude.value, self.bandgap.value,
                     self.temperature.value))[0]

class WaveVectorConservingPLSpectrum(AbstractPLSpectrum):
    @staticmethod
    def function(energy, A, Eg, T):
        if T <= 0:
            return energy * 0.
        scale = A / ( np.sqrt(.5*kB*T) * np.exp(-.5))
        E = energy.astype(np.complex128)
        result = scale * np.sqrt(E - Eg) * np.exp(-(energy - Eg)/(kB*T))
        return result.real

class WaveVectorNonConservingPLSpectrum(AbstractPLSpectrum):
    @staticmethod
    def function(energy, A, Eg, T):
        if T <= 0:
            return energy * 0.
        scale = A / ( (2.*kB*T)**2. * np.exp(-2.))
        #E = energy.astype(np.complex128)
        result = scale * (energy - Eg)**2. * np.exp(-(energy - Eg)/(kB*T))
        step_function = 0.5 * (np.sign(energy - Eg) + 1)
        result *= step_function
        #return result.real
        return result