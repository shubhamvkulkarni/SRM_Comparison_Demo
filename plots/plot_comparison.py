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
    plt.figure()

    plt.plot(C_base, label="No SRM", linewidth=2)
    plt.plot(C_srm, label="With SRM", linewidth=2)

    plt.xlabel("Time step")
    plt.ylabel("Concentration (Region A)")
    plt.title("Impact of SRM on Air Quality")

    plt.legend()
    plt.grid()

    # Save figure
    plt.savefig("plots/srm_vs_baseline.png", dpi=300)

    plt.show()


if __name__ == "__main__":
    main()