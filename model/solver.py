#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# model/solver.py

"""
Time integration of the SRM toy model

This module combines:
    - emissions (source)
    - removal (sink)
    - transport (dynamics)

We solve the system:

    dC/dt = E - λC + Transport

For Region A:
    dC_A/dt = E_A - λC_A
              + k_h (C_B - C_A)
              + k_v (C_strat - C_A)

For Region B:
    dC_B/dt = E_B - λC_B
              + k_h (C_A - C_B)
              + k_v (C_strat - C_B)

For Stratosphere:
    dC_strat/dt = -k_v[(C_strat - C_A) + (C_strat - C_B)]

where:
    t = time [s]
    C = concentration [kg m^-3]
    E = source term [kg m^-3 s^-1]
    λ = removal rate [s^-1]
    k_h = horizontal mixing (A ↔ B) [s^-1]
    k_v = vertical exchange (strat ↔ trop) [s^-1]

SRM affects k_h and k_v (handled in dynamics.py)

We use simple forward Euler time stepping:
    C(t+dt) = C(t) + dt * (dC/dt)
"""

import numpy as np

from utils import config
from model.chemistry import emissions, removal
from model.dynamics import transport_terms, compute_transport_rates


def run_model():
    """
    Run time integration and return concentration time series.

    Returns:
        Arrays of C_A, C_B, C_strat in [kg m^-3]
    """

    # initialise state
    C_A = config.C_A0
    C_B = config.C_B0
    C_strat = config.C_strat0

    # store time series
    C_A_series = []
    C_B_series = []
    C_strat_series = []

    for _ in range(config.n_steps):

        # --- chemistry ---
        E_A, E_B = emissions()
        R_A, R_B = removal(C_A, C_B)

        # --- transport ---
        T_A_vert, T_B_vert, T_A_horiz, T_B_horiz = transport_terms(
            C_A, C_B, C_strat
        )

        k_vertical, _ = compute_transport_rates()

        # --- tendencies (dC/dt) [kg m^-3 s^-1] ---
        dC_A = E_A + R_A + T_A_vert + T_A_horiz
        dC_B = E_B + R_B + T_B_vert + T_B_horiz

        # Stratosphere loses/gains via vertical exchange [kg m^-3 s^-1].
        dC_strat = -k_vertical * (
            (C_strat - C_A) + (C_strat - C_B)
        )

        # --- time stepping (Euler): C_new = C_old + dt * dC/dt ---
        C_A += config.dt * dC_A
        C_B += config.dt * dC_B
        C_strat += config.dt * dC_strat

        # store results
        C_A_series.append(C_A)
        C_B_series.append(C_B)
        C_strat_series.append(C_strat)

    return np.array(C_A_series), np.array(C_B_series), np.array(C_strat_series)
