# -*- coding: utf-8 -*-
"""
Coaxial Class
"""
import numpy as np
from . constants import *

class Coax(object):
    """
    Coaxial Line Section
    """
    def __init__(self, Dint, Dout, L, eps_r=1, sigma=conductivity_Cu):
        self.Dint = Dint
        self.Dout = Dout
        self.L = L
        self.eps_r = eps_r
        self.sigma = sigma
        
        # Characteristic impedance of the coaxial transmission line
        self.Zc = 1/(2*pi)*np.sqrt(mu_0/epsilon_0/self.eps_r) \
                    *np.log(self.Dout/self.Dint)
       
    def alpha(self, f):
        """
        Transmission line loss coefficient
        
        Args:
        ----
        f : float
            frequency in Hz
        """
        # RF sheet resistance of conductors
        omega = 2*pi*f
        Rs = np.sqrt(omega*mu_0/(2*self.sigma))
        # Transmission Line Losses
        alpha = Rs/pi*(1/self.Dint + 1/self.Dout) / (2*self.Zc)
        
        return alpha
        
    def gamma(self, f):
        """
        Transmission line propagation constant (wavenumber)
        """
        alpha = self.alpha(f)
        beta = 2*pi*f/c # TEM mode in coaxial -> vacuum wavenumber 
        gamma = alpha + 1j*beta
        return gamma
        
    def __repr__(self):
        return 'Coaxial line: Dint={}m,\t Dout={}m,\t L={} m, epsr={}, sigma={} MS/m'.format(\
                self.Dint, self.Dout, self.L, self.eps_r, self.sigma/1e6)
                
                


