#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# experiments/run_srm.py

"""
Run the model WITH SRM (SAI perturbation)

This script explores how SRM modifies air quality by changing transport.

Key idea:
SRM (via stratospheric aerosol injection) alters atmospheric circulation,
which we represent as a modification of transport coefficients:

    k = k_base * (1 + α * SAI_strength)

where:
    k = transport rate (vertical or horizontal)
    α = sensitivity parameter
    SAI_strength = strength of SRM forcing

Thus the governing equation becomes:

    dC/dt = E - λC + Transport(SRM-modified)

We compare this against the baseline (run_base.py).
"""

import matplotlib.pyplot as plt

from utils import config
from model.solver import run_model


def main():
    # -------------------------
    # Set SRM strength
    # -------------------------
    config.SAI_strength = 0.5   # try values: 0.2, 0.5, 1.0

    # -------------------------
    # Run model
    # -------------------------
    C_A, C_B, C_strat = run_model()

    # -------------------------
    # Plot results
    # -------------------------
    plt.figure()

    plt.plot(C_A, label="Region A (SRM)")
    plt.plot(C_B, label="Region B (SRM)")
    plt.plot(C_strat, label="Stratosphere (SRM)")

    plt.xlabel("Time step")
    plt.ylabel("Concentration")
    plt.title(f"SRM case (SAI_strength = {config.SAI_strength})")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()