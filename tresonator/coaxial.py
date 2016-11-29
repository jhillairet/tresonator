# -*- coding: utf-8 -*-
"""
Coaxial Class
"""
import numpy as np
from . constants import *

class Coax(object):
    """
    Coaxial Line transmission line
    """
    def __init__(self, L, Dint, Dout,  eps_r=1, sigma=conductivity_Cu):
        """
        Coax transmission line. 
        
        Args
        ----
        L :     length [m]
        Dint:   inner diameter [m]
        Dout:   outer conductor diameter [m]
        eps_r:  relative permittivity of the medium between the two conductor (default=1)
        sigma:  conductor conductivity [S/m] (default is copper conductivty)
        
        """
        if Dint <= 0 or Dout <= 0 or L <= 0 or eps_r < 1 or sigma <= 0 or Dint == Dout:
            raise ValueError
        
        self.Dint = Dint
        self.Dout = Dout
        self.L = L
        self.eps_r = eps_r
        self.sigma = sigma
        
        # Characteristic impedance of the coaxial transmission line
        self.Zc = 1/(2*pi)*np.sqrt(mu_0/epsilon_0/self.eps_r) * \
                    np.log(self.Dout/self.Dint)
       
    def alpha(self, f):
        """
        Transmission line loss coefficient
        
        Args:
        ----
        f : float
            frequency in Hz
        """
        if f <= 0: raise ValueError
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
        if f <= 0: raise ValueError
        alpha = self.alpha(f)
        beta = 2*pi*f/c # TEM mode in coaxial -> vacuum wavenumber 
        gamma = alpha + 1j*beta
        return gamma
        
    def __repr__(self):
        return 'Coaxial line: Dint={}m,\t Dout={}m,\t L={} m, Zc={}, epsr={}, sigma={} MS/m'.format(\
                self.Dint, self.Dout, self.L, self.Zc, self.eps_r, self.sigma/1e6)
                
                


