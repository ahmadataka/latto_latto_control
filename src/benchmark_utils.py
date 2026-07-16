import json
import random
from pathlib import Path

import numpy as np
from stable_baselines3 import A2C, PPO, SAC


ALGORITHM_MAP = {
    "a2c": A2C,
    "ppo": PPO,
    "sac": SAC,
}


def ensure_parent_dir(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def set_global_seed(seed):
    random.seed(seed)
    np.random.seed(seed)


def format_float_tag(value, precision=3):
    return f"{value:.{precision}f}".replace(".", "p")


def build_run_name(algorithm, reward_variant, restitution, seed, extras=None):
    parts = [
        algorithm.lower(),
        reward_variant,
        f"e_{format_float_tag(restitution)}",
        f"seed_{seed}",
    ]
    if extras:
        for key, value in extras.items():
            if isinstance(value, float):
                value = format_float_tag(value)
            parts.append(f"{key}_{value}")
    return "_".join(parts)


def build_model(algorithm, env, seed, verbose=1):
    model_class = ALGORITHM_MAP[algorithm.lower()]
    return model_class("MlpPolicy", env, verbose=verbose, seed=seed)


def evaluate_model(model, env, rollout_steps, deterministic=True, render=False):
    observation = env.reset()

    time_trace = []
    action_trace = []
    z_trace = []
    theta_trace = []
    reward_trace = []
    sparse_reward_trace = []
    swing_growth_trace = []
    collision_energy_loss_trace = []
    collision_time_trace = []
    collision_energy_loss_events = []

    reward_sum = 0.0
    alternating_collisions = 0
    total_collisions = 0
    longest_alternating_streak = 0
    current_alternating_streak = 0
    time_to_first_alternating_collision = None
    times = 0.0

    for _ in range(rollout_steps):
        action, _state = model.predict(observation[0], deterministic=deterministic)
        observation, reward, terminated, info = env.step(action)

        if render:
            env.render()

        time_trace.append(times)
        action_trace.append(float(action[0]))
        z_trace.append(float(env.state[0]))
        theta_trace.append(float(env.state[2]))
        reward_trace.append(float(reward))
        sparse_reward_trace.append(float(info["sparse_reward"]))
        swing_growth_trace.append(float(info["swing_growth_reward"]))
        collision_energy_loss_trace.append(float(info["collision_energy_loss"]))

        reward_sum += float(reward)
        if info["collision_flag"]:
            total_collisions += 1
            collision_time_trace.append(times)
            collision_energy_loss_events.append(float(info["collision_energy_loss"]))
            if info["alternating_collision"]:
                alternating_collisions += 1
                current_alternating_streak += 1
                longest_alternating_streak = max(
                    longest_alternating_streak,
                    current_alternating_streak,
                )
                if time_to_first_alternating_collision is None:
                    time_to_first_alternating_collision = times
            else:
                current_alternating_streak = 0

        times += env.delta_t
        if terminated:
            break

    mean_collision_energy_loss = 0.0
    if collision_energy_loss_events:
        mean_collision_energy_loss = float(np.mean(collision_energy_loss_events))

    return {
        "reward_sum": reward_sum,
        "alternating_collisions": alternating_collisions,
        "longest_alternating_streak": longest_alternating_streak,
        "total_collisions": total_collisions,
        "time_to_first_alternating_collision": time_to_first_alternating_collision,
        "mean_abs_z": float(np.mean(np.abs(z_trace))) if z_trace else 0.0,
        "max_abs_z": float(np.max(np.abs(z_trace))) if z_trace else 0.0,
        "mean_collision_energy_loss": mean_collision_energy_loss,
        "time": time_trace,
        "action": action_trace,
        "z": z_trace,
        "theta": theta_trace,
        "reward": reward_trace,
        "sparse_reward": sparse_reward_trace,
        "swing_growth_reward": swing_growth_trace,
        "collision_energy_loss": collision_energy_loss_trace,
        "collision_times": collision_time_trace,
    }


def save_json(path, payload):
    ensure_parent_dir(path)
    Path(path).write_text(json.dumps(payload, indent=2))


def summarize_runs(results):
    if not results:
        return {}

    metric_names = [
        "reward_sum",
        "alternating_collisions",
        "longest_alternating_streak",
        "total_collisions",
        "time_to_first_alternating_collision",
        "mean_abs_z",
        "max_abs_z",
        "mean_collision_energy_loss",
    ]
    summary = {"num_runs": len(results)}
    for metric_name in metric_names:
        metric_values = [
            result[metric_name]
            for result in results
            if result[metric_name] is not None
        ]
        if not metric_values:
            summary[metric_name] = {"mean": None, "std": None}
            continue
        summary[metric_name] = {
            "mean": float(np.mean(metric_values)),
            "std": float(np.std(metric_values)),
        }
    return summary
