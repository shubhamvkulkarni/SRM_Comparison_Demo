#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# experiments/run_base.py

"""
Run the model WITHOUT SRM (baseline case)

This script represents the "control" experiment:
    SAI_strength = 0

Purpose:
- Establish baseline air quality response to emissions
- This is what SRM cases will be compared against

We solve:
    dC/dt = E - λC + Transport

but with:
    k_h = base_k_horizontal
    k_v = base_k_vertical

(i.e. no SRM modification)

Outputs:
- Time evolution of concentrations in:
    Region A (C_A)
    Region B (C_B)
    Stratosphere (C_strat)

Internal model units:
    - time: s
    - concentration: kg m^-3

For plotting, concentrations are converted to ug m^-3 and time to days
for readability.
"""

import matplotlib.pyplot as plt

from utils import config
from model.solver import run_model


def main():
    # -------------------------
    # Ensure NO SRM
    # -------------------------
    config.SAI_strength = 0.0

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

    plt.plot(time_days, C_A_plot, label="Region A (high emissions)")
    plt.plot(time_days, C_B_plot, label="Region B (low emissions)")
    plt.plot(time_days, C_strat_plot, label="Stratosphere")

    plt.xlabel("Time [days]")
    plt.ylabel("Concentration [ug m^-3]")
    plt.title("Baseline (No SRM)")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()
