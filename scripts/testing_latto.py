from pathlib import Path
import sys
import argparse

import matplotlib.pyplot as plt
from stable_baselines3 import PPO

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from latto_latto_model import LattoLatto

DEFAULT_MODEL_PATH = ROOT / "models" / "baselines" / "ppo_latto_z_penalty"
ACTION_PLOT_PATH = ROOT / "results" / "testing" / "testing_action_trace.png"
POSE_PLOT_PATH = ROOT / "results" / "testing" / "testing_pose_trace.png"

backend = plt.get_backend().lower()
interactive_backend = backend not in {"agg", "pdf", "ps", "svg", "template"}
if interactive_backend:
    plt.ion()


parser = argparse.ArgumentParser()
parser.add_argument(
    "model_path",
    nargs="?",
    default=str(DEFAULT_MODEL_PATH),
    help="Path to a PPO checkpoint without or with the .zip suffix.",
)
args = parser.parse_args()

env = LattoLatto()
observation = env.reset()

model = PPO.load(args.model_path, env=env)
print(observation)
action_array = []
time_array = []
pivot_z_array = []
theta_array = []
times = 0
for i in range(0,100):
    # action = env.action_space.sample()
    action, _state = model.predict(observation[0], deterministic=True)
    observation, reward, terminated, _ = env.step(action)
    env.render()
    action_array.append(float(action[0]))
    time_array.append(times)
    pivot_z_array.append(float(env.state[0]))
    theta_array.append(float(env.state[2]))
    times = times + env.delta_t
    if terminated:
        print('done')
        observation = env.reset()
fig1, ax1 = plt.subplots()
ax1.plot(time_array, action_array, '-r')
ax1.set_xlabel("time")
ax1.set_ylabel("acceleration")
fig1.tight_layout()
fig1.savefig(ACTION_PLOT_PATH)

fig2, (ax2, ax3) = plt.subplots(2, 1, sharex=True)
ax2.plot(time_array, pivot_z_array, '-b')
ax2.set_ylabel("pivot z")
ax2.set_title("Latto-Latto Pose")
ax3.plot(time_array, theta_array, '-g')
ax3.set_xlabel("time")
ax3.set_ylabel("theta")
fig2.tight_layout()
fig2.savefig(POSE_PLOT_PATH)
if interactive_backend:
    plt.ioff()
    plt.show()
env.close()
