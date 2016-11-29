# -*- coding: utf-8 -*-
"""
Transmission Line helper functions
"""
import numpy as np

def ZL_2_Zin(L,Z0,gamma,ZL):
    """
    Returns the input impedance seen through a lossy transmission line of
    characteristic impedance Z0 and complex wavenumber gamma=alpha+j*beta
             
    Zin = ZL_2_Zin(L,Z0,gamma,ZL)
    
    Args
    ----
    L : length [m] of the transmission line
    Z0: characteristic impedance of the transmission line
    gamma: complex wavenumber associated to the transmission line
    ZL: Load impedance

    Returns
    -------
    Zin: input impedance
    """
    Zin = Z0*(ZL + Z0*np.tanh(gamma*L))/(Z0 + ZL*np.tanh(gamma*L))
    return Zin

def transfer_matrix(L,V0,I0,Z0,gamma):
    """
    Returns the voltage and the current at a distance L from an
    initial voltage V0 and current I0 on a transmission line which
    propagation constant is gamma.
     
    VL, IL = transfer_matrix(L,V0,I0,Z0,gamma)
     
    L is positive from the load toward the generator
      
    Args
    -----
    L  : transmission line length [m]
    V0: initial voltage [V]
    I0: initial current [A]
    Z0 : characteristic impedance of the transmission line
    gamma: =alpha+j*beta propagation constant of the transmission line
    
    Returns
    --------
    VL: voltage at length L
    IL: current at length L
    """
    
    Transfer_matrix = np.array([[np.cosh(gamma*L), Z0*np.sinh(gamma*L)], 
                                [np.sinh(gamma*L)/Z0, np.cosh(gamma*L)]])
    A = Transfer_matrix.dot(np.array([[V0],[I0]]))              
    VL = A[0]
    IL = A[1]
    return VL, IL

def V0f_2_VL(L, V0f, gamma, reflection_coefficient):
    """
    Propagation of the voltage at a distance L from the forward
    voltage and reflection coefficient
     
    VL = V0f_2_VL(L, V0f, gamma, reflectionCoefficient)
     
    Args
    ----
    L : Transmission Line Length [m]
    V0f : forward voltage [V]
    gamma : Transmission Line Complex Propagatioon Constant [1]
    reflectionCoefficient : complex reflection coefficient [1]
    
    Returns
    --------
    VL : (total) voltage at length L 
    """ 
    VL = V0f*(np.exp(-gamma*L) + reflection_coefficient*np.exp(+gamma*L))
    return VL       
    
