import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

from latto_latto_model import LattoLatto


ALPHAS = [0.01, 0.02, 0.05]
TOTAL_TIMESTEPS = 500000
ROLLOUT_STEPS = 100
COLLISION_RESTITUTION = 0.9
MODEL_PREFIX = "ppo_latto_inelastic_alpha"
RESULTS_JSON = "alpha_sweep_inelastic_results.json"
POSE_PLOT = "alpha_pose_inelastic_comparison.png"


def alpha_tag(alpha):
    return f"{alpha:.3f}".replace(".", "p")


def model_path(alpha):
    return f"{MODEL_PREFIX}_{alpha_tag(alpha)}"


def train_model(alpha):
    env = LattoLatto(
        z_position_penalty_weight=alpha,
        collision_restitution=COLLISION_RESTITUTION,
    )
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=TOTAL_TIMESTEPS)
    model.save(model_path(alpha))
    env.close()
    return model


def evaluate_model(alpha):
    env = LattoLatto(
        z_position_penalty_weight=alpha,
        collision_restitution=COLLISION_RESTITUTION,
    )
    model = PPO.load(model_path(alpha), env=env)
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
        sparse_reward_hits += int(info["sparse_reward"] > 0)
        times += env.delta_t
        if terminated:
            break

    env.close()

    return {
        "alpha": alpha,
        "collision_restitution": COLLISION_RESTITUTION,
        "model_path": f"{model_path(alpha)}.zip",
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
                "collision_restitution": result["collision_restitution"],
                "model_path": result["model_path"],
                "reward_sum": result["reward_sum"],
                "max_abs_z": result["max_abs_z"],
                "mean_abs_z": result["mean_abs_z"],
                "alternating_collisions": result["alternating_collisions"],
            }
        )

    Path(RESULTS_JSON).write_text(json.dumps(summary, indent=2))


def plot_comparison(results):
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    for result in results:
        label = f"alpha={result['alpha']:.2f}"
        ax1.plot(result["time"], result["z"], label=label)
        ax2.plot(result["time"], result["theta"], label=label)

    ax1.set_ylabel("pivot z")
    ax1.set_title(
        "Latto-Latto Pose Comparison Across Reward Weights "
        f"(e={COLLISION_RESTITUTION})"
    )
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel("time")
    ax2.set_ylabel("theta")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(POSE_PLOT)
    plt.close(fig)


def main():
    results = []

    for alpha in ALPHAS:
        print(f"=== Training alpha={alpha:.2f} ===")
        train_model(alpha)
        print(f"=== Evaluating alpha={alpha:.2f} ===")
        result = evaluate_model(alpha)
        results.append(result)
        print(
            {
                "alpha": result["alpha"],
                "reward_sum": round(result["reward_sum"], 6),
                "max_abs_z": round(result["max_abs_z"], 6),
                "mean_abs_z": round(result["mean_abs_z"], 6),
                "alternating_collisions": result["alternating_collisions"],
            }
        )

    save_results(results)
    plot_comparison(results)
    print(f"Saved summary to {RESULTS_JSON}")
    print(f"Saved pose comparison plot to {POSE_PLOT}")


if __name__ == "__main__":
    main()
