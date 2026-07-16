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


RESTITUTIONS = [1.0, 0.95, 0.9, 0.8]
DEFAULT_MODEL_DIR = ROOT / "models" / "restitution_sweep"
DEFAULT_RESULTS_DIR = ROOT / "results" / "restitution_sweep"


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--controller",
        default="ppo",
        choices=["ppo", "a2c", "sac", "zero", "random", "sinusoidal", "pumping", "phase_pumping"],
    )
    parser.add_argument(
        "--reward-variants",
        nargs="+",
        default=["z_penalty", "swing_growth"],
        choices=["sparse_only", "z_penalty", "deadzone", "swing_growth"],
    )
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--timesteps", type=int, default=500000)
    parser.add_argument("--rollout-steps", type=int, default=100)
    parser.add_argument("--collision-reward-weight", type=float, default=1.0)
    parser.add_argument("--z-penalty-weight", type=float, default=0.01)
    parser.add_argument("--z-tolerance", type=float, default=0.0)
    parser.add_argument("--swing-growth-weight", type=float, default=0.05)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--verbose", type=int, default=0)
    parser.add_argument("--sinusoidal-amplitude", type=float, default=7.5)
    parser.add_argument("--sinusoidal-frequency-hz", type=float, default=1.2)
    parser.add_argument("--sinusoidal-phase", type=float, default=0.0)
    parser.add_argument("--pumping-gain", type=float, default=6.0)
    parser.add_argument("--pumping-theta-deadband", type=float, default=0.08)
    parser.add_argument("--pumping-damping-gain", type=float, default=1.5)
    parser.add_argument("--phase-pumping-gain", type=float, default=8.0)
    parser.add_argument("--phase-pumping-phase-lead", type=float, default=0.6)
    parser.add_argument("--phase-pumping-omega-scale", type=float, default=6.0)
    parser.add_argument("--phase-pumping-z-feedback-gain", type=float, default=0.5)
    parser.add_argument("--phase-pumping-z-dot-feedback-gain", type=float, default=0.15)
    return parser.parse_args()


def build_env(args, reward_variant, restitution):
    return LattoLatto(
        z_position_penalty_weight=args.z_penalty_weight,
        z_position_tolerance=args.z_tolerance,
        collision_reward_weight=args.collision_reward_weight,
        collision_restitution=restitution,
        reward_variant=reward_variant,
        swing_growth_reward_weight=args.swing_growth_weight,
    )


def controller_kwargs_for(args):
    if args.controller == "sinusoidal":
        return {
            "amplitude": args.sinusoidal_amplitude,
            "frequency_hz": args.sinusoidal_frequency_hz,
            "phase": args.sinusoidal_phase,
        }
    if args.controller == "pumping":
        return {
            "gain": args.pumping_gain,
            "theta_deadband": args.pumping_theta_deadband,
            "damping_gain": args.pumping_damping_gain,
        }
    if args.controller == "phase_pumping":
        return {
            "gain": args.phase_pumping_gain,
            "phase_lead": args.phase_pumping_phase_lead,
            "omega_scale": args.phase_pumping_omega_scale,
            "z_feedback_gain": args.phase_pumping_z_feedback_gain,
            "z_dot_feedback_gain": args.phase_pumping_z_dot_feedback_gain,
        }
    return {}


def main():
    args = parse_args()
    ensure_dir(args.model_dir)
    ensure_dir(args.results_dir)

    global_summary = []
    for reward_variant in args.reward_variants:
        reward_variant_summary = []
        for restitution in RESTITUTIONS:
            restitution_results = []
            for seed in args.seeds:
                set_global_seed(seed)
                env = build_env(args, reward_variant=reward_variant, restitution=restitution)
                env.reset(seed=seed)
                controller = build_controller(
                    controller_name=args.controller,
                    env=env,
                    seed=seed,
                    verbose=args.verbose,
                    controller_kwargs=controller_kwargs_for(args),
                )
                train_controller(controller, total_timesteps=args.timesteps)

                run_name = build_run_name(
                    controller_name=args.controller,
                    reward_variant=reward_variant,
                    restitution=restitution,
                    seed=seed,
                    extras={
                        "alpha": args.z_penalty_weight,
                        "ztol": args.z_tolerance,
                        "wc": args.collision_reward_weight,
                        "beta": args.swing_growth_weight if reward_variant == "swing_growth" else 0.0,
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
                    "reward_variant": reward_variant,
                    "collision_restitution": restitution,
                    "collision_reward_weight": args.collision_reward_weight,
                    "z_position_penalty_weight": args.z_penalty_weight,
                    "z_position_tolerance": args.z_tolerance,
                    "swing_growth_reward_weight": args.swing_growth_weight,
                    "model_path": f"{model_path}.zip" if is_rl_algorithm(args.controller) else f"{model_path}.json",
                    "evaluation": evaluation,
                }
                save_json(args.results_dir / f"{run_name}.json", result_payload)
                restitution_results.append(evaluation)
                env.close()
                print(
                    {
                        "reward_variant": reward_variant,
                        "restitution": restitution,
                        "seed": seed,
                        "reward_sum": round(evaluation["reward_sum"], 6),
                        "alternating_collisions": evaluation["alternating_collisions"],
                        "longest_alternating_streak": evaluation["longest_alternating_streak"],
                        "max_abs_z": round(evaluation["max_abs_z"], 6),
                    }
                )

            restitution_summary = summarize_runs(restitution_results)
            reward_variant_summary.append(
                {
                    "collision_restitution": restitution,
                    "summary": restitution_summary,
                }
            )
            global_summary.append(
                {
                    "reward_variant": reward_variant,
                    "collision_restitution": restitution,
                    "summary": restitution_summary,
                }
            )

        save_json(
            args.results_dir / f"{args.controller}_{reward_variant}_restitution_sweep_summary.json",
            {
                "date": "2026-07-16",
                "controller": args.controller,
                "controller_family": "rl" if is_rl_algorithm(args.controller) else "heuristic",
                "reward_variant": reward_variant,
                "seeds": args.seeds,
                "timesteps": args.timesteps,
                "rollout_steps": args.rollout_steps,
                "collision_reward_weight": args.collision_reward_weight,
                "z_position_penalty_weight": args.z_penalty_weight,
                "z_position_tolerance": args.z_tolerance,
                "swing_growth_reward_weight": args.swing_growth_weight,
                "results": reward_variant_summary,
            },
        )

    save_json(
        args.results_dir / f"{args.controller}_restitution_sweep_overview.json",
        {
            "date": "2026-07-16",
            "controller": args.controller,
            "reward_variants": args.reward_variants,
            "results": global_summary,
        },
    )


if __name__ == "__main__":
    main()
