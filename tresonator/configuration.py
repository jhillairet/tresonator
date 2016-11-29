# -*- coding: utf-8 -*-
"""
Configuration of the T-resonator
"""
from . constants import *
from . coaxial import Coax
from . transmission_line_utils import ZL_2_Zin, transfer_matrix
import numpy as np

class Configuration(object):
    def __init__(self, f, P_in, L_DUT, L_CEA, additional_losses=1):
                
        # Source frequency [Hz]
        self.f = f 
        
        # Input power [W]
        self.P_in = P_in
        
        # Branches end lengths
        self.L_DUT = L_DUT
        self.L_CEA = L_CEA
        
        # Short Impedance [Ohm] 
        self.Z_short_DUT = 0.0052 
        self.Z_short_CEA = 0.0087 
        
        # feeder impedance 
        self.R = 29.8 # Ohm
        
        # relative additional loss coefficient to multiply with the loss in the
        # coaxial transmission line, in order to match measurements 
        # example : +20# losses --> 1.2
        self.additional_losses = additional_losses 
        
        self.TLs, self.gammas = self._resonator_config()

    def __repr__(self):
        return 'T-resonator config: f={} MHz, P_in={} kW, L_DUT={} m, L_CEA={} m'.format( \
                     self.f/1e6, self.P_in/1e3, self.L_DUT, self.L_CEA)

    def _resonator_config(self):
        """
        Default resonator configuration
        """
       
        # Resonator TL section description
        #
        # Item      Length(mm)	Zc(Ohm) Inner/Outer Diam(m)	Inner   Outer
        # ---------------------------------------------------------------------
        # L1(DUT)	Variable	    26.83   0.140,0.219         SS      SS  CEA extension
        # or
        # SSA13:
        # L1(DUT)	Variable	    33.14   0.126,0.219         Au      SS  DUT extension  
        # SSA50:
        # L1(DUT)	Variable	    32.20   0.12792,0.219       Cu      SS  DUT extension  
        # L2     	  1100       18.72   0.1683,0.23         Cu      Cu
        # L3        1021.5     29.8    0.14,0.23           Cu      Cu
        # L4        100        49.5    0.1,0.23            Ag      Ag
        # L5        114        29.8    0.14,0.23           Ag      Ag
        # L6        661.2      29.8    0.14,0.23           Ag      Ag
        # L7        100        49.94   idem  L4            Ag      Ag
        # L8        1497.5     29.8    0.14,0.23           SS      SS
        # L9(CEA)   Variable	26.82   0.140,0.219         SS      SS
        #
        
        TLs = []
        # DUT Branch
        # Characteristic Impedance of the last DUT section (L1)
        # NB : CEA: Dout/Dint=219/140 -> 26.82 Ohm 
        #      SSA13, CCFE Home-made: 219/126 -> 33.14 Ohm
        #      SSA50: 219/127.92 -> 32.2 Ohm
        TLs.append(Coax(self.L_DUT, 0.1279, 0.219, sigma=conductivity_Cu))
        TLs.append(Coax(   1066e-3, 0.1683, 0.230, sigma=conductivity_Cu)) # was ZCinter=18.62 and Linter=1.1
        TLs.append(Coax(   1033e-3, 0.140,  0.230, sigma=conductivity_Cu)) # 1021.5e-3 = 2.1215-Linter
        TLs.append(Coax(    100e-3, 0.100,  0.230, sigma=conductivity_Ag)) # was ZC4=49.94 ### ZC for small reduction copper plating
        TLs.append(Coax(    120e-3, 0.140,  0.230, sigma=conductivity_Ag))
        
        # CEA Branch
        TLs.append(Coax(    687e-3, 0.140,  0.230, sigma=conductivity_Ag)) # coude
        TLs.append(Coax(    100e-3, 0.100,  0.230, sigma=conductivity_Ag))
        # Dans le code d'Arnaud, une section de ligne supplementaire de 0.016m/ZC2/gamma_copper est
        # ajoutee ici entre 7 et 8. Cette section n'est pas d??crite dans la documentation D0&D1. 
        # Est-ce le bellows ?
        TLs.append(Coax(   1513e-3, 0.140,  0.230, sigma=conductivity_SS))
        TLs.append(Coax(self.L_CEA, 0.140,  0.219, sigma=conductivity_SS))
        
        # Calculate the losses for each section
        
        gammas = []        
        for TL in TLs:
            gamma = TL.gamma(self.f, self.additional_losses)
            gammas.append(gamma)
            
        return TLs, gammas


    def input_impedance(self):
        """
        Calculate the input impedance of the T-resonator
         
        Args
        -----        
        None
        
        Returns
        -------
        Zin:    input impedance of the T-resonator
        Z_CEA:  input impedances at each sections of the CEA branch, from short to T
        Z_DUT:  input impedances at each sections of the DUT branch, from short to T   
        """        
        
        # DUT BRANCH
        Z_DUT = []
        Z_DUT.append(ZL_2_Zin(self.TLs[0].L, self.TLs[0].Zc, self.gammas[0], self.Z_short_DUT))
        Z_DUT.append(ZL_2_Zin(self.TLs[1].L, self.TLs[1].Zc, self.gammas[1], Z_DUT[0]))
        Z_DUT.append(ZL_2_Zin(self.TLs[2].L, self.TLs[2].Zc, self.gammas[2], Z_DUT[1]))
        Z_DUT.append(ZL_2_Zin(self.TLs[3].L, self.TLs[3].Zc, self.gammas[3], Z_DUT[2]))
        Z_DUT.append(ZL_2_Zin(self.TLs[4].L, self.TLs[4].Zc, self.gammas[4], Z_DUT[3]))
        
        # CEA BRANCH
        Z_CEA = []
        Z_CEA.append(ZL_2_Zin(self.TLs[8].L, self.TLs[8].Zc, self.gammas[8], self.Z_short_CEA))# 9
        Z_CEA.append(ZL_2_Zin(self.TLs[7].L, self.TLs[7].Zc, self.gammas[7], Z_CEA[0])) # 8
        Z_CEA.append(ZL_2_Zin(self.TLs[6].L, self.TLs[6].Zc, self.gammas[6], Z_CEA[1])) # 7
        Z_CEA.append(ZL_2_Zin(self.TLs[5].L, self.TLs[5].Zc, self.gammas[5], Z_CEA[2])) # 6
        
        # At T-junction. Impedance are associated in parallel.
        Zin = (Z_DUT[-1]*Z_CEA[-1])/(Z_DUT[-1] + Z_CEA[-1])
        
        return Zin, Z_CEA, Z_DUT
        
        
    def voltage_current(self):
        """ 
        Returns the voltage and current along the resonator. 
        
        Returns
        -------
        L_CEA: length 
        L_DUT:
        V_CEA:
        V_DUT: 
        I_CEA:
        I_DUT:
        """
        Zin, Z_CEA, Z_DUT = self.input_impedance()
        
        # Corresponding Transmission Line Section indexes
        TL_indexes_DUT = [4,3,2,1,0]
        TL_indexes_CEA = [5,6,7,8]

        # calculate the voltage and current along the T-resonator branches
        L_CEA, V_CEA, I_CEA, Z_CEA = self._voltage_current_branch(Zin, Z_CEA[3], TL_indexes_CEA)
        L_DUT, V_DUT, I_DUT, Z_DUT = self._voltage_current_branch(Zin, Z_DUT[4], TL_indexes_DUT)
        
        return L_CEA, L_DUT, V_CEA, V_DUT, I_CEA, I_DUT
        
    def _voltage_current_branch(self, Zin, Zbranch, TL_indexes):
        # spatial sampling 
        dl = 1e-3   
        # Input voltage from input power and feeder impedance
        Vin = np.sqrt(self.P_in*2*self.R) # forward voltage
        rho_in = (Zin - self.R)/(Zin + self.R) # reflection coefficient
        
        # arrays of initial voltage and current for each line section
        V0, I0 = [], []
        # arrays along L
        V, I, Z, L_full = [], [], [], []

        # Going from T to short 
        V0.append( Vin*(1 + rho_in) ) # total voltage
        I0.append( V0[0]/Zbranch)
        
        # For each transmission line section,
        # propagates the V,I,Z from the last section values to the length of current section
        for TL_index in TL_indexes:
            _L = np.arange(start=0, stop=self.TLs[TL_index].L, step=dl)         
            for l in _L:
                _V, _I = transfer_matrix(-l, V0[-1], I0[-1], self.TLs[TL_index].Zc, self.gammas[TL_index])
                V.append(_V)
                I.append(_I)
                Z.append(_V/_I)
            # cumulate the length array    
            if L_full:
                L_full.append(_L + L_full[-1][-1])
            else:
                L_full.append(_L) # 1st step
            # section intersection values
            V0.append( V[-1] )
            I0.append( I[-1] )
        
        # convert list into arrays
        V = np.asarray(V)
        I = np.asarray(I)
        Z = np.asarray(Z)
        L = np.concatenate(np.asarray([np.asarray(_L) for _L in L_full]))
        
        return L, V, I, Z
    
