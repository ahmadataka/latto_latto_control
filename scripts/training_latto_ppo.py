from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import (
    build_controller,
    build_run_name,
    ensure_dir,
    save_json,
    set_global_seed,
    train_controller,
)
from latto_latto_model import LattoLatto


DEFAULT_MODEL_DIR = ROOT / "models" / "baselines"
DEFAULT_RESULTS_DIR = ROOT / "results" / "baselines"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--algorithm", default="ppo", choices=["ppo", "a2c", "sac"])
    parser.add_argument("--reward-variant", default="z_penalty", choices=["sparse_only", "z_penalty", "deadzone", "swing_growth"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--timesteps", type=int, default=500000)
    parser.add_argument("--collision-restitution", type=float, default=0.9)
    parser.add_argument("--collision-reward-weight", type=float, default=1.0)
    parser.add_argument("--z-penalty-weight", type=float, default=0.1)
    parser.add_argument("--z-tolerance", type=float, default=0.0)
    parser.add_argument("--swing-growth-weight", type=float, default=0.0)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--verbose", type=int, default=1)
    return parser.parse_args()


def main():
    args = parse_args()
    set_global_seed(args.seed)

    env = LattoLatto(
        z_position_penalty_weight=args.z_penalty_weight,
        z_position_tolerance=args.z_tolerance,
        collision_reward_weight=args.collision_reward_weight,
        collision_restitution=args.collision_restitution,
        reward_variant=args.reward_variant,
        swing_growth_reward_weight=args.swing_growth_weight,
    )
    env.reset(seed=args.seed)

    run_name = build_run_name(
        controller_name=args.algorithm,
        reward_variant=args.reward_variant,
        restitution=args.collision_restitution,
        seed=args.seed,
        extras={
            "alpha": args.z_penalty_weight,
            "ztol": args.z_tolerance,
            "wc": args.collision_reward_weight,
            "beta": args.swing_growth_weight,
        },
    )

    ensure_dir(args.model_dir)
    ensure_dir(args.results_dir)

    controller = build_controller(args.algorithm, env, seed=args.seed, verbose=args.verbose)
    train_controller(controller, total_timesteps=args.timesteps)

    model_path = args.model_dir / run_name
    controller.save(str(model_path))

    metadata_path = args.results_dir / f"{run_name}_train_metadata.json"
    save_json(
        metadata_path,
        {
            "run_name": run_name,
            "algorithm": args.algorithm,
            "seed": args.seed,
            "timesteps": args.timesteps,
            "reward_variant": args.reward_variant,
            "collision_restitution": args.collision_restitution,
            "collision_reward_weight": args.collision_reward_weight,
            "z_position_penalty_weight": args.z_penalty_weight,
            "z_position_tolerance": args.z_tolerance,
            "swing_growth_reward_weight": args.swing_growth_weight,
            "model_path": f"{model_path}.zip",
        },
    )
    env.close()
    print(f"Saved model to {model_path}.zip")
    print(f"Saved metadata to {metadata_path}")


if __name__ == "__main__":
    main()
