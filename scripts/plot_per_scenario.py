import argparse
import csv
import os
from collections import defaultdict

import matplotlib.pyplot as plt

DEFAULT_RUN_DIR = (
    r"C:\Users\yfk13\OneDrive\Documents\New project\NadyProject\NadyProject"
    r"\benchmarks\run-2026-03-19T15-55-56Z"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate per-scenario charts")
    parser.add_argument("--run-dir", default=DEFAULT_RUN_DIR)
    args = parser.parse_args()

    run_dir = args.run_dir
    raw_csv = os.path.join(run_dir, "raw_requests.csv")
    charts_dir = os.path.join(run_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    records = defaultdict(list)

    with open(raw_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scenario = row.get("scenario") or "unknown"
            try:
                latency = float(row.get("latency_ms") or 0)
            except ValueError:
                continue
            ts = row.get("timestamp") or ""
            records[scenario].append((ts, latency))

    for scenario in sorted(records.keys()):
        series = records[scenario]
        try:
            series.sort(key=lambda x: x[0])
        except Exception:
            pass

        latencies = [x[1] for x in series]
        if not latencies:
            continue

        plt.figure(figsize=(10, 5))
        plt.plot(range(len(latencies)), latencies, linewidth=1)
        plt.title(f"Latency Time Series: {scenario}")
        plt.xlabel("Sample")
        plt.ylabel("Latency (ms)")
        plt.tight_layout()
        ts_path = os.path.join(charts_dir, f"latency_timeseries_{scenario}.png")
        plt.savefig(ts_path)
        plt.close()

        plt.figure(figsize=(10, 5))
        plt.hist(latencies, bins=30, alpha=0.8)
        plt.title(f"Latency Histogram: {scenario}")
        plt.xlabel("Latency (ms)")
        plt.ylabel("Count")
        plt.tight_layout()
        hist_path = os.path.join(charts_dir, f"latency_histogram_{scenario}.png")
        plt.savefig(hist_path)
        plt.close()

    print("Done. Generated per-scenario charts in:", charts_dir)


if __name__ == "__main__":
    main()
