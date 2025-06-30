#!/usr/bin/env python3
"""Plot pump efficiencies from CSV data.

The repository already contains a CSV file with the efficiency
measurements (``V32HL56-efficiency.csv``).  This script reads the CSV,
groups the data by *rounded* displacement and pressure difference and
generates three plots for each displacement:

``Etat`` vs speed,
``Etav`` vs speed and
``Etam`` vs speed.
"""

import csv
import os
from collections import defaultdict
import matplotlib.pyplot as plt

DATA_FILE = "V32HL56-efficiency.csv"


def read_data(file_path: str = DATA_FILE):
    """Return list of rows sorted by speed, displacement and pressure.

    All numeric fields are converted to ``float`` for easier processing.
    """
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
    """Group rows by rounded displacement and pressure difference."""
    grouped = defaultdict(list)
    for row in rows:
        disp = int(round(row["Displacement"]))
        key = (disp, row["Deltap"])
        grouped[key].append(row)
    return grouped


def plot_grouped(groups, output_dir="plots"):
    """Create efficiency plots for every displacement."""
    os.makedirs(output_dir, exist_ok=True)
    by_disp = defaultdict(list)
    for (disp, dp), data in groups.items():
        by_disp[disp].append((dp, data))

    labels = {
        "Etat": "Overall $\\eta_t$",
        "Etav": "Volumetric $\\eta_v$",
        "Etam": "Hydromechanical $\\eta_m$",
    }

    for disp, dp_groups in by_disp.items():
        for key, label in labels.items():
            plt.figure()
            for dp, data in sorted(dp_groups, key=lambda t: t[0]):
                speeds = [row["Speed"] for row in data]
                plt.plot(speeds, [row[key] for row in data], label=f"Δp={dp:.2f}")

            plt.xlabel("Speed")
            plt.ylabel(label)
            plt.title(f"{label} vs Speed (Displacement {disp} cc/rev)")
            plt.grid(True)
            plt.legend()
            out_name = f"{key.lower()}_vs_speed_disp_{disp}.png"
            plt.savefig(os.path.join(output_dir, out_name))
            plt.close()


def main():
    rows = read_data()
    groups = group_data(rows)
    plot_grouped(groups)


if __name__ == "__main__":
    main()
