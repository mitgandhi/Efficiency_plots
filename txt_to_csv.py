#!/usr/bin/env python3
"""Convert the raw pump efficiency text file to CSV format.

Reads `V32HL56-efficiency test.txt` and writes a CSV file with Unix
line endings named `V32HL56-efficiency.csv`.
"""

import csv

INPUT_FILE = "V32HL56-efficiency test.txt"
OUTPUT_FILE = "V32HL56-efficiency.csv"


def convert(in_path: str = INPUT_FILE, out_path: str = OUTPUT_FILE) -> None:
    """Convert the input text file to CSV with Unix newlines."""
    with open(in_path, newline="") as src, open(out_path, "w", newline="") as dst:
        reader = csv.reader(src)
        writer = csv.writer(dst)
        for row in reader:
            writer.writerow(row)


if __name__ == "__main__":
    convert()
    print(f"Wrote {OUTPUT_FILE}")
