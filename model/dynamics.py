#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# model/dynamics.py

"""
Transport and SRM effects module

This module represents how pollutants are transported between:
    - Region A
    - Region B
    - Stratosphere

It includes:
    - Horizontal mixing (cross-boundary transport)
    - Vertical exchange (stratosphere ↔ troposphere)
    - Modification of transport under SRM

---

🔹 Physical representation

Transport terms are modelled as linear exchange:

Horizontal mixing:
    T_h = k_h (C_other - C)

Vertical exchange:
    T_v = k_v (C_strat - C)

where:
    k_h = horizontal mixing coefficient
    k_v = vertical exchange coefficient

---

🔹 SRM representation

Stratospheric aerosol injection (SAI) modifies circulation,
which we represent as a change in transport efficiency:

    k = k_base (1 + α * SAI_strength)

where:
    α = sensitivity parameter
    SAI_strength = strength of SRM forcing

Interpretation:
- α < 0 → reduced mixing (e.g. strat heating stabilisation)
- α > 0 → enhanced mixing

---

IMPORTANT:
We import config as a module (not individual variables),
so changes to SAI_strength propagate dynamically.
"""

from utils import config


def compute_transport_rates():
    """
    Compute SRM-modified transport coefficients

    k_v = base_k_vertical * (1 + α_v * SAI_strength)
    k_h = base_k_horizontal * (1 + α_h * SAI_strength)
    """

    k_vertical = config.base_k_vertical * (
        1 + config.alpha_vertical * config.SAI_strength
    )

    k_horizontal = config.base_k_horizontal * (
        1 + config.alpha_horizontal * config.SAI_strength
    )

    return k_vertical, k_horizontal


def transport_terms(C_A, C_B, C_strat):
    """
    Compute transport contributions for each region

    Returns:
        T_A_vert  = vertical transport into A
        T_B_vert  = vertical transport into B
        T_A_horiz = horizontal transport into A
        T_B_horiz = horizontal transport into B

    Formulas:

        T_A_vert = k_v (C_strat - C_A)
        T_B_vert = k_v (C_strat - C_B)

        T_A_horiz = k_h (C_B - C_A)
        T_B_horiz = k_h (C_A - C_B)
    """

    k_vertical, k_horizontal = compute_transport_rates()

    # Vertical exchange (stratosphere ↔ troposphere)
    T_A_vert = k_vertical * (C_strat - C_A)
    T_B_vert = k_vertical * (C_strat - C_B)

    # Horizontal mixing (Region A ↔ B)
    T_A_horiz = k_horizontal * (C_B - C_A)
    T_B_horiz = k_horizontal * (C_A - C_B)

    return T_A_vert, T_B_vert, T_A_horiz, T_B_horiz