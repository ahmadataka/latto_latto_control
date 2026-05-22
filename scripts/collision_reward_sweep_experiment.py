import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from latto_latto_model import LattoLatto


COLLISION_REWARD_WEIGHTS = [1.0, 2.0, 5.0]
TOTAL_TIMESTEPS = 500000
ROLLOUT_STEPS = 100
COLLISION_RESTITUTION = 0.9
ALPHA = 0.1
Z_TOL = 0.08
MODEL_DIR = ROOT / "models" / "collision_reward_sweep_inelastic"
RESULTS_PATH = ROOT / "results" / "collision_reward_sweep_inelastic" / "collision_reward_sweep_inelastic_results.json"
POSE_PLOT_PATH = ROOT / "results" / "collision_reward_sweep_inelastic" / "collision_reward_pose_inelastic_comparison.png"


def reward_weight_tag(weight):
    return f"{weight:.1f}".replace(".", "p")


def model_path(weight):
    return MODEL_DIR / f"ppo_latto_inelastic_wc_{reward_weight_tag(weight)}"


def build_env(weight):
    return LattoLatto(
        z_position_penalty_weight=ALPHA,
        z_position_tolerance=Z_TOL,
        collision_reward_weight=weight,
        collision_restitution=COLLISION_RESTITUTION,
    )


def train_model(weight):
    env = build_env(weight)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    model.save(model_path(weight))
    env.close()


def evaluate_model(weight):
    env = build_env(weight)
    model = PPO.load(model_path(weight), env=env)
    observation = env.reset()

    time_array = []
    z_array = []
    theta_array = []
    reward_array = []
    sparse_reward_hits = 0
    times = 0.0

    for _ in range(ROLLOUT_STEPS):
        action, _state = model.predict(observation[0], deterministic=True)
        observation, reward, terminated, info = env.step(action)
        time_array.append(times)
        z_array.append(float(env.state[0]))
        theta_array.append(float(env.state[2]))
        reward_array.append(float(reward))
        sparse_reward_hits += int(info["collision_flag"] and info["sparse_reward"] > 0)
        times += env.delta_t
        if terminated:
            break

    env.close()

    return {
        "alpha": ALPHA,
        "z_tol": Z_TOL,
        "collision_reward_weight": weight,
        "collision_restitution": COLLISION_RESTITUTION,
        "model_path": f"{model_path(weight)}.zip",
        "time": time_array,
        "z": z_array,
        "theta": theta_array,
        "reward_sum": float(np.sum(reward_array)),
        "max_abs_z": float(np.max(np.abs(z_array))),
        "mean_abs_z": float(np.mean(np.abs(z_array))),
        "alternating_collisions": sparse_reward_hits,
    }


def save_results(results):
    summary = []
    for result in results:
        summary.append(
            {
                "alpha": result["alpha"],
                "z_tol": result["z_tol"],
                "collision_reward_weight": result["collision_reward_weight"],
                "collision_restitution": result["collision_restitution"],
                "model_path": result["model_path"],
                "reward_sum": result["reward_sum"],
                "max_abs_z": result["max_abs_z"],
                "mean_abs_z": result["mean_abs_z"],
                "alternating_collisions": result["alternating_collisions"],
            }
        )

    RESULTS_PATH.write_text(json.dumps(summary, indent=2))


def plot_comparison(results):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    for result in results:
        label = f"w_c={result['collision_reward_weight']:.1f}"
        ax1.plot(result["time"], result["z"], label=label)
        ax2.plot(result["time"], result["theta"], label=label)

    ax1.set_ylabel("pivot z")
    ax1.set_title(
        "Latto-Latto Pose Comparison Across Collision Reward Weights "
        f"(alpha={ALPHA}, z_tol={Z_TOL}, e={COLLISION_RESTITUTION})"
    )
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("time")
    ax2.set_ylabel("theta")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(POSE_PLOT_PATH)
    plt.close(fig)


def main():
    results = []

    for weight in COLLISION_REWARD_WEIGHTS:
        print(f"=== Training collision_reward_weight={weight:.1f} ===")
        train_model(weight)
        print(f"=== Evaluating collision_reward_weight={weight:.1f} ===")
        result = evaluate_model(weight)
        results.append(result)
        print(
            {
                "collision_reward_weight": result["collision_reward_weight"],
                "reward_sum": round(result["reward_sum"], 6),
                "max_abs_z": round(result["max_abs_z"], 6),
                "mean_abs_z": round(result["mean_abs_z"], 6),
                "alternating_collisions": result["alternating_collisions"],
            }
        )

    save_results(results)
    plot_comparison(results)
    print(f"Saved summary to {RESULTS_PATH}")
    print(f"Saved pose comparison plot to {POSE_PLOT_PATH}")


if __name__ == "__main__":
    main()
