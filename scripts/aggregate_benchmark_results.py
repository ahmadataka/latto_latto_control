from argparse import ArgumentParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import save_json, summarize_runs


DEFAULT_RESULTS_DIR = ROOT / "results" / "benchmark"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--pattern", default="*.json")
    parser.add_argument("--output-name", default="aggregated_summary.json")
    return parser.parse_args()


def load_result_files(results_dir, pattern):
    payloads = []
    for path in sorted(results_dir.glob(pattern)):
        if path.name.endswith("_summary.json") or path.name == "aggregated_summary.json":
            continue
        payload = json.loads(path.read_text())
        if "evaluation" not in payload:
            continue
        payloads.append(payload)
    return payloads


def main():
    args = parse_args()
    payloads = load_result_files(args.results_dir, args.pattern)
    evaluations = [payload["evaluation"] for payload in payloads]
    summary = summarize_runs(evaluations)

    grouped = {}
    for payload in payloads:
        key = "|".join(
            [
                payload["algorithm"],
                payload["reward_variant"],
                f"e={payload['collision_restitution']}",
            ]
        )
        grouped.setdefault(key, []).append(payload["evaluation"])

    grouped_summary = {
        key: summarize_runs(results)
        for key, results in grouped.items()
    }

    output_path = args.results_dir / args.output_name
    save_json(
        output_path,
        {
            "num_runs": len(payloads),
            "overall_summary": summary,
            "grouped_summary": grouped_summary,
        },
    )
    print(f"Saved aggregated summary to {output_path}")


if __name__ == "__main__":
    main()
