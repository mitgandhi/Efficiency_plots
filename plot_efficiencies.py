#!/usr/bin/env python3
"""Plot corrected pump efficiencies from CSV data (MPa version with clean legends)."""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

DATA_FILE = "V32HL56-efficiency.csv"
OUTPUT_DIR = "corrected_plots"
Output_sepa= "Efficiency_plots"

def load_and_prepare_data(file_path: str = DATA_FILE):
    df = pd.read_csv(file_path)

    # Round displacement to nearest cc and Δp to the nearest 0.1 MPa
    df["RoundedDisplacement"] = df["Displacement"].round().astype(int)
    df["RoundedDeltap"] = df["Deltap"].round(1)  # e.g., 8.0 MPa, 8.5 MPa

    return df


def plot_efficiencies(df: pd.DataFrame, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    efficiency_labels = {
        "Etat": "Overall Efficiency (Etat) [%]",
        "Etav": "Volumetric Efficiency (Etav) [%]",
        "Etam": "Hydromechanical Efficiency (Etam) [%]"
    }

    for disp, disp_group in df.groupby("RoundedDisplacement"):
        for eff_key, eff_label in efficiency_labels.items():
            plt.figure(figsize=(8, 6))
            ax = plt.gca()

            # Limit number of curves (e.g., unique pressure values)
            unique_dps = sorted(disp_group["RoundedDeltap"].unique())
            step = max(len(unique_dps) // 8, 1)  # show ~8 curves max
            filtered_dps = unique_dps[::step]

            for dp in filtered_dps:
                sub_group = disp_group[disp_group["RoundedDeltap"] == dp].sort_values("Speed")
                ax.plot(sub_group["Speed"], sub_group[eff_key], label=f"Δp = {dp:.1f} MPa")

            ax.set_xlabel("Speed [RPM]")
            ax.set_ylabel(eff_label)
            ax.set_title(f"{eff_label} vs Speed (Displacement = {disp} cc/rev)")
            ax.grid(True)

            # Move legend below the plot
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True)

            plt.tight_layout()
            filename = f"{eff_key.lower()}_vs_speed_disp_{disp}.png"
            plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight')
            plt.close()

def plot_efficiencies_sep(df: pd.DataFrame, output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    target_pressures = [11.0, 32.0, 38.0]  # in MPa
    tolerance = 0.2  # to allow for float imprecision

    efficiency_labels = {
        "Etat": "Overall Efficiency (Etat) [%]",
        "Etav": "Volumetric Efficiency (Etav) [%]",
        "Etam": "Hydromechanical Efficiency (Etam) [%]"
    }

    for target_dp in target_pressures:
        # Filter data near the target pressure
        dp_group = df[(df["Deltap"] - target_dp).abs() <= tolerance]

        if dp_group.empty:
            print(f"No data found for Δp ≈ {target_dp} MPa")
            continue

        for eff_key, eff_label in efficiency_labels.items():
            plt.figure(figsize=(8, 6))
            ax = plt.gca()

            # Group by displacement
            for disp, sub_group in dp_group.groupby("RoundedDisplacement"):
                sub_group_sorted = sub_group.sort_values("Speed")
                ax.plot(sub_group_sorted["Speed"], sub_group_sorted[eff_key],
                        label=f"{disp} cc/rev")

            ax.set_xlabel("Speed [RPM]")
            ax.set_ylabel(eff_label)
            ax.set_title(f"{eff_label} vs Speed\n(Δp ≈ {target_dp} MPa)")
            ax.grid(True)

            # Place legend below plot
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=True)

            plt.tight_layout()
            filename = f"{eff_key.lower()}_vs_speed_dp_{int(target_dp)}mpa.png"
            plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight')
            plt.close()



def plot_efficiency_contours(df: pd.DataFrame, output_dir="contour_plots"):
    os.makedirs(output_dir, exist_ok=True)

    efficiency_labels = {
        "Etat": "Overall Efficiency (Etat) [%]",
        "Etav": "Volumetric Efficiency (Etav) [%]",
        "Etam": "Hydromechanical Efficiency (Etam) [%]"
    }

    # Round values for consistency
    df["RoundedDisplacement"] = df["Displacement"].round().astype(int)
    df["RoundedDeltap"] = df["Deltap"].round(1)

    for disp, group in df.groupby("RoundedDisplacement"):
        for eff_key, eff_label in efficiency_labels.items():
            pivot = group.pivot_table(
                index="Speed",               # Y-axis
                columns="RoundedDeltap",    # X-axis
                values=eff_key,
                aggfunc='mean'
            )

            if pivot.shape[0] < 2 or pivot.shape[1] < 2:
                continue  # Not enough data to contour

            X, Y = np.meshgrid(pivot.columns, pivot.index)
            Z = pivot.values

            plt.figure(figsize=(8, 6))
            contour = plt.contourf(X, Y, Z, levels=20, cmap="viridis")
            cbar = plt.colorbar(contour)
            cbar.set_label(eff_label)

            plt.xlabel("Δp [MPa]")
            plt.ylabel("Speed [RPM]")
            plt.title(f"{eff_label} Contour\n(Displacement = {disp} cc/rev)")
            plt.grid(True)

            filename = f"{eff_key.lower()}_contour_disp_{disp}.png"
            plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight')
            plt.close()

def plot_total_efficiency_field(df: pd.DataFrame, output_dir="efficiency_fields"):
    os.makedirs(output_dir, exist_ok=True)

    df["RoundedDisplacement"] = df["Displacement"].round().astype(int)
    df["RoundedDeltap"] = df["Deltap"].round(1)

    for disp, group in df.groupby("RoundedDisplacement"):
        pivot = group.pivot_table(
            index="Speed",               # Y-axis
            columns="RoundedDeltap",    # X-axis
            values="Etat",              # Efficiency
            aggfunc='mean'
        )

        if pivot.shape[0] < 2 or pivot.shape[1] < 2:
            continue

        X, Y = np.meshgrid(pivot.columns, pivot.index)
        Z = pivot.values

        plt.figure(figsize=(8, 6))
        # Automatically determine contour levels based on efficiency range
        min_eff = np.floor(Z.min())
        max_eff = np.ceil(Z.max())
        levels = np.arange(min_eff, max_eff + 1, 2)
        contour = plt.contourf(X, Y, Z, levels=levels, cmap="inferno", extend='both')
        cbar = plt.colorbar(contour)
        cbar.set_label("Total Efficiency [%]")

        # Add contour labels
        line_contours = plt.contour(X, Y, Z, levels=levels, colors="black", linewidths=0.5)
        plt.clabel(line_contours, inline=True, fontsize=8, fmt="%.0f")

        # Labels and style
        plt.xlabel("Pressure difference Δp [MPa]")
        plt.ylabel("Speed [RPM]")
        plt.title(f"Total Efficiency Map\nDisplacement = {disp} cc/rev")
        plt.grid(True)

        # Save
        filename = f"efficiency_map_disp_{disp}.png"
        plt.savefig(os.path.join(output_dir, filename), bbox_inches='tight')
        plt.close()


def main():
    df = load_and_prepare_data()
    plot_efficiencies(df)

    plot_efficiencies_sep(df,Output_sepa)
    plot_efficiency_contours(df)
    plot_total_efficiency_field(df)


if __name__ == "__main__":
    main()
