# -*- coding: utf-8 -*-
"""
ICRF T-Resonator
  
Calculates the voltage and current and S11 for a given configuration
 """
import tresonator as T
import matplotlib.pyplot as plt
import numpy as np

f = 62.64e6 # Hz
P_in = 80e3 # W

# setup the initial resonator configuration, in which L_DUT and L_CEA
# are not the necessary optimum values
Lsc_DUT = 0.035 # m
Lsc_CEA = 0.027 # m


cfg = T.Configuration(f, P_in, Lsc_DUT, Lsc_CEA, additional_losses=1)

# Calculates the voltage and current along the transmission lines
L_CEA, L_DUT, V_CEA, V_DUT, I_CEA, I_DUT = cfg.voltage_current()
    
# Plotting V,I
fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(-L_DUT, np.abs(V_DUT)/1e3, L_CEA, np.abs(V_CEA)/1e3, lw=2)
ax[0].set_ylim(0, 45)
ax[0].grid(True)
ax[0].set_xlim(min(-L_DUT), max(L_CEA))
ax[0].axvline(x=cfg.L_Vprobe_CEA_fromT, ls='--', color='gray', lw=3)
ax[0].axvline(x=-cfg.L_Vprobe_DUT_fromT, ls='--', color='gray', lw=3)
ax[0].set_ylabel('|V| [kV]', fontsize=14)

ax[1].plot(-L_DUT, np.abs(I_DUT), L_CEA, np.abs(I_CEA), lw=2)
ax[1].set_ylim(0, 2500)
ax[1].grid(True)
ax[1].axvline(x=cfg.L_Vprobe_CEA_fromT, ls='--', color='gray', lw=3)
ax[1].axvline(x=-cfg.L_Vprobe_DUT_fromT, ls='--', color='gray', lw=3)
ax[1].set_xlabel('L [m]', fontsize=14)
ax[1].set_ylabel('|I| [A]', fontsize=14)


# Calculates the S11 for a range of frequency
freqs = np.linspace(61e6, 64e6, 101)
S11 = []
for freq in freqs:
    _cfg = T.Configuration(freq, P_in, Lsc_DUT, Lsc_CEA, additional_losses=1)
    S11.append( _cfg.S11dB() )
S11 = np.asarray(S11)

# Plotting S11
fig, ax = plt.subplots(1,1)
ax.plot(freqs/1e6, S11, lw=2)
ax.grid(True)
ax.set_xlabel('Frequency [MHz]', fontsize=14)
ax.set_ylabel('S11 [dB]', fontsize=14)