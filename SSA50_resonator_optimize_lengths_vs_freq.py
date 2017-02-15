# -*- coding: utf-8 -*-
"""
Calculates and display the optimized short lengths of the T-resonator vs frequency
"""
import tresonator as T
import matplotlib.pyplot as plt
import numpy as np

# T-resonator configuration 
P_in = 80e3 # W
add_loss = 1.2

# Frequency range
freqs = np.linspace(61e6, 63e6, 201)

# For all frequencies, calculate the optimized short lengths (the 2 solutions)
L_CEA_opt1, L_CEA_opt2 = [], [] 
L_DUT_opt1, L_DUT_opt2 = [], []

for freq in freqs:
    # initiate a configuration with dummy lengths
    _cfg = T.Configuration(freq, P_in, 0.05, 0.05, additional_losses=add_loss)
    L_opt1 = _cfg.optimize_short_lengths()
    while True:
        L_opt2 = _cfg.optimize_short_lengths()
        if np.isclose(L_opt1[0], L_opt2[0]) or \
            np.isclose(L_opt1[1], L_opt2[1]):
                pass
        else:
            L_DUT_opt1.append(np.min([L_opt1[0], L_opt2[0]]))
            L_DUT_opt2.append(np.max([L_opt1[0], L_opt2[0]]))    
            L_CEA_opt1.append(np.min([L_opt1[1], L_opt2[1]]))
            L_CEA_opt2.append(np.max([L_opt1[1], L_opt2[1]]))
            print(freq/1e6)
            break
    
            


fig, ax = plt.subplots(1,1)
ax.plot(freqs/1e6, L_DUT_opt1, '.')
ax.plot(freqs/1e6, L_CEA_opt1, '.')
ax.plot(freqs/1e6, L_DUT_opt2, '.') 
ax.plot(freqs/1e6, L_CEA_opt2, '.')
ax.legend(('DUT sol 1', 'CEA sol 1', 'DUT sol 2', 'CEA sol 2')) 
ax.grid(True)
ax.set_xlabel('f [MHz]', fontsize=14)
ax.set_ylabel('Short length [m]', fontsize=14)