from argparse import ArgumentParser
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from stable_baselines3 import A2C, PPO, SAC

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import ensure_dir, evaluate_model, save_json
from latto_latto_model import LattoLatto


MODEL_MAP = {
    "a2c": A2C,
    "ppo": PPO,
    "sac": SAC,
}

DEFAULT_MODEL_PATH = ROOT / "models" / "baselines" / "ppo_z_penalty_e_0p900_seed_0_alpha_0p100_ztol_0p000_wc_1p000_beta_0p000"
DEFAULT_RESULTS_DIR = ROOT / "results" / "testing"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("model_path", nargs="?", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--algorithm", default="ppo", choices=["ppo", "a2c", "sac"])
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

    model_class = MODEL_MAP[args.algorithm]
    model = model_class.load(args.model_path, env=env)
    evaluation = evaluate_model(
        model=model,
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
            "algorithm": args.algorithm,
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
