# -*- coding: utf-8 -*-
"""
ICRF T-Resonator
  
Calculates the optimized variable length of both branches in order to
match the T-resonator.
 
Once an optimized configuration is found, calculates the current and
voltage distribution along both branches of the resonator.
"""
import tresonator as T
import matplotlib.pyplot as plt

f = 62.90e6 # Hz
P_in = 80e3 # W

# setup the initial resonator configuration, in which L_DUT and L_CEA
# are not the necessary optimum values
L_DUT = 0.0426 # m
L_CEA = 0.0686 # m
cfg = T.Configuration(f, P_in, L_DUT, L_CEA, additional_losses=1)


Zin, Z_CEA, Z_DUT = cfg.input_impedance()

L_CEA, L_DUT, V_CEA, V_DUT, I_CEA, I_DUT = cfg.voltage_current();


# Plotting results
L_Vprobe_CEA = 1.236;
L_Vprobe_DUT = 0.669;

fig, ax = plt.subplots(2,1, sharex=True)
ax[0].plot(-L_DUT, np.abs(V_DUT)/1e3, L_CEA, np.abs(V_CEA)/1e3, lw=2)
ax[0].set_ylim(0, 45)
ax[0].grid(True)
ax[0].set_xlim(min(-L_DUT), max(L_CEA))
ax[0].axvline(x=L_Vprobe_CEA, ls='--', color='gray', lw=3)
ax[0].axvline(x=-L_Vprobe_DUT, ls='--', color='gray', lw=3)
ax[0].set_xlabel('L [m]', fontsize=14)
ax[0].set_ylabel('|V| [kV]', fontsize=14)

ax[1].plot(-L_DUT, np.abs(I_DUT), L_CEA, np.abs(I_CEA), lw=2)
ax[1].set_ylim(0, 2500)
ax[1].grid(True)
ax[1].axvline(x=L_Vprobe_CEA, ls='--', color='gray', lw=3)
ax[1].axvline(x=-L_Vprobe_DUT, ls='--', color='gray', lw=3)
ax[1].set_xlabel('L [m]', fontsize=14)
ax[1].set_ylabel('|I| [A]', fontsize=14)