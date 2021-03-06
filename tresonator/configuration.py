# -*- coding: utf-8 -*-
"""
Configuration of the T-resonator
"""
from . constants import *
from . coaxial import Coax
from . transmission_line_utils import ZL_2_Zin, transfer_matrix
from scipy.optimize import minimize
import numpy as np
import skrf as rf
from skrf.media import Coaxial


class Configuration(object):
    """
    T-resonator configuration.
    
    Args:
    -----
    f:  float>0
        frequency [Hz]
    P_in: float>0
        input power [W]
    L_DUT: float>0
        short length at DUT side branch
    L_CEA: float>0
        short length at CEA side branch
    additional_losses: float
        Multiplicative factor to propagation losses
    """            
    def __init__(self, f, P_in, L_DUT, L_CEA, 
                 Z_short_DUT=1e-2, Z_short_CEA=1e-2, additional_losses=1):
        # Source frequency [Hz]
        self.f = f 
        
        # Input power [W]
        self.P_in = P_in
        
        # Branches end lengths
        self.L_DUT = L_DUT
        self.L_CEA = L_CEA
        
        # Short Impedance [Ohm] 
        self.Z_short_DUT = Z_short_DUT
        self.Z_short_CEA = Z_short_CEA
        
        # feeder impedance 
        self.R = 29.8 # Ohm
        # Location of voltage probes on the resonator (starting from T)
        self.L_Vprobe_CEA_fromT = 1.236
        self.L_Vprobe_DUT_fromT = 0.669
        
        # Maximum number of iterations during a short lengths optimization
        self.NB_ITER_MAX = 5000
        
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
        TLs.append(Coax(   1100e-3, 0.1683, 0.230, sigma=conductivity_Cu)) # was ZCinter=18.62 and Linter=1.1
        TLs.append(Coax(   1021e-3, 0.140,  0.230, sigma=conductivity_Cu)) # 1021.5e-3 = 2.1215-Linter
        TLs.append(Coax(    100e-3, 0.100,  0.230, sigma=conductivity_Ag)) # was ZC4=49.94 ### ZC for small reduction copper plating
        TLs.append(Coax(    114e-3, 0.140,  0.230, sigma=conductivity_Ag))
        
        # CEA Branch
        TLs.append(Coax(    728e-3, 0.140,  0.230, sigma=conductivity_Ag)) # coude
        TLs.append(Coax(    100e-3, 0.100,  0.230, sigma=conductivity_Ag))
        TLs.append(Coax(   1512e-3, 0.140,  0.230, sigma=conductivity_SS))
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
    
    def S11(self):
        """
        Returns the S11 of the T-resonator at a given frequency
        
        Returns
        -------
        S11 : 
        """
        Zin, _ , _ = self.input_impedance()
        
        S11 = (Zin - self.R)/(Zin + self.R)
        
        return S11
        
    def S11dB(self):
        return 20*np.log10(np.abs(self.S11()))
        
        
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
        L_CEA, V_CEA, I_CEA, Z_CEA = self._voltage_current_branch(Zin, Z_CEA[-1], TL_indexes_CEA)
        L_DUT, V_DUT, I_DUT, Z_DUT = self._voltage_current_branch(Zin, Z_DUT[-1], TL_indexes_DUT)
        
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
    
    def optimize_short_lengths(self, bounds=[(1e-3,200e-3),(1e-3,200e-3)]):
        """
        Solve the matching problem in order to find the length of the variable
        section of the CEA and DUT branches.
        
        Arguments
        ---------
        bounds : list of 2-tuples
            Search bounds for L_DUT and L_CEA
            [(L_DUT min, L_DUT max), (L_CEA min, L_CEA max)]
            default : [(1e-3,1),(1e-3,1)]
            
        Returns
        -------
        L: tuple
           optimized short lengths (L_DUT, L_CEA)
        """
        
        L_opt = self._search_short_lengths(bounds)
        if L_opt is not None:
            return L_opt
        else:
            raise ValueError('No solution found !')

    def _search_short_lengths(self, bounds):
        """
        Optimization routine on T-resonator variable length (CEA and DUT branches)
        """
    
        # In order to get a correct solution, repeats the minimize call
        # until a physical solution is found        
        random_lengths = 0 + (0.5 - 0)*np.random.rand(2, self.NB_ITER_MAX)
               
        for nb_iter in range(self.NB_ITER_MAX):
            L0 = random_lengths[:,nb_iter]   
            res = minimize(self._optim_fun_impedance_matching, L0,
                           bounds=bounds,
                           options={'maxiter':self.NB_ITER_MAX})
            if res.success:
                if np.isclose(res.x[0], 1e-3) or np.isclose(res.x[1], 1e-3):
                    pass # length too low ->  Repeat
                elif np.isclose(res.x[0], 1) or np.isclose(res.x[1], 1):
                    pass # length too high ->  Repeat
                else:
                    L_opt = res.x
                    print('Solution found: L={}'.format(L_opt))
                    break # True good solution found
        else:
            print('No solution found !')
            L_opt = None
        return L_opt


    def _optim_fun_impedance_matching(self, L):
        _cfg = Configuration(self.f, self.P_in, L_DUT=L[0], L_CEA=L[1], 
                            additional_losses=self.additional_losses)
        # Minimize the return loss
        S11 = np.abs(_cfg.S11())
        return S11 
        

    def circuit(self, freq=None):
        """
        Returns the circuit object of the corresponding configuration
    
        Returns
        -------
        None.
    
        """
        
        Z_short_DUT = 1e-2 
        Z_short_CEA = 1e-2
        
        if not freq:
            freq = rf.Frequency(self.f, unit='Hz', npoints=1)
        
        # DUT Branch
        # NB : CEA: Dout/Dint=219/140 -> 26.82 Ohm 
        #      SSA13, CCFE Home-made: 219/126 -> 33.14 Ohm
        #      SSA50: 219/127.92 -> 32.2 Ohm
        D4_ = Coaxial(frequency=freq, Dint=0.1279, Dout=0.219, epsilon_r=1, sigma=conductivity_Cu)
        D4 = D4_.line(self.L_DUT, unit='m', name='D4')        
        D3 = Coaxial(frequency=freq, Dint=0.1683, Dout=0.230, epsilon_r=1, sigma=conductivity_Cu).line(1100e-3, unit='m', name='D3')
        D2 = Coaxial(frequency=freq, Dint=0.140,  Dout=0.230, epsilon_r=1, sigma=conductivity_Cu).line(1021e-3, unit='m', name='D2')
        D1 = Coaxial(frequency=freq, Dint=0.100,  Dout=0.230, epsilon_r=1, sigma=conductivity_Ag).line(100e-3, unit='m', name='D1')
        D0 = Coaxial(frequency=freq, Dint=0.140,  Dout=0.230, epsilon_r=1, sigma=conductivity_Ag).line(114e-3, unit='m', name='D0')
        
        # CEA Branch
        C0 = Coaxial(frequency=freq, Dint=0.140,  Dout=0.230, epsilon_r=1, sigma=conductivity_Ag).line(728e-3, unit='m', name='C0') # coude
        C1 = Coaxial(frequency=freq, Dint=0.100, Dout=0.230, epsilon_r=1, sigma=conductivity_Ag).line(100e-3, unit='m', name='C1')
        C2 = Coaxial(frequency=freq, Dint=0.140, Dout=0.230, epsilon_r=1, sigma=conductivity_SS).line(1512e-3, unit='m', name='C2')
        C3_ = Coaxial(frequency=freq, Dint=0.140, Dout=0.219, epsilon_r=1, sigma=conductivity_Cu)
        C3 = C3_.line(self.L_CEA, unit='m', name='C3')
        
        port1 = rf.Circuit.Port(frequency=freq, z0=self.R, name='port1')
        resistor_dut = D4_.resistor(self.Z_short_DUT, name='short_dut')
        resistor_cea = C3_.resistor(self.Z_short_CEA, name='short_cea')
        gnd_dut = rf.Circuit.Ground(frequency=freq, z0=D4_.z0[0], name='gnd_dut')
        gnd_cea = rf.Circuit.Ground(frequency=freq, z0=C3_.z0[0], name='gnd_cea')
        
        cnx = [
            # T-junction
            [(port1, 0), (D0, 0), (C0, 0)],
            # DUT Branch
            [(D0, 1), (D1, 0)],
            [(D1, 1), (D2, 0)],
            [(D2, 1), (D3, 0)],
            [(D3, 1), (D4, 0)],
            [(D4, 1), (resistor_dut, 0)],
            [(resistor_dut, 1), (gnd_dut, 0)],
            # CEA branch
            [(C0, 1), (C1, 0)],
            [(C1, 1), (C2, 0)],
            [(C2, 1), (C3, 0)],
            [(C3, 1), (resistor_cea, 0)],
            [(resistor_cea, 1), (gnd_cea, 0)],
        ]
        circuit = rf.Circuit(cnx)
        
        return circuit