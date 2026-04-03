#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# model/chemistry.py

"""
Handles emissions and removal (simple chemistry module)

This module represents the "source–sink" part of the system.

We model concentration evolution as:

    dC/dt = E - λC

where:
    C = concentration [kg m^-3]
    E = emissions/source term [kg m^-3 s^-1]
    λ = removal rate [s^-1]

This is a simplified representation of:
    - emissions from surface sources
    - removal via deposition, chemistry, etc.

Note:
- Emissions (E_A, E_B) are prescribed inputs (not computed)
- This allows us to study how concentrations respond to emissions
  → key for "air quality controllability"
"""

from utils import config


def emissions():
    """
    Return emissions for regions A and B

    E_A: source term in region A [kg m^-3 s^-1]
    E_B: source term in region B [kg m^-3 s^-1]

    These are control variables in the system.
    """
    return config.E_A, config.E_B


def removal(C_A, C_B):
    """
    Linear removal (first-order decay):

        R = -λC

    where:
        λ = removal rate [s^-1]

    Returns:
        R_A, R_B with units [kg m^-3 s^-1]

    Applied independently to each region.
    """
    R_A = -config.lambda_removal * C_A
    R_B = -config.lambda_removal * C_B

    return R_A, R_B
