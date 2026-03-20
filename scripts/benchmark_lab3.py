import argparse
import asyncio
import csv
import json
import math
import os
import random
import re
import statistics
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx


@dataclass
class RequestSpec:
    method: str
    url: str
    name: str
    json_body: Optional[dict] = None
    headers: Optional[dict] = None


def utc_now_tag() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")


def percentile(values: List[float], p: float) -> Optional[float]:
    if not values:
        return None
    values_sorted = sorted(values)
    if len(values_sorted) == 1:
        return values_sorted[0]
    k = (len(values_sorted) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[f] * (c - k)
    d1 = values_sorted[c] * (k - f)
    return d0 + d1


def summarize_latencies(values: List[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "stdev": None,
            "p50": None,
            "p75": None,
            "p90": None,
            "p95": None,
            "p99": None,
        }

    values_sorted = sorted(values)
    return {
        "count": len(values_sorted),
        "min": values_sorted[0],
        "max": values_sorted[-1],
        "mean": statistics.mean(values_sorted),
        "stdev": statistics.pstdev(values_sorted) if len(values_sorted) > 1 else 0.0,
        "p50": percentile(values_sorted, 0.50),
        "p75": percentile(values_sorted, 0.75),
        "p90": percentile(values_sorted, 0.90),
        "p95": percentile(values_sorted, 0.95),
        "p99": percentile(values_sorted, 0.99),
    }


def parse_size_to_mib(value: str) -> Optional[float]:
    value = value.strip()
    if not value:
        return None

    match = re.match(r"([0-9.]+)\s*([A-Za-z]+)", value)
    if not match:
        return None

    num = float(match.group(1))
    unit = match.group(2).lower()
    if unit in ["b"]:
        return num / (1024 * 1024)
    if unit in ["kib", "kb"]:
        return num / 1024
    if unit in ["mib", "mb"]:
        return num
    if unit in ["gib", "gb"]:
        return num * 1024
    if unit in ["tib", "tb"]:
        return num * 1024 * 1024
    return None


def parse_percent(value: str) -> Optional[float]:
    value = value.strip().replace("%", "")
    try:
        return float(value)
    except ValueError:
        return None


def parse_docker_stats_line(line: str) -> Optional[dict]:
    # format: name,cpu%,memUsage,netIO,blockIO
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 5:
        return None

    name = parts[0]
    cpu = parse_percent(parts[1])

    mem_used = None
    if parts[2]:
        mem_used = parts[2].split("/")[0].strip()

    mem_mib = parse_size_to_mib(mem_used) if mem_used else None

    net_io = None
    if parts[3]:
        net_io = parts[3].split("/")[0].strip()
    net_mib = parse_size_to_mib(net_io) if net_io else None

    block_io = None
    if parts[4]:
        block_io = parts[4].split("/")[0].strip()
    block_mib = parse_size_to_mib(block_io) if block_io else None

    return {
        "name": name,
        "cpu_percent": cpu,
        "mem_mib": mem_mib,
        "net_mib": net_mib,
        "block_mib": block_mib,
    }


class ResourceSampler:
    def __init__(self, interval_s: float, docker_names: Optional[List[str]] = None):
        self.interval_s = interval_s
        self.docker_names = docker_names or []
        self.samples: List[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=5)

    def _run(self) -> None:
        while not self._stop.is_set():
            ts = datetime.utcnow().isoformat() + "Z"
            if self.docker_names:
                self._sample_docker(ts)
            time.sleep(self.interval_s)

    def _sample_docker(self, ts: str) -> None:
        cmd = [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}",
        ]
        cmd.extend(self.docker_names)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except Exception:
            return

        for line in result.stdout.splitlines():
            parsed = parse_docker_stats_line(line)
            if not parsed:
                continue
            parsed["timestamp"] = ts
            self.samples.append(parsed)


def build_request_mix(
    base_url: str,
    total_requests: int,
    auth_email: Optional[str],
    auth_password: Optional[str],
) -> List[RequestSpec]:
    weights = [
        ("read_products", 0.45),
        ("read_categories", 0.25),
        ("read_data", 0.10),
        ("write_data", 0.10),
        ("auth_login", 0.10),
    ]

    choices = []
    for name, weight in weights:
        choices.extend([name] * int(weight * 100))

    requests: List[RequestSpec] = []
    for i in range(total_requests):
        choice = random.choice(choices)
        if choice == "read_products":
            requests.append(
                RequestSpec(
                    method="GET",
                    url=f"{base_url}/api/v2/products?pagesNum=1&elemCount=10",
                    name="GET /api/v2/products",
                )
            )
        elif choice == "read_categories":
            requests.append(
                RequestSpec(
                    method="GET",
                    url=f"{base_url}/api/v2/categories?pagesNum=1&elemCount=10",
                    name="GET /api/v2/categories",
                )
            )
        elif choice == "read_data":
            requests.append(
                RequestSpec(
                    method="GET",
                    url=f"{base_url}/api/v2/data",
                    name="GET /api/v2/data",
                )
            )
        elif choice == "write_data":
            requests.append(
                RequestSpec(
                    method="POST",
                    url=f"{base_url}/api/v2/data",
                    name="POST /api/v2/data",
                    json_body={"payload": "benchmark", "seq": i},
                    headers={"Content-Type": "application/json"},
                )
            )
        elif choice == "auth_login" and auth_email and auth_password:
            requests.append(
                RequestSpec(
                    method="POST",
                    url=f"{base_url}/api/v2/auth/login",
                    name="POST /api/v2/auth/login",
                    json_body={"email": auth_email, "password": auth_password},
                    headers={"Content-Type": "application/json"},
                )
            )
        else:
            requests.append(
                RequestSpec(
                    method="GET",
                    url=f"{base_url}/api/v2/health",
                    name="GET /health",
                )
            )

    return requests


async def run_requests(
    client: httpx.AsyncClient,
    requests: List[RequestSpec],
    concurrency: int,
) -> List[dict]:
    semaphore = asyncio.Semaphore(concurrency)
    results: List[dict] = []

    async def worker(req: RequestSpec) -> None:
        async with semaphore:
            start = time.perf_counter()
            error = None
            status_code = None
            try:
                resp = await client.request(
                    req.method,
                    req.url,
                    json=req.json_body,
                    headers=req.headers,
                )
                status_code = resp.status_code
            except Exception as exc:
                error = str(exc)
            latency_ms = (time.perf_counter() - start) * 1000.0
            results.append(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "method": req.method,
                    "endpoint": req.name,
                    "status_code": status_code,
                    "latency_ms": latency_ms,
                    "error": error,
                }
            )

    tasks = [asyncio.create_task(worker(req)) for req in requests]
    await asyncio.gather(*tasks)
    return results


def wait_for_health(base_url: str, timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            resp = httpx.get(f"{base_url}/health", timeout=5)
            if resp.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)

    raise RuntimeError("Health check timed out")


def docker_compose(compose_file: str, args: List[str]) -> None:
    cmd = ["docker", "compose", "-f", compose_file] + args
    subprocess.run(cmd, check=True)


def ensure_auth_user(base_url: str, email: str, password: str) -> None:
    payload = {
        "name": "Benchmark User",
        "email": email,
        "password": password,
        "phone": "+79999999999",
        "address": "Benchmark Street",
    }
    try:
        httpx.post(f"{base_url}/api/v2/auth/register", json=payload, timeout=10)
    except Exception:
        # Registration may fail if user already exists; ignore to keep benchmark running
        pass


def compute_summary(records: List[dict]) -> Dict[str, dict]:
    summary: Dict[str, dict] = {}
    for record in records:
        scenario = record["scenario"]
        endpoint = record["endpoint"]
        error = record["error"]
        latency = record["latency_ms"]

        summary.setdefault(scenario, {}).setdefault(endpoint, {"latencies": [], "errors": 0})
        if error or (record["status_code"] and record["status_code"] >= 500):
            summary[scenario][endpoint]["errors"] += 1
        summary[scenario][endpoint]["latencies"].append(latency)

    result: Dict[str, dict] = {}
    for scenario, endpoints in summary.items():
        result[scenario] = {}
        for endpoint, data in endpoints.items():
            latencies = data["latencies"]
            stats = summarize_latencies(latencies)
            stats["errors"] = data["errors"]
            stats["error_rate"] = (data["errors"] / len(latencies)) if latencies else None
            result[scenario][endpoint] = stats

    return result


def summarize_resources(samples: List[dict]) -> Dict[str, dict]:
    grouped: Dict[str, List[dict]] = {}
    for sample in samples:
        grouped.setdefault(sample["name"], []).append(sample)

    result: Dict[str, dict] = {}
    for name, rows in grouped.items():
        cpu_values = [r["cpu_percent"] for r in rows if r.get("cpu_percent") is not None]
        mem_values = [r["mem_mib"] for r in rows if r.get("mem_mib") is not None]

        result[name] = {
            "cpu_min": min(cpu_values) if cpu_values else None,
            "cpu_max": max(cpu_values) if cpu_values else None,
            "cpu_mean": statistics.mean(cpu_values) if cpu_values else None,
            "mem_min_mib": min(mem_values) if mem_values else None,
            "mem_max_mib": max(mem_values) if mem_values else None,
            "mem_mean_mib": statistics.mean(mem_values) if mem_values else None,
            "samples": len(rows),
        }

    return result


def write_csv(path: str, fieldnames: List[str], rows: List[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_progress(out_dir: str, trial: int, total: int, note: str = "") -> None:
    progress_path = os.path.join(out_dir, "progress.txt")
    timestamp = datetime.utcnow().isoformat() + "Z"
    message = f"{timestamp} | trial {trial}/{total}"
    if note:
        message += f" | {note}"
    with open(progress_path, "w", encoding="utf-8") as f:
        f.write(message + "\n")
    print(message)


def try_plot(records: List[dict], out_dir: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    os.makedirs(out_dir, exist_ok=True)

    # Time series
    plt.figure(figsize=(10, 5))
    scenarios = sorted({r["scenario"] for r in records})
    for scenario in scenarios:
        series = [r for r in records if r["scenario"] == scenario]
        series.sort(key=lambda x: x["timestamp"])
        times = [i for i in range(len(series))]
        values = [r["latency_ms"] for r in series]
        plt.plot(times, values, label=scenario, linewidth=1)
    plt.title("Latency Time Series")
    plt.xlabel("Sample")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "latency_timeseries.png"))
    plt.close()

    # Histograms
    plt.figure(figsize=(10, 5))
    for scenario in scenarios:
        values = [r["latency_ms"] for r in records if r["scenario"] == scenario]
        if values:
            plt.hist(values, bins=30, alpha=0.5, label=scenario)
    plt.title("Latency Histogram")
    plt.xlabel("Latency (ms)")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "latency_histograms.png"))
    plt.close()

    # Percentiles
    plt.figure(figsize=(10, 5))
    x_labels = ["p50", "p75", "p90", "p95", "p99"]
    x = range(len(x_labels))
    width = 0.8 / max(len(scenarios), 1)
    for idx, scenario in enumerate(scenarios):
        values = [r["latency_ms"] for r in records if r["scenario"] == scenario]
        stats = summarize_latencies(values)
        perc_values = [stats["p50"], stats["p75"], stats["p90"], stats["p95"], stats["p99"]]
        offsets = [i + idx * width for i in x]
        plt.bar(offsets, perc_values, width=width, label=scenario)
    plt.xticks([i + width * (len(scenarios) / 2) for i in x], x_labels)
    plt.title("Latency Percentiles")
    plt.ylabel("Latency (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "latency_percentiles.png"))
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Lab 3 benchmark runner")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--baseline-requests", type=int, default=200)
    parser.add_argument("--baseline-concurrency", type=int, default=20)
    parser.add_argument("--max-concurrency", type=int, default=150)
    parser.add_argument("--degradation-step", type=int, default=20)
    parser.add_argument("--p95-threshold-ms", type=int, default=500)
    parser.add_argument("--error-rate-threshold", type=float, default=0.05)
    parser.add_argument("--compose-file", default="")
    parser.add_argument("--docker-per-trial", action="store_true")
    parser.add_argument("--docker-stats", nargs="*", default=[])
    parser.add_argument("--run-id", default="")
    args = parser.parse_args()

    run_id = args.run_id or f"run-{utc_now_tag()}"
    out_dir = os.path.join("benchmarks", run_id)
    os.makedirs(out_dir, exist_ok=True)

    metadata = {
        "run_id": run_id,
        "base_url": args.base_url,
        "trials": args.trials,
        "baseline_requests": args.baseline_requests,
        "baseline_concurrency": args.baseline_concurrency,
        "max_concurrency": args.max_concurrency,
        "degradation_step": args.degradation_step,
        "p95_threshold_ms": args.p95_threshold_ms,
        "error_rate_threshold": args.error_rate_threshold,
        "docker_per_trial": args.docker_per_trial,
        "compose_file": args.compose_file,
        "docker_stats": args.docker_stats,
        "started_at": datetime.utcnow().isoformat() + "Z",
    }

    all_records: List[dict] = []
    resource_samples: List[dict] = []

    for trial in range(1, args.trials + 1):
        write_progress(out_dir, trial, args.trials, "starting")
        if args.compose_file and args.docker_per_trial:
            docker_compose(args.compose_file, ["up", "-d", "--build"])
            wait_for_health(args.base_url, timeout_s=90)

        auth_email = f"bench_{run_id}_{trial}@example.com"
        auth_password = "benchmark123"
        ensure_auth_user(args.base_url, auth_email, auth_password)

        sampler = None
        if args.docker_stats:
            sampler = ResourceSampler(interval_s=2.0, docker_names=args.docker_stats)
            sampler.start()

        async def run_trial() -> None:
            async with httpx.AsyncClient(timeout=10) as client:
                # Scenario 1: baseline
                write_progress(out_dir, trial, args.trials, "baseline")
                baseline_requests = build_request_mix(
                    args.base_url,
                    args.baseline_requests,
                    auth_email,
                    auth_password,
                )
                baseline_results = await run_requests(
                    client, baseline_requests, args.baseline_concurrency
                )
                for item in baseline_results:
                    item["scenario"] = "baseline"
                    item["trial"] = trial
                    all_records.append(item)

                # Scenario 2: degradation point search
                write_progress(out_dir, trial, args.trials, "degradation_search")
                degradation_found = False
                for conc in range(args.degradation_step, args.max_concurrency + 1, args.degradation_step):
                    step_requests = build_request_mix(
                        args.base_url,
                        args.baseline_requests,
                        auth_email,
                        auth_password,
                    )
                    step_results = await run_requests(client, step_requests, conc)
                    for item in step_results:
                        item["scenario"] = f"degradation_{conc}"
                        item["trial"] = trial
                        all_records.append(item)

                    latencies = [r["latency_ms"] for r in step_results]
                    errors = [r for r in step_results if r["error"] or (r["status_code"] and r["status_code"] >= 500)]
                    p95 = percentile(latencies, 0.95) if latencies else None
                    error_rate = (len(errors) / len(step_results)) if step_results else 0

                    if p95 and (p95 > args.p95_threshold_ms or error_rate > args.error_rate_threshold):
                        degradation_found = True
                        break

                if not degradation_found:
                    # Ensure we still have a max load step
                    step_requests = build_request_mix(
                        args.base_url,
                        args.baseline_requests,
                        auth_email,
                        auth_password,
                    )
                    step_results = await run_requests(client, step_requests, args.max_concurrency)
                    for item in step_results:
                        item["scenario"] = f"degradation_{args.max_concurrency}"
                        item["trial"] = trial
                        all_records.append(item)

                # Scenario 3: recovery after overload
                write_progress(out_dir, trial, args.trials, "overload")
                overload_requests = build_request_mix(
                    args.base_url,
                    args.baseline_requests,
                    auth_email,
                    auth_password,
                )
                overload_results = await run_requests(client, overload_requests, args.max_concurrency)
                for item in overload_results:
                    item["scenario"] = "overload"
                    item["trial"] = trial
                    all_records.append(item)

                # Recovery windows
                for window in range(1, 6):
                    write_progress(out_dir, trial, args.trials, f"recovery_window_{window}")
                    recovery_requests = build_request_mix(
                        args.base_url,
                        args.baseline_requests // 4,
                        auth_email,
                        auth_password,
                    )
                    recovery_results = await run_requests(client, recovery_requests, args.baseline_concurrency)
                    for item in recovery_results:
                        item["scenario"] = f"recovery_window_{window}"
                        item["trial"] = trial
                        all_records.append(item)

        asyncio.run(run_trial())

        if sampler:
            sampler.stop()
            resource_samples.extend(sampler.samples)

        if args.compose_file and args.docker_per_trial:
            docker_compose(args.compose_file, ["down", "-v"])

        # Write partial results after each trial to show progress
        partial_raw = os.path.join(out_dir, "raw_requests_partial.csv")
        write_csv(
            partial_raw,
            [
                "timestamp",
                "scenario",
                "trial",
                "method",
                "endpoint",
                "status_code",
                "latency_ms",
                "error",
            ],
            all_records,
        )

        partial_summary = compute_summary(all_records)
        with open(os.path.join(out_dir, "summary_partial.json"), "w", encoding="utf-8") as f:
            json.dump(partial_summary, f, ensure_ascii=False, indent=2)

        if resource_samples:
            write_csv(
                os.path.join(out_dir, "resources_partial.csv"),
                ["timestamp", "name", "cpu_percent", "mem_mib", "net_mib", "block_mib"],
                resource_samples,
            )
            resources_summary = summarize_resources(resource_samples)
            with open(os.path.join(out_dir, "resources_summary_partial.json"), "w", encoding="utf-8") as f:
                json.dump(resources_summary, f, ensure_ascii=False, indent=2)

        write_progress(out_dir, trial, args.trials, "completed")

    # Write outputs
    write_csv(
        os.path.join(out_dir, "raw_requests.csv"),
        [
            "timestamp",
            "scenario",
            "trial",
            "method",
            "endpoint",
            "status_code",
            "latency_ms",
            "error",
        ],
        all_records,
    )

    summary = compute_summary(all_records)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    if resource_samples:
        write_csv(
            os.path.join(out_dir, "resources.csv"),
            ["timestamp", "name", "cpu_percent", "mem_mib", "net_mib", "block_mib"],
            resource_samples,
        )
        resources_summary = summarize_resources(resource_samples)
        with open(os.path.join(out_dir, "resources_summary.json"), "w", encoding="utf-8") as f:
            json.dump(resources_summary, f, ensure_ascii=False, indent=2)

    charts_dir = os.path.join(out_dir, "charts")
    try_plot(all_records, charts_dir)
    # Auto-generate resource charts if samples exist
    if resource_samples:
        try:
            from scripts.plot_resources import main as plot_resources_main
            import sys

            sys.argv = [
                "plot_resources",
                "--resources",
                os.path.join(out_dir, "resources.csv"),
                "--out-dir",
                charts_dir,
            ]
            plot_resources_main()
        except Exception:
            pass

    metadata["finished_at"] = datetime.utcnow().isoformat() + "Z"
    with open(os.path.join(out_dir, "run_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
