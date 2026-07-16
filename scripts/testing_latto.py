from argparse import ArgumentParser
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import (
    ensure_dir,
    evaluate_controller,
    save_json,
)
from latto_latto_model import LattoLatto

from stable_baselines3 import A2C, PPO, SAC


MODEL_MAP = {"a2c": A2C, "ppo": PPO, "sac": SAC}

DEFAULT_MODEL_PATH = ROOT / "models" / "baselines" / "ppo_z_penalty_e_0p900_seed_0_alpha_0p100_ztol_0p000_wc_1p000_beta_0p000"
DEFAULT_RESULTS_DIR = ROOT / "results" / "testing"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("model_path", nargs="?", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--controller", default="ppo", choices=["ppo", "a2c", "sac", "zero", "random", "sinusoidal"])
    parser.add_argument("--reward-variant", default="z_penalty", choices=["sparse_only", "z_penalty", "deadzone", "swing_growth"])
    parser.add_argument("--rollout-steps", type=int, default=100)
    parser.add_argument("--collision-restitution", type=float, default=0.9)
    parser.add_argument("--collision-reward-weight", type=float, default=1.0)
    parser.add_argument("--z-penalty-weight", type=float, default=0.1)
    parser.add_argument("--z-tolerance", type=float, default=0.0)
    parser.add_argument("--swing-growth-weight", type=float, default=0.0)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--output-prefix", default="testing")
    parser.add_argument("--render", action="store_true")
    return parser.parse_args()


def load_controller(args, env):
    if args.controller in MODEL_MAP:
        return MODEL_MAP[args.controller].load(args.model_path, env=env)
    metadata = Path(args.model_path)
    if metadata.suffix != ".json":
        metadata = Path(f"{args.model_path}.json")
    payload = {}
    if metadata.exists():
        payload = json.loads(metadata.read_text())
    if args.controller == "zero":
        from benchmark_utils import ZeroController

        return ZeroController(env=env, seed=payload.get("seed", 0))
    if args.controller == "random":
        from benchmark_utils import RandomController

        return RandomController(env=env, seed=payload.get("seed", 0))
    if args.controller == "sinusoidal":
        from benchmark_utils import SinusoidalController

        return SinusoidalController(
            env=env,
            seed=payload.get("seed", 0),
            amplitude=payload.get("amplitude", 7.5),
            frequency_hz=payload.get("frequency_hz", 1.2),
            phase=payload.get("phase", 0.0),
        )
    raise ValueError(f"Unsupported controller: {args.controller}")


def main():
    args = parse_args()
    ensure_dir(args.results_dir)

    env = LattoLatto(
        z_position_penalty_weight=args.z_penalty_weight,
        z_position_tolerance=args.z_tolerance,
        collision_reward_weight=args.collision_reward_weight,
        collision_restitution=args.collision_restitution,
        reward_variant=args.reward_variant,
        swing_growth_reward_weight=args.swing_growth_weight,
    )

    controller = load_controller(args, env)
    evaluation = evaluate_controller(
        controller=controller,
        env=env,
        rollout_steps=args.rollout_steps,
        deterministic=True,
        render=args.render,
    )

    action_plot_path = args.results_dir / f"{args.output_prefix}_action_trace.png"
    pose_plot_path = args.results_dir / f"{args.output_prefix}_pose_trace.png"
    metrics_path = args.results_dir / f"{args.output_prefix}_metrics.json"

    fig1, ax1 = plt.subplots()
    ax1.plot(evaluation["time"], evaluation["action"], "-r")
    ax1.set_xlabel("time")
    ax1.set_ylabel("acceleration")
    fig1.tight_layout()
    fig1.savefig(action_plot_path)
    plt.close(fig1)

    fig2, (ax2, ax3) = plt.subplots(2, 1, sharex=True)
    ax2.plot(evaluation["time"], evaluation["z"], "-b")
    ax2.set_ylabel("pivot z")
    ax2.set_title("Latto-Latto Pose")
    ax3.plot(evaluation["time"], evaluation["theta"], "-g")
    ax3.set_xlabel("time")
    ax3.set_ylabel("theta")
    fig2.tight_layout()
    fig2.savefig(pose_plot_path)
    plt.close(fig2)

    save_json(
        metrics_path,
        {
            "model_path": args.model_path,
            "controller": args.controller,
            "reward_variant": args.reward_variant,
            "collision_restitution": args.collision_restitution,
            "collision_reward_weight": args.collision_reward_weight,
            "z_position_penalty_weight": args.z_penalty_weight,
            "z_position_tolerance": args.z_tolerance,
            "swing_growth_reward_weight": args.swing_growth_weight,
            "evaluation": evaluation,
        },
    )

    env.close()
    print(f"Saved action plot to {action_plot_path}")
    print(f"Saved pose plot to {pose_plot_path}")
    print(f"Saved metrics to {metrics_path}")


if __name__ == "__main__":
    main()
