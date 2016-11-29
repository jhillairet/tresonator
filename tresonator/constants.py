# -*- coding: utf-8 -*-
"""
Usefull constants
"""
from scipy.constants import c, mu_0, epsilon_0, pi
import numpy as np

# Vacuum impedance
Z0 = np.sqrt(mu_0/epsilon_0)

# Conductors conductivity [Siemens/m]
conductivity_SS = 1.32e6 # 1.45e6 in Wikipedia
conductivity_Cu = 5.8e7 # Annealed copper.  5.96e7 for pure Cu in Wikipedia
conductivity_Ag = 6.3e7 # Wikipedia

