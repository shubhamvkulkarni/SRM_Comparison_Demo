#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from utils.simulation import compute_sensitivity, current_defaults, run_case, sweep_sai_strength


ACCENT = "#2C6E63"
ACCENT_LIGHT = "#D8ECE4"
INK = "#17332D"
WARM = "#C46A2E"
GOLD = "#C6A546"
DIAGRAM_PATH = "plots/diagram.jpg"


def apply_page_style():
    st.set_page_config(
        page_title="SRM Air Quality Explorer",
        page_icon=":sun_behind_small_cloud:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(216, 236, 228, 0.95), transparent 34%),
                linear-gradient(180deg, #f7f5ef 0%, #f3efe5 100%);
            color: {INK};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}
        h1, h2, h3 {{
            color: {INK};
            letter-spacing: -0.02em;
        }}
        div[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #10342d 0%, #1f4d43 100%);
        }}
        div[data-testid="stSidebar"] * {{
            color: #f7f5ef;
        }}
        .hero-card {{
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(23, 51, 45, 0.10);
            border-radius: 22px;
            padding: 1.35rem 1.5rem;
            box-shadow: 0 20px 60px rgba(25, 46, 40, 0.08);
            margin-bottom: 1rem;
        }}
        .metric-card {{
            background: linear-gradient(135deg, rgba(216, 236, 228, 0.95), rgba(255, 255, 255, 0.92));
            border: 1px solid rgba(44, 110, 99, 0.12);
            border-radius: 18px;
            padding: 1rem 1.1rem;
        }}
        .metric-label {{
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: rgba(23, 51, 45, 0.70);
        }}
        .metric-value {{
            font-size: 1.7rem;
            font-weight: 700;
            color: {INK};
            margin-top: 0.15rem;
        }}
        .metric-detail {{
            font-size: 0.90rem;
            color: rgba(23, 51, 45, 0.80);
            margin-top: 0.25rem;
        }}
        .hero-text {{
            font-size: 1.02rem;
            line-height: 1.65;
            color: rgba(23, 51, 45, 0.90);
        }}
        .hero-image-wrap {{
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(23, 51, 45, 0.08);
            border-radius: 18px;
            padding: 0.65rem;
            box-shadow: 0 12px 35px rgba(25, 46, 40, 0.08);
        }}
        .hero-caption {{
            font-size: 0.95rem;
            color: rgba(23, 51, 45, 0.78);
            margin-top: 0.55rem;
            text-align: center;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def parse_float(value, label):
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid number.") from exc


def styled_metric(label, value, detail):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-detail">{detail}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_timeseries_figure(case, sai_strength):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(case["time_days"], case["C_A_ug_m3"], label="Region A", color=ACCENT, linewidth=2.6)
    ax.plot(case["time_days"], case["C_B_ug_m3"], label="Region B", color=WARM, linewidth=2.6)
    ax.plot(case["time_days"], case["C_strat_ug_m3"], label="Stratosphere", color=GOLD, linewidth=2.2)
    ax.set_xlabel(r"Time [$\mathrm{days}$]")
    ax.set_ylabel(r"Concentration [$\mu\mathrm{g\,m^{-3}}$]")
    ax.set_title(rf"Concentration evolution at $\mathrm{{SAI\ strength}} = {sai_strength:.2f}$")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def create_comparison_figure(baseline_case, active_case):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(
        baseline_case["time_days"],
        baseline_case["C_A_ug_m3"],
        label="Region A, no SRM",
        color=ACCENT,
        linewidth=2.4,
    )
    ax.plot(
        active_case["time_days"],
        active_case["C_A_ug_m3"],
        label="Region A, current SRM",
        color=WARM,
        linewidth=2.4,
    )
    ax.set_xlabel(r"Time [$\mathrm{days}$]")
    ax.set_ylabel(r"Region A concentration [$\mu\mathrm{g\,m^{-3}}$]")
    ax.set_title("Baseline versus current SRM case")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def create_sai_response_figure(sai_values, percent_change_a, percent_change_b):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(sai_values, percent_change_a, label="Region A", color=ACCENT, linewidth=2.5)
    ax.plot(sai_values, percent_change_b, label="Region B", color=WARM, linewidth=2.5)
    ax.axhline(0.0, color=INK, linestyle="--", linewidth=1.0, alpha=0.6)
    ax.set_xlabel(r"$\mathrm{SAI\ strength}$ [1]")
    ax.set_ylabel(r"Final concentration change [$\%$]")
    ax.set_title("Surface air-quality response across SAI strengths")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def create_sensitivity_figure(baseline_sensitivity, active_sensitivity):
    labels = ["Region A", "Region B", "Stratosphere"]
    baseline_values = [
        baseline_sensitivity["sensitivity_A"],
        baseline_sensitivity["sensitivity_B"],
        baseline_sensitivity["sensitivity_strat"],
    ]
    active_values = [
        active_sensitivity["sensitivity_A"],
        active_sensitivity["sensitivity_B"],
        active_sensitivity["sensitivity_strat"],
    ]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(x - width / 2, baseline_values, width=width, label="No SRM", color=ACCENT)
    ax.bar(x + width / 2, active_values, width=width, label="Current SRM", color=WARM)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(r"$dC/dE$ [$\mathrm{s}$]")
    ax.set_title("Air-quality controllability")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    return fig


def main():
    apply_page_style()
    defaults = current_defaults()

    left_col, right_col = st.columns([1.45, 1.0], gap="large")
    with left_col:
        st.markdown(
            """
            <div class="hero-card">
                <h1>SRM Air Quality Explorer</h1>
                <div class="hero-text">
                    This interactive model presents a simple first-order approximation of pollutant
                    concentrations in two surface regions and the stratosphere. Solar radiation
                    modification is represented as a perturbation to atmospheric transport efficiency,
                    so when you adjust the SRM controls you are testing how altered vertical exchange
                    and cross-boundary mixing reshape regional air quality. The diagnostics below compare
                    the no-SRM baseline with the active scenario, show how final concentrations respond
                    across a sweep of SAI strength, and estimate how air-quality controllability changes
                    in response to emission perturbations. For further explanation of the physical model
                    and variables, see the
                    <a href="https://github.com/shubhamvkulkarni/SRM_Comparison_Demo/blob/main/physical_model.md">physical model notes</a>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right_col:
        st.markdown('<div class="hero-image-wrap">', unsafe_allow_html=True)
        st.image(DIAGRAM_PATH, use_container_width=True)
        st.markdown(
            '<div class="hero-caption">Model geometry and transport processes are visualised above.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("Scenario Controls")
        sai_strength = st.slider(
            "SAI strength",
            min_value=0.0,
            max_value=1.0,
            value=float(defaults["SAI_strength"]),
            step=0.01,
        )
        alpha_vertical = st.slider(
            "α_vertical",
            min_value=-1.5,
            max_value=1.5,
            value=float(defaults["alpha_vertical"]),
            step=0.01,
        )
        alpha_horizontal = st.slider(
            "α_horizontal",
            min_value=-1.5,
            max_value=1.5,
            value=float(defaults["alpha_horizontal"]),
            step=0.01,
        )

        st.header("Editable Defaults")
        e_a_input = st.text_input("E_a", value=f'{defaults["E_A"]:.6e}')
        e_b_input = st.text_input("E_b", value=f'{defaults["E_B"]:.6e}')

        st.caption(
            "Emissions use internal SI units: kg m^-3 s^-1. "
            "Keep scientific notation if you want the current scale."
        )

    try:
        e_a = parse_float(e_a_input, "E_a")
        e_b = parse_float(e_b_input, "E_b")
    except ValueError as error:
        st.error(str(error))
        st.stop()

    active_case = run_case(
        sai_strength=sai_strength,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a,
        e_b=e_b,
    )
    baseline_case = run_case(
        sai_strength=0.0,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a,
        e_b=e_b,
    )

    delta_e = 0.1 * e_a if e_a != 0.0 else 1.0e-16
    baseline_sensitivity = compute_sensitivity(
        e_a=e_a,
        delta_e=delta_e,
        sai_strength=0.0,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_b=e_b,
    )
    active_sensitivity = compute_sensitivity(
        e_a=e_a,
        delta_e=delta_e,
        sai_strength=sai_strength,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_b=e_b,
    )

    sai_values = np.linspace(0.0, 1.0, 21)
    percent_change_a, percent_change_b = sweep_sai_strength(
        sai_values=sai_values,
        alpha_vertical=alpha_vertical,
        alpha_horizontal=alpha_horizontal,
        e_a=e_a,
        e_b=e_b,
    )

    metric_columns = st.columns(4)
    with metric_columns[0]:
        styled_metric(
            "Final Region A",
            f'{active_case["C_A_ug_m3"][-1]:.2f} ug m^-3',
            "Current end-state concentration",
        )
    with metric_columns[1]:
        styled_metric(
            "Final Region B",
            f'{active_case["C_B_ug_m3"][-1]:.2f} ug m^-3',
            "Lower-emission region response",
        )
    with metric_columns[2]:
        styled_metric(
            "Vertical Exchange",
            f'{active_case["k_vertical"]:.3e} s^-1',
            "SRM-modified strat-trop coupling",
        )
    with metric_columns[3]:
        change_pct = 100.0 * (
            active_sensitivity["sensitivity_A"] - baseline_sensitivity["sensitivity_A"]
        ) / baseline_sensitivity["sensitivity_A"]
        styled_metric(
            "Sensitivity Shift",
            f"{change_pct:.2f}%",
            "Region A controllability versus no SRM",
        )

    st.subheader("Model Plots")

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(create_timeseries_figure(active_case, sai_strength), clear_figure=True)
    with col2:
        st.pyplot(create_comparison_figure(baseline_case, active_case), clear_figure=True)

    col3, col4 = st.columns(2)
    with col3:
        st.pyplot(
            create_sai_response_figure(sai_values, percent_change_a, percent_change_b),
            clear_figure=True,
        )
    with col4:
        st.pyplot(
            create_sensitivity_figure(baseline_sensitivity, active_sensitivity),
            clear_figure=True,
        )

    with st.expander("Scenario details"):
        st.write(
            {
                "SAI_strength": sai_strength,
                "alpha_vertical": alpha_vertical,
                "alpha_horizontal": alpha_horizontal,
                "E_a": e_a,
                "E_b": e_b,
                "k_vertical": active_case["k_vertical"],
                "k_horizontal": active_case["k_horizontal"],
            }
        )


if __name__ == "__main__":
    main()
