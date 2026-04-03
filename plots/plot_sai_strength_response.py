#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# plots/plot_sai_strength_response.py

"""
Generate a README figure showing how air quality changes with SAI strength.

This script sweeps SAI_strength from 0 to 1 and computes the percent change
in final-time surface pollutant concentration relative to the no-SRM baseline.

Air quality metric used here:
    percent change in final concentration

        % change = 100 * (C_final(SAI) - C_final(no SRM)) / C_final(no SRM)

We report this for both surface regions:
    - Region A
    - Region B

Internal model units:
    - time: s
    - concentration: kg m^-3

The percent-change diagnostic is dimensionless.
"""

import numpy as np
import matplotlib.pyplot as plt

from utils import config
from model.solver import run_model


def run_case(sai_strength):
    """
    Run the model for a given SAI strength and return final concentrations.
    """
    original_sai = config.SAI_strength

    try:
        config.SAI_strength = sai_strength
        c_a, c_b, c_strat = run_model()
    finally:
        config.SAI_strength = original_sai

    return c_a[-1], c_b[-1], c_strat[-1]


def percent_change(new_value, baseline_value):
    """
    Compute percent change relative to baseline.
    """
    return 100.0 * (new_value - baseline_value) / baseline_value


def main():
    sai_values = np.linspace(0.0, 1.0, 21)

    baseline_a, baseline_b, _ = run_case(0.0)

    percent_change_a = []
    percent_change_b = []

    for sai_strength in sai_values:
        final_a, final_b, _ = run_case(float(sai_strength))
        percent_change_a.append(percent_change(final_a, baseline_a))
        percent_change_b.append(percent_change(final_b, baseline_b))

    plt.figure(figsize=(8.5, 5.0))

    plt.plot(
        sai_values,
        percent_change_a,
        label="Region A",
        linewidth=2.4,
        color="steelblue",
    )
    plt.plot(
        sai_values,
        percent_change_b,
        label="Region B",
        linewidth=2.4,
        color="darkorange",
    )
    plt.axhline(0.0, color="black", linewidth=1.0, linestyle="--", alpha=0.7)

    plt.xlabel("SAI strength [1]")
    plt.ylabel("Air quality change [%]")
    plt.title("Change in surface air quality versus SAI strength")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig("plots/sai_strength_vs_air_quality_change.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
