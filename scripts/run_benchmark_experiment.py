from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import (
    build_controller,
    build_run_name,
    ensure_dir,
    evaluate_controller,
    is_rl_algorithm,
    save_json,
    set_global_seed,
    summarize_runs,
    train_controller,
)
from latto_latto_model import LattoLatto


DEFAULT_MODEL_DIR = ROOT / "models" / "benchmark"
DEFAULT_RESULTS_DIR = ROOT / "results" / "benchmark"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--controller",
        default="ppo",
        choices=["ppo", "a2c", "sac", "zero", "random", "sinusoidal"],
    )
    parser.add_argument("--reward-variant", default="z_penalty", choices=["sparse_only", "z_penalty", "deadzone", "swing_growth"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--timesteps", type=int, default=500000)
    parser.add_argument("--rollout-steps", type=int, default=100)
    parser.add_argument("--collision-restitution", type=float, default=0.9)
    parser.add_argument("--collision-reward-weight", type=float, default=1.0)
    parser.add_argument("--z-penalty-weight", type=float, default=0.1)
    parser.add_argument("--z-tolerance", type=float, default=0.0)
    parser.add_argument("--swing-growth-weight", type=float, default=0.0)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--verbose", type=int, default=0)
    parser.add_argument("--sinusoidal-amplitude", type=float, default=7.5)
    parser.add_argument("--sinusoidal-frequency-hz", type=float, default=1.2)
    parser.add_argument("--sinusoidal-phase", type=float, default=0.0)
    return parser.parse_args()


def build_env(args):
    return LattoLatto(
        z_position_penalty_weight=args.z_penalty_weight,
        z_position_tolerance=args.z_tolerance,
        collision_reward_weight=args.collision_reward_weight,
        collision_restitution=args.collision_restitution,
        reward_variant=args.reward_variant,
        swing_growth_reward_weight=args.swing_growth_weight,
    )


def main():
    args = parse_args()
    ensure_dir(args.model_dir)
    ensure_dir(args.results_dir)

    all_results = []
    run_group_name = build_run_name(
        controller_name=args.controller,
        reward_variant=args.reward_variant,
        restitution=args.collision_restitution,
        seed="multi",
        extras={
            "alpha": args.z_penalty_weight,
            "ztol": args.z_tolerance,
            "wc": args.collision_reward_weight,
            "beta": args.swing_growth_weight,
        },
    )

    for seed in args.seeds:
        set_global_seed(seed)
        env = build_env(args)
        env.reset(seed=seed)
        controller = build_controller(
            controller_name=args.controller,
            env=env,
            seed=seed,
            verbose=args.verbose,
            controller_kwargs={
                "amplitude": args.sinusoidal_amplitude,
                "frequency_hz": args.sinusoidal_frequency_hz,
                "phase": args.sinusoidal_phase,
            },
        )
        train_controller(controller, total_timesteps=args.timesteps)

        run_name = build_run_name(
            controller_name=args.controller,
            reward_variant=args.reward_variant,
            restitution=args.collision_restitution,
            seed=seed,
            extras={
                "alpha": args.z_penalty_weight,
                "ztol": args.z_tolerance,
                "wc": args.collision_reward_weight,
                "beta": args.swing_growth_weight,
            },
        )
        model_path = args.model_dir / run_name
        controller.save(str(model_path))

        evaluation = evaluate_controller(
            controller=controller,
            env=env,
            rollout_steps=args.rollout_steps,
            deterministic=True,
            render=False,
        )
        result_payload = {
            "run_name": run_name,
            "controller": args.controller,
            "controller_family": "rl" if is_rl_algorithm(args.controller) else "heuristic",
            "seed": seed,
            "timesteps": args.timesteps,
            "reward_variant": args.reward_variant,
            "collision_restitution": args.collision_restitution,
            "collision_reward_weight": args.collision_reward_weight,
            "z_position_penalty_weight": args.z_penalty_weight,
            "z_position_tolerance": args.z_tolerance,
            "swing_growth_reward_weight": args.swing_growth_weight,
            "model_path": f"{model_path}.zip",
            "evaluation": evaluation,
        }
        save_json(args.results_dir / f"{run_name}.json", result_payload)
        all_results.append(evaluation)
        env.close()
        print(
            {
                "seed": seed,
                "reward_sum": round(evaluation["reward_sum"], 6),
                "alternating_collisions": evaluation["alternating_collisions"],
                "longest_alternating_streak": evaluation["longest_alternating_streak"],
                "max_abs_z": round(evaluation["max_abs_z"], 6),
            }
        )

    summary = summarize_runs(all_results)
    summary_payload = {
        "run_group_name": run_group_name,
        "controller": args.controller,
        "controller_family": "rl" if is_rl_algorithm(args.controller) else "heuristic",
        "seeds": args.seeds,
        "timesteps": args.timesteps,
        "reward_variant": args.reward_variant,
        "collision_restitution": args.collision_restitution,
        "collision_reward_weight": args.collision_reward_weight,
        "z_position_penalty_weight": args.z_penalty_weight,
        "z_position_tolerance": args.z_tolerance,
        "swing_growth_reward_weight": args.swing_growth_weight,
        "summary": summary,
    }
    summary_path = args.results_dir / f"{run_group_name}_summary.json"
    save_json(summary_path, summary_payload)
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
