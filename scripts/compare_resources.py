import argparse
import json
from pathlib import Path


def load_summary(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Compare resource summaries")
    parser.add_argument("--label-a", default="baseline")
    parser.add_argument("--label-b", default="variant")
    parser.add_argument("--a", required=True, help="path to resources_summary.json")
    parser.add_argument("--b", required=True, help="path to resources_summary.json")
    args = parser.parse_args()

    a = load_summary(Path(args.a))
    b = load_summary(Path(args.b))

    print("| Container | CPU avg (A) | CPU avg (B) | RAM avg MiB (A) | RAM avg MiB (B) |")
    print("|---|---:|---:|---:|---:|")

    containers = sorted(set(a.keys()) | set(b.keys()))
    for name in containers:
        a_row = a.get(name, {})
        b_row = b.get(name, {})
        print(
            f"| {name} | "
            f"{a_row.get('cpu_mean', '')} | {b_row.get('cpu_mean', '')} | "
            f"{a_row.get('mem_mean_mib', '')} | {b_row.get('mem_mean_mib', '')} |"
        )


if __name__ == "__main__":
    main()
