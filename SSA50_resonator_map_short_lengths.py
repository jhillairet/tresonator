# -*- coding: utf-8 -*-
"""
Map the short lengths for a given frequency
"""
import tresonator as T
import matplotlib.pyplot as plt
import numpy as np


f = 62.90e6 # Hz
P_in = 80e3 # W
add_loss = 1

# short lengths to map
L_CEA = np.linspace(1e-3, 0.2, num=201)
L_DUT = np.linspace(1e-3, 0.1, num=201)

# calculates the S11 and Zin for all the short lengths
S11dB = np.zeros( (len(L_DUT), len(L_CEA)) )
Zin = np.zeros_like(S11dB, dtype='complex')

for idx_DUT, _L_DUT in enumerate(L_DUT):
    for idx_CEA, _L_CEA in enumerate(L_CEA):
        _cfg = T.Configuration(f, P_in, L_DUT=_L_DUT, L_CEA=_L_CEA, additional_losses=add_loss)
        S11dB[idx_DUT, idx_CEA] = _cfg.S11dB()
        _Zin, _ , _ = _cfg.input_impedance()
        Zin[idx_DUT, idx_CEA] = _Zin

# Plotting S11 vs L_DUT and L_CEA        
f,ax=plt.subplots(1,1)
cx=ax.contourf(L_DUT, L_CEA, S11dB.T, 50, cmap='afmhot')
plt.colorbar(cx)
ax.set_xlabel('L DUT [m]', fontsize=14)
ax.set_ylabel('L CEA [m]', fontsize=14)

L = _cfg.optimize_short_lengths()
ax.axvline(L[0], color='gray')
ax.axhline(L[1], color='gray')