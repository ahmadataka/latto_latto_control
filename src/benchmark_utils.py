import json
import math
import random
from pathlib import Path

import numpy as np
from stable_baselines3 import A2C, PPO, SAC


RL_ALGORITHM_MAP = {
    "a2c": A2C,
    "ppo": PPO,
    "sac": SAC,
}

HEURISTIC_CONTROLLER_NAMES = {
    "zero",
    "random",
    "sinusoidal",
    "pumping",
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


def build_run_name(controller_name, reward_variant, restitution, seed, extras=None):
    parts = [
        controller_name.lower(),
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


def is_rl_algorithm(controller_name):
    return controller_name.lower() in RL_ALGORITHM_MAP


def is_heuristic_controller(controller_name):
    return controller_name.lower() in HEURISTIC_CONTROLLER_NAMES


class HeuristicController:
    def __init__(self, env, seed=0):
        self.env = env
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def learn(self, total_timesteps):
        return self

    def save(self, path):
        payload = {
            "controller_type": self.__class__.__name__,
            "seed": self.seed,
        }
        Path(f"{path}.json").write_text(json.dumps(payload, indent=2))


class ZeroController(HeuristicController):
    def predict(self, observation, deterministic=True):
        return np.array([0.0], dtype=np.float32), None


class RandomController(HeuristicController):
    def predict(self, observation, deterministic=True):
        action = self.rng.uniform(
            low=-self.env.max_action,
            high=self.env.max_action,
        )
        return np.array([action], dtype=np.float32), None


class SinusoidalController(HeuristicController):
    def __init__(self, env, seed=0, amplitude=7.5, frequency_hz=1.2, phase=0.0):
        super().__init__(env=env, seed=seed)
        self.amplitude = amplitude
        self.frequency_hz = frequency_hz
        self.phase = phase
        self.step_index = 0

    def predict(self, observation, deterministic=True):
        time_now = self.step_index * self.env.delta_t
        action = self.amplitude * math.sin(
            2.0 * math.pi * self.frequency_hz * time_now + self.phase
        )
        self.step_index += 1
        return np.array([action], dtype=np.float32), None

    def save(self, path):
        payload = {
            "controller_type": self.__class__.__name__,
            "seed": self.seed,
            "amplitude": self.amplitude,
            "frequency_hz": self.frequency_hz,
            "phase": self.phase,
        }
        Path(f"{path}.json").write_text(json.dumps(payload, indent=2))


class PumpingController(HeuristicController):
    def __init__(
        self,
        env,
        seed=0,
        gain=6.0,
        theta_center=math.pi / 2.0,
        theta_deadband=0.08,
        damping_gain=1.5,
    ):
        super().__init__(env=env, seed=seed)
        self.gain = gain
        self.theta_center = theta_center
        self.theta_deadband = theta_deadband
        self.damping_gain = damping_gain

    def predict(self, observation, deterministic=True):
        z, z_dot, theta, theta_dot = observation
        centered_theta = theta - self.theta_center

        # Pump energy away from the middle crossing, then damp near the apex.
        if abs(centered_theta) < self.theta_deadband:
            command = self.damping_gain * theta_dot
        else:
            command = self.gain * np.sign(centered_theta * theta_dot)

        action = float(np.clip(command, -self.env.max_action, self.env.max_action))
        return np.array([action], dtype=np.float32), None

    def save(self, path):
        payload = {
            "controller_type": self.__class__.__name__,
            "seed": self.seed,
            "gain": self.gain,
            "theta_center": self.theta_center,
            "theta_deadband": self.theta_deadband,
            "damping_gain": self.damping_gain,
        }
        Path(f"{path}.json").write_text(json.dumps(payload, indent=2))


def build_controller(controller_name, env, seed, verbose=1, controller_kwargs=None):
    controller_kwargs = controller_kwargs or {}
    name = controller_name.lower()
    if name in RL_ALGORITHM_MAP:
        model_class = RL_ALGORITHM_MAP[name]
        return model_class("MlpPolicy", env, verbose=verbose, seed=seed)
    if name == "zero":
        return ZeroController(env=env, seed=seed)
    if name == "random":
        return RandomController(env=env, seed=seed)
    if name == "sinusoidal":
        return SinusoidalController(env=env, seed=seed, **controller_kwargs)
    if name == "pumping":
        return PumpingController(env=env, seed=seed, **controller_kwargs)
    raise ValueError(f"Unsupported controller_name: {controller_name}")


def build_model(algorithm, env, seed, verbose=1):
    return build_controller(
        controller_name=algorithm,
        env=env,
        seed=seed,
        verbose=verbose,
    )


def train_controller(controller, total_timesteps):
    controller.learn(total_timesteps=total_timesteps)
    return controller


def evaluate_controller(controller, env, rollout_steps, deterministic=True, render=False):
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
        action, _state = controller.predict(observation[0], deterministic=deterministic)
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


def evaluate_model(model, env, rollout_steps, deterministic=True, render=False):
    return evaluate_controller(
        controller=model,
        env=env,
        rollout_steps=rollout_steps,
        deterministic=deterministic,
        render=render,
    )


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
