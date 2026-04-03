#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# plots/plot_comparison.py

"""
Generate a key figure for README:
Comparison of baseline vs SRM

This shows how SRM modifies concentration evolution.

We plot:
    C_A(t) with and without SRM

This directly demonstrates:
    SRM → transport change → air quality impact

Internal model units:
    - time: s
    - concentration: kg m^-3

For the figure, time is shown in days and concentration in ug m^-3
for readability.
"""

import matplotlib.pyplot as plt

from utils import config
from model.solver import run_model


def run_case(SAI_strength):
    config.SAI_strength = SAI_strength
    C_A, _, _ = run_model()
    return C_A


def main():
    # Run baseline
    C_base = run_case(SAI_strength=0.0)

    # Run SRM
    C_srm = run_case(SAI_strength=0.5)

    # Plot
    time_days = [config.dt * i / config.SECONDS_PER_DAY for i in range(len(C_base))]
    C_base_plot = C_base * config.KG_PER_M3_TO_UG_PER_M3
    C_srm_plot = C_srm * config.KG_PER_M3_TO_UG_PER_M3

    plt.figure()

    plt.plot(time_days, C_base_plot, label="No SRM", linewidth=2)
    plt.plot(time_days, C_srm_plot, label="With SRM", linewidth=2)

    plt.xlabel("Time [days]")
    plt.ylabel("Region A concentration [ug m^-3]")
    plt.title("Impact of SRM on Air Quality")

    plt.legend()
    plt.grid()

    # Save figure
    plt.savefig("plots/srm_vs_baseline.png", dpi=300)

    plt.show()


if __name__ == "__main__":
    main()
