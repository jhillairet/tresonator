# -*- coding: utf-8 -*-
"""
ICRF T-Resonator
  
Calculates the optimized variable length of both branches in order to
match the T-resonator.
 
Once an optimized configuration is found, calculates the current and
voltage distribution along both branches of the resonator.
"""
import tresonator as T

f = 62.90e6 # Hz
P_in = 100 # W

# setup the initial resonator configuration, in which L_DUT and L_CEA
# are not the necessary optimum values
L_DUT = 0.0437 # m
L_CEA = 0.0736 # m
cfg = T.Configuration(f, P_in, L_DUT, L_CEA)


Zin, Z_CEA, Z_DUT = cfg.input_impedance()

L_CEA, L_DUT, V_CEA, V_DUT, I_CEA, I_DUT = cfg.voltage_current();

