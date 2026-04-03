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
    k = transport rate (vertical or horizontal) [s^-1]
    α = sensitivity parameter [1]
    SAI_strength = strength of SRM forcing [1]

Internal model units:
    - time: s
    - concentration: kg m^-3

For plotting, concentrations are converted to ug m^-3 and time to days
for readability.

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
    time_days = [config.dt * i / config.SECONDS_PER_DAY for i in range(len(C_A))]

    C_A_plot = C_A * config.KG_PER_M3_TO_UG_PER_M3
    C_B_plot = C_B * config.KG_PER_M3_TO_UG_PER_M3
    C_strat_plot = C_strat * config.KG_PER_M3_TO_UG_PER_M3

    plt.figure()

    plt.plot(time_days, C_A_plot, label="Region A (SRM)")
    plt.plot(time_days, C_B_plot, label="Region B (SRM)")
    plt.plot(time_days, C_strat_plot, label="Stratosphere (SRM)")

    plt.xlabel("Time [days]")
    plt.ylabel("Concentration [ug m^-3]")
    plt.title(f"SRM case (SAI_strength = {config.SAI_strength})")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()
