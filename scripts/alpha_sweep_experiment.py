from argparse import ArgumentParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from benchmark_utils import (
    build_model,
    ensure_dir,
    evaluate_model,
    format_float_tag,
    save_json,
    set_global_seed,
    summarize_runs,
)
from latto_latto_model import LattoLatto


ALPHAS = [0.01, 0.02, 0.05]
DEFAULT_MODEL_DIR = ROOT / "models" / "alpha_sweep_inelastic"
DEFAULT_RESULTS_DIR = ROOT / "results" / "alpha_sweep_inelastic"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--algorithm", default="ppo", choices=["ppo", "a2c", "sac"])
    parser.add_argument("--reward-variant", default="z_penalty", choices=["sparse_only", "z_penalty", "deadzone", "swing_growth"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--timesteps", type=int, default=500000)
    parser.add_argument("--rollout-steps", type=int, default=100)
    parser.add_argument("--collision-restitution", type=float, default=0.9)
    parser.add_argument("--collision-reward-weight", type=float, default=1.0)
    parser.add_argument("--z-tolerance", type=float, default=0.0)
    parser.add_argument("--swing-growth-weight", type=float, default=0.0)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--verbose", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_dir(args.model_dir)
    ensure_dir(args.results_dir)

    experiment_summary = []
    for alpha in ALPHAS:
        alpha_results = []
        for seed in args.seeds:
            set_global_seed(seed)
            env = LattoLatto(
                z_position_penalty_weight=alpha,
                z_position_tolerance=args.z_tolerance,
                collision_reward_weight=args.collision_reward_weight,
                collision_restitution=args.collision_restitution,
                reward_variant=args.reward_variant,
                swing_growth_reward_weight=args.swing_growth_weight,
            )
            env.reset(seed=seed)

            model = build_model(args.algorithm, env, seed=seed, verbose=args.verbose)
            model.learn(total_timesteps=args.timesteps)

            run_name = (
                f"{args.algorithm}_{args.reward_variant}_alpha_{format_float_tag(alpha)}"
                f"_e_{format_float_tag(args.collision_restitution)}_seed_{seed}"
            )
            model_path = args.model_dir / run_name
            model.save(str(model_path))

            evaluation = evaluate_model(model, env, rollout_steps=args.rollout_steps)
            payload = {
                "run_name": run_name,
                "algorithm": args.algorithm,
                "seed": seed,
                "alpha": alpha,
                "reward_variant": args.reward_variant,
                "collision_restitution": args.collision_restitution,
                "collision_reward_weight": args.collision_reward_weight,
                "z_position_tolerance": args.z_tolerance,
                "swing_growth_reward_weight": args.swing_growth_weight,
                "model_path": f"{model_path}.zip",
                "evaluation": evaluation,
            }
            save_json(args.results_dir / f"{run_name}.json", payload)
            alpha_results.append(evaluation)
            env.close()
            print(
                {
                    "alpha": alpha,
                    "seed": seed,
                    "reward_sum": round(evaluation["reward_sum"], 6),
                    "alternating_collisions": evaluation["alternating_collisions"],
                    "longest_alternating_streak": evaluation["longest_alternating_streak"],
                }
            )

        experiment_summary.append(
            {
                "alpha": alpha,
                "summary": summarize_runs(alpha_results),
            }
        )

    summary_path = args.results_dir / "alpha_sweep_inelastic_results.json"
    save_json(
        summary_path,
        {
            "date": "2026-07-16",
            "algorithm": args.algorithm,
            "reward_variant": args.reward_variant,
            "seeds": args.seeds,
            "timesteps": args.timesteps,
            "rollout_steps": args.rollout_steps,
            "collision_restitution": args.collision_restitution,
            "collision_reward_weight": args.collision_reward_weight,
            "z_position_tolerance": args.z_tolerance,
            "swing_growth_reward_weight": args.swing_growth_weight,
            "results": experiment_summary,
        },
    )
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
