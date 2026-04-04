#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shared simulation helpers for scripts and interactive apps.
"""

from contextlib import contextmanager

import numpy as np

from model.dynamics import compute_transport_rates
from model.solver import run_model
from utils import config


PARAMETER_NAMES = (
    "SAI_strength",
    "alpha_vertical",
    "alpha_horizontal",
    "E_A",
    "E_B",
)


def current_defaults():
    """
    Return the current configurable model defaults.
    """

    return {name: getattr(config, name) for name in PARAMETER_NAMES}


@contextmanager
def temporary_config(**overrides):
    """
    Temporarily override selected config values.
    """

    original_values = {name: getattr(config, name) for name in overrides}

    try:
        for name, value in overrides.items():
            setattr(config, name, value)
        yield
    finally:
        for name, value in original_values.items():
            setattr(config, name, value)


def run_case(
    *,
    sai_strength=None,
    alpha_vertical=None,
    alpha_horizontal=None,
    e_a=None,
    e_b=None,
):
    """
    Run the model for a configurable parameter set.
    """

    overrides = {}

    if sai_strength is not None:
        overrides["SAI_strength"] = sai_strength
    if alpha_vertical is not None:
        overrides["alpha_vertical"] = alpha_vertical
    if alpha_horizontal is not None:
        overrides["alpha_horizontal"] = alpha_horizontal
    if e_a is not None:
        overrides["E_A"] = e_a
    if e_b is not None:
        overrides["E_B"] = e_b

    with temporary_config(**overrides):
        c_a, c_b, c_strat = run_model()
        k_vertical, k_horizontal = compute_transport_rates()

    return {
        "C_A": c_a,
        "C_B": c_b,
        "C_strat": c_strat,
        "k_vertical": k_vertical,
        "k_horizontal": k_horizontal,
        "time_days": np.arange(len(c_a)) * config.dt / config.SECONDS_PER_DAY,
        "C_A_ug_m3": c_a * config.KG_PER_M3_TO_UG_PER_M3,
        "C_B_ug_m3": c_b * config.KG_PER_M3_TO_UG_PER_M3,
        "C_strat_ug_m3": c_strat * config.KG_PER_M3_TO_UG_PER_M3,
    }


def compute_sensitivity(
    *,
    e_a,
    delta_e,
    sai_strength,
    alpha_vertical,
    alpha_horizontal,
    e_b,
):
    """
    Compute final-time dC/dE for a given parameter configuration.
    """

    base_case = run_case(
        sai_strength=sai_strength,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a,
        e_b=e_b,
    )

    perturbed_case = run_case(
        sai_strength=sai_strength,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a + delta_e,
        e_b=e_b,
    )

    return {
        "sensitivity_A": (perturbed_case["C_A"][-1] - base_case["C_A"][-1]) / delta_e,
        "sensitivity_B": (perturbed_case["C_B"][-1] - base_case["C_B"][-1]) / delta_e,
        "sensitivity_strat": (
            perturbed_case["C_strat"][-1] - base_case["C_strat"][-1]
        ) / delta_e,
    }


def sweep_sai_strength(
    *,
    sai_values,
    alpha_vertical,
    alpha_horizontal,
    e_a,
    e_b,
):
    """
    Sweep SAI strength and return percent changes in final concentrations.
    """

    baseline_case = run_case(
        sai_strength=0.0,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a,
        e_b=e_b,
    )

    baseline_a = baseline_case["C_A"][-1]
    baseline_b = baseline_case["C_B"][-1]

    percent_change_a = []
    percent_change_b = []

    for sai_strength in sai_values:
        case = run_case(
            sai_strength=float(sai_strength),
            alpha_vertical=alpha_vertical,
            alpha_horizontal=alpha_horizontal,
            e_a=e_a,
            e_b=e_b,
        )
        percent_change_a.append(
            100.0 * (case["C_A"][-1] - baseline_a) / baseline_a
        )
        percent_change_b.append(
            100.0 * (case["C_B"][-1] - baseline_b) / baseline_b
        )

    return np.array(percent_change_a), np.array(percent_change_b)
