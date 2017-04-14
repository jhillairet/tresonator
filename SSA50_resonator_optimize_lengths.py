# -*- coding: utf-8 -*-
"""
ICRH T-resonator

Solve the short-circuit lengths at a given frequency. 

"""
import tresonator as T
import matplotlib.pyplot as plt
import numpy as np

f = 62.64e6 # Hz
P_in = 20e3 # W
add_loss = 1.0

# setup the initial resonator configuration, in which L_DUT and L_CEA
# are not the necessary optimum values
Lsc_DUT = 0.05 # m
Lsc_CEA = 0.03 # m

cfg = T.Configuration(f, P_in, Lsc_DUT, Lsc_CEA, additional_losses=add_loss)

# Solve the optimization problem
L_opt = cfg.optimize_short_lengths()
while True: # repeat searches until a physical meaningfull solution is found...
    if L_opt[0] < 20e-3 or L_opt[0] > 60e-3:
        L_opt = cfg.optimize_short_lengths()
    else:
        break

# Calculates the S11 for a range of frequency
freqs = np.linspace(61e6, 64e6, 301)
S11, Zin = [], []
for freq in freqs:
    cfg_opt = T.Configuration(freq, P_in, L_opt[0], L_opt[1], additional_losses=add_loss)
    _Zin, _ , _ = cfg_opt.input_impedance()
    S11.append( cfg_opt.S11dB() )
    Zin.append( _Zin )
S11 = np.asarray(S11)
Zin = np.asarray(Zin)

# Plotting S11
fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(freqs/1e6, np.real(Zin), 
           freqs/1e6, np.imag(Zin), lw=2)
ax[0].grid(True)
ax[0].set_ylabel('Z in [Ohm]', fontsize=14)

ax[1].plot(freqs/1e6, S11,lw=2)
ax[1].grid(True)
ax[1].set_xlabel('Frequency [MHz]', fontsize=14)
ax[1].set_ylabel('S11 [dB]', fontsize=14)