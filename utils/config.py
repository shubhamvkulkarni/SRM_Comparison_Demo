#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/config.py

"""
Global configuration for SRM air quality toy model

This file defines all model parameters and initial conditions.

IMPORTANT:
This module is imported as:
    from utils import config

so that parameters can be modified dynamically (e.g. SAI_strength, emissions).

---

🔹 Governing equation:

    dC/dt = E - λC + Transport

where:
    C = concentration
    E = emissions
    λ = removal rate

Transport consists of:
    Horizontal mixing:
        T_h = k_h (C_other - C)

    Vertical exchange:
        T_v = k_v (C_strat - C)

---

🔹 SRM representation:

Stratospheric aerosol injection (SAI) modifies transport:

    k = k_base (1 + α * SAI_strength)

where:
    α = sensitivity parameter
    SAI_strength = strength of SRM forcing

Negative α → reduced mixing (physically plausible for strat heating effects)
"""

# -------------------------
# Time settings
# -------------------------
dt = 1.0            # time step
n_steps = 200       # number of time steps

# -------------------------
# Emissions (control variables)
# -------------------------
E_A = 1.0           # Region A (high emissions)
E_B = 0.3           # Region B (low emissions)

# -------------------------
# Removal (first-order decay)
# -------------------------
lambda_removal = 0.1

# Removal term:
#     R = -λC

# -------------------------
# Transport parameters
# -------------------------
base_k_vertical = 0.05    # strat ↔ trop exchange
base_k_horizontal = 0.1   # A ↔ B mixing

# Transport terms:
#     T_v = k_v (C_strat - C)
#     T_h = k_h (C_other - C)

# -------------------------
# SRM parameters
# -------------------------
SAI_strength = 0.0        # 0 = no SRM

alpha_vertical = -0.5     # SRM effect on vertical transport
alpha_horizontal = -0.3   # SRM effect on horizontal mixing

# Effective transport:
#     k_v = base_k_vertical * (1 + α_v * SAI_strength)
#     k_h = base_k_horizontal * (1 + α_h * SAI_strength)

# -------------------------
# Initial conditions
# -------------------------
C_A0 = 0.0
C_B0 = 0.0
C_strat0 = 0.0