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
    plt.figure()

    plt.plot(C_A, label="Region A (high emissions)")
    plt.plot(C_B, label="Region B (low emissions)")
    plt.plot(C_strat, label="Stratosphere")

    plt.xlabel("Time step")
    plt.ylabel("Concentration")
    plt.title("Baseline (No SRM)")
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()