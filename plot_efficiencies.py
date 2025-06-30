#!/usr/bin/env python3
"""Plot pump efficiencies from data file.

Reads ``V32HL56-efficiency test.txt`` and generates line plots of
hydromechanical, volumetric and overall efficiencies versus speed.
The data are first sorted by speed, displacement and pressure.
For each displacement and pressure combination a set of lines is drawn.
"""

import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt

DATA_FILE = "V32HL56-efficiency test.txt"


def read_data(file_path: str = DATA_FILE):
    """Return list of rows from the CSV file sorted by speed, displacement and pressure."""
    rows = []
    with open(file_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert all values to float for easier processing
            for key, value in row.items():
                row[key] = float(value)
            rows.append(row)
    rows.sort(key=lambda r: (r["Speed"], r["Displacement"], r["Deltap"]))
    return rows


def group_data(rows):
    """Group rows by (displacement, pressure difference)."""
    grouped = defaultdict(list)
    for row in rows:
        key = (row["Displacement"], row["Deltap"])
        grouped[key].append(row)
    return grouped


def plot_grouped(groups, output_dir="plots"):
    """Create efficiency plots for every displacement and pressure group."""
    os.makedirs(output_dir, exist_ok=True)
    by_disp = defaultdict(list)
    for (disp, dp), data in groups.items():
        by_disp[disp].append((dp, data))

    labels = [
        "Hydromechanical $\\eta_m$",
        "Volumetric $\\eta_v$",
        "Overall $\\eta_t$",
    ]
    keys = ["Etam", "Etav", "Etat"]

    for disp, dp_groups in by_disp.items():
        fig, axes = plt.subplots(3, 1, sharex=True, figsize=(8, 10))

        for dp, data in sorted(dp_groups, key=lambda t: t[0]):
            speeds = [row["Speed"] for row in data]
            for ax, key, label in zip(axes, keys, labels):
                ax.plot(speeds, [row[key] for row in data], label=f"Δp={dp:.2f}")
                ax.set_ylabel(label)
                ax.grid(True)

        for ax in axes:
            ax.legend()
        axes[-1].set_xlabel("Speed")
        fig.suptitle(f"Displacement {disp:.2f} cc/rev")
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        out_path = os.path.join(output_dir, f"efficiency_{disp:.2f}.png")
        plt.savefig(out_path)
        plt.close(fig)


def main():
    rows = read_data()
    groups = group_data(rows)
    plot_grouped(groups)


if __name__ == "__main__":
    main()
