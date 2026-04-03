#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# experiments/run_sensitivity.py

"""
Air quality controllability experiment

This script quantifies how sensitive surface pollution is to emissions.

Key metric:
    Sensitivity = dC / dE

With the SI unit convention used here:
    [dC/dE] = (kg m^-3) / (kg m^-3 s^-1) = s

We approximate this numerically using finite differences:

    dC/dE ≈ (C(E + ΔE) - C(E)) / ΔE

This is central to the project:
→ how controllable air quality is under different conditions

We compare:
    - baseline (no SRM)
    - SRM case

to see how SRM changes this sensitivity.

Interpretation:
- High sensitivity → emissions strongly affect air quality
- Low sensitivity → harder to control pollution via emissions
"""

import matplotlib.pyplot as plt

from utils import config
from model.solver import run_model
from model.dynamics import compute_transport_rates


def run_case(E_A, SAI_strength):
    """
    Run the model for a single emissions / SRM configuration.

    Parameters:
        E_A: Region A source term [kg m^-3 s^-1]
        SAI_strength: dimensionless
    """

    config.E_A = E_A
    config.SAI_strength = SAI_strength
    return run_model()


def compute_sensitivity(E_base, delta_E, SAI_strength):
    """
    Compute dC/dE using a finite difference on the final concentration.

    Parameters:
        E_base: baseline Region A source term [kg m^-3 s^-1]
        delta_E: source perturbation [kg m^-3 s^-1]
        SAI_strength: dimensionless

    Returns:
        Sensitivities in [s]
    """

    original_E_A = config.E_A
    original_SAI = config.SAI_strength

    try:
        C_A_base, C_B_base, C_strat_base = run_case(E_base, SAI_strength)
        C_A_pert, C_B_pert, C_strat_pert = run_case(E_base + delta_E, SAI_strength)
    finally:
        config.E_A = original_E_A
        config.SAI_strength = original_SAI

    sensitivity_A = (C_A_pert[-1] - C_A_base[-1]) / delta_E
    sensitivity_B = (C_B_pert[-1] - C_B_base[-1]) / delta_E
    sensitivity_strat = (C_strat_pert[-1] - C_strat_base[-1]) / delta_E

    return {
        "sensitivity_A": sensitivity_A,
        "sensitivity_B": sensitivity_B,
        "sensitivity_strat": sensitivity_strat,
        "final_A_base": C_A_base[-1],
        "final_A_pert": C_A_pert[-1],
        "final_B_base": C_B_base[-1],
        "final_B_pert": C_B_pert[-1],
        "final_strat_base": C_strat_base[-1],
        "final_strat_pert": C_strat_pert[-1],
    }


def main():
    E_base = config.E_A
    delta_E = 0.1 * config.E_A

    # -------------------------
    # No SRM
    # -------------------------
    config.SAI_strength = 0.0
    k_v_no_srm, k_h_no_srm = compute_transport_rates()
    sens_no_srm = compute_sensitivity(E_base, delta_E, SAI_strength=0.0)

    # -------------------------
    # With SRM
    # -------------------------
    config.SAI_strength = 0.5
    k_v_srm, k_h_srm = compute_transport_rates()
    sens_srm = compute_sensitivity(E_base, delta_E, SAI_strength=0.5)

    # -------------------------
    # Plot comparison
    # -------------------------
    labels = ["No SRM", "With SRM"]
    values_A = [sens_no_srm["sensitivity_A"], sens_srm["sensitivity_A"]]
    values_B = [sens_no_srm["sensitivity_B"], sens_srm["sensitivity_B"]]
    values_strat = [sens_no_srm["sensitivity_strat"], sens_srm["sensitivity_strat"]]

    percent_change_A = 100.0 * (
        sens_srm["sensitivity_A"] - sens_no_srm["sensitivity_A"]
    ) / sens_no_srm["sensitivity_A"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    bar_colors = ["steelblue", "darkorange"]
    bars = axes[0].bar(labels, values_A, color=bar_colors)
    axes[0].set_ylabel(r"Final-time sensitivity [s]")
    axes[0].set_title("Region A controllability")
    axes[0].grid(axis="y", alpha=0.3)

    for bar, value in zip(bars, values_A):
        axes[0].text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.03,
            f"{value:.3f}",
            ha="center",
            va="bottom",
        )

    metric_labels = ["Region A", "Region B", "Stratosphere"]
    no_srm_metrics = [values_A[0], values_B[0], values_strat[0]]
    srm_metrics = [values_A[1], values_B[1], values_strat[1]]
    x = range(len(metric_labels))
    width = 0.34

    axes[1].bar(
        [i - width / 2 for i in x],
        no_srm_metrics,
        width=width,
        label="No SRM",
        color="steelblue",
    )
    axes[1].bar(
        [i + width / 2 for i in x],
        srm_metrics,
        width=width,
        label="With SRM",
        color="darkorange",
    )
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(metric_labels)
    axes[1].set_ylabel(r"dC / dE [s]")
    axes[1].set_title("Sensitivity across model compartments")
    axes[1].legend()
    axes[1].grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Air quality controllability under SRM\n"
        f"Region A sensitivity change = {percent_change_A:.2f}%",
        fontsize=13,
    )
    fig.tight_layout()

    plt.show()

    print("No SRM transport rates [s^-1]:", {"k_vertical": k_v_no_srm, "k_horizontal": k_h_no_srm})
    print("With SRM transport rates [s^-1]:", {"k_vertical": k_v_srm, "k_horizontal": k_h_srm})
    print("Sensitivity diagnostics (No SRM):", sens_no_srm)
    print("Sensitivity diagnostics (With SRM):", sens_srm)


if __name__ == "__main__":
    main()
