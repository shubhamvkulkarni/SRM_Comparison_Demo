#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# utils/config.py

"""
Global configuration for SRM air quality toy model

This file defines all model parameters and initial conditions.

Unit convention used throughout the model:
    - time: seconds (s)
    - concentration C: kilograms per cubic meter (kg m^-3)
    - emissions/source term E: kilograms per cubic meter per second
      (kg m^-3 s^-1)
    - removal and exchange coefficients (lambda, k_h, k_v): per second (s^-1)
    - sensitivity dC/dE: seconds (s)
    - alpha parameters: dimensionless
    - SAI_strength: dimensionless

IMPORTANT:
This module is imported as:
    from utils import config

so that parameters can be modified dynamically (e.g. SAI_strength, emissions).

---

🔹 Governing equation:

    dC/dt = E - λC + Transport

where:
    C = concentration [kg m^-3]
    E = emissions/source term [kg m^-3 s^-1]
    λ = removal rate [s^-1]

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
    α = sensitivity parameter [1]
    SAI_strength = strength of SRM forcing [1]

Negative α → reduced mixing (physically plausible for strat heating effects)
"""

SECONDS_PER_DAY = 86400.0
KG_PER_M3_TO_UG_PER_M3 = 1.0e9

# -------------------------
# Time settings
# -------------------------
dt = 1.0 * SECONDS_PER_DAY   # time step [s] = 1 day
n_steps = 200                # number of time steps [1]

# -------------------------
# Emissions (control variables)
# -------------------------
# Chosen so equilibrium near-surface concentrations are on the order of
# 5-20 ug m^-3 after conversion from SI units.
E_A = 3.0e-14       # Region A source [kg m^-3 s^-1]
E_B = 9.0e-15       # Region B source [kg m^-3 s^-1]

# -------------------------
# Removal (first-order decay)
# -------------------------
# About a 7 day e-folding lifetime for near-surface pollutant removal.
lambda_removal = 1.0 / (7.0 * SECONDS_PER_DAY)   # [s^-1]

# Removal term:
#     R = -λC

# -------------------------
# Transport parameters
# -------------------------
# Horizontal mixing is faster than stratosphere-troposphere exchange.
base_k_vertical = 1.0 / (90.0 * SECONDS_PER_DAY)    # strat ↔ trop exchange [s^-1]
base_k_horizontal = 1.0 / (14.0 * SECONDS_PER_DAY)  # A ↔ B mixing [s^-1]

# Transport terms:
#     T_v = k_v (C_strat - C)
#     T_h = k_h (C_other - C)

# -------------------------
# SRM parameters
# -------------------------
SAI_strength = 0.0        # SRM strength [1], 0 = no SRM

alpha_vertical = -0.5     # SRM effect on vertical transport [1]
alpha_horizontal = -0.3   # SRM effect on horizontal mixing [1]

# Effective transport:
#     k_v = base_k_vertical * (1 + α_v * SAI_strength)
#     k_h = base_k_horizontal * (1 + α_h * SAI_strength)

# -------------------------
# Initial conditions
# -------------------------
C_A0 = 0.0                # Initial Region A concentration [kg m^-3]
C_B0 = 0.0                # Initial Region B concentration [kg m^-3]
C_strat0 = 0.0            # Initial stratospheric concentration [kg m^-3]
