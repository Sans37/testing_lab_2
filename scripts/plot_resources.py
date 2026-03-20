import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


def parse_ts(value: str) -> datetime:
    # ISO format with Z
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_resources(path: Path):
    by_container = defaultdict(list)
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = parse_ts(row["timestamp"])
            name = row["name"]
            cpu = float(row["cpu_percent"]) if row["cpu_percent"] else 0.0
            mem = float(row["mem_mib"]) if row["mem_mib"] else 0.0
            net = float(row.get("net_mib") or 0.0)
            block = float(row.get("block_mib") or 0.0)
            by_container[name].append((ts, cpu, mem, net, block))
    # sort by time
    for name in by_container:
        by_container[name].sort(key=lambda x: x[0])
    return by_container


def plot_timeseries(by_container, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    # CPU
    plt.figure(figsize=(10, 5))
    for name, rows in by_container.items():
        xs = [r[0] for r in rows]
        ys = [r[1] for r in rows]
        plt.plot(xs, ys, label=name)
    plt.title("CPU Usage (%) by Container")
    plt.xlabel("Time")
    plt.ylabel("CPU %")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "resources_cpu_timeseries.png", dpi=140)
    plt.close()

    # Memory
    plt.figure(figsize=(10, 5))
    for name, rows in by_container.items():
        xs = [r[0] for r in rows]
        ys = [r[2] for r in rows]
        plt.plot(xs, ys, label=name)
    plt.title("Memory Usage (MiB) by Container")
    plt.xlabel("Time")
    plt.ylabel("MiB")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "resources_mem_timeseries.png", dpi=140)
    plt.close()

    # Network I/O (MiB)
    plt.figure(figsize=(10, 5))
    for name, rows in by_container.items():
        xs = [r[0] for r in rows]
        ys = [r[3] for r in rows]
        plt.plot(xs, ys, label=name)
    plt.title("Network I/O (MiB) by Container")
    plt.xlabel("Time")
    plt.ylabel("MiB")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "resources_net_timeseries.png", dpi=140)
    plt.close()

    # Block I/O (MiB)
    plt.figure(figsize=(10, 5))
    for name, rows in by_container.items():
        xs = [r[0] for r in rows]
        ys = [r[4] for r in rows]
        plt.plot(xs, ys, label=name)
    plt.title("Block I/O (MiB) by Container")
    plt.xlabel("Time")
    plt.ylabel("MiB")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / "resources_block_timeseries.png", dpi=140)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot resource usage from resources.csv")
    parser.add_argument("--resources", required=True, help="Path to resources.csv")
    parser.add_argument("--out-dir", required=False, help="Output directory for charts")
    args = parser.parse_args()

    resources_path = Path(args.resources)
    out_dir = Path(args.out_dir) if args.out_dir else resources_path.parent
    by_container = load_resources(resources_path)
    if not by_container:
        raise SystemExit("No resource samples found in resources.csv")
    plot_timeseries(by_container, out_dir)


if __name__ == "__main__":
    main()
