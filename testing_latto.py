%matplotlib
import gym
import math
from latto_latto_model import LattoLatto
from stable_baselines3 import PPO
import matplotlib.pyplot as plt

env = LattoLatto()
observation = env.reset()

model = PPO.load("ppo_latto", env=env)
print(observation)
action_array = []
time_array = []
times = 0
for i in range(0,100):
    # action = env.action_space.sample()
    action, _state = model.predict(observation[0], deterministic=True)
    observation, reward, terminated, _ = env.step(action)
    env.render()
    action_array.append(action)
    time_array.append(times)
    times = times + env.delta_t
    if terminated:
        print('done')
        observation = env.reset()
env.close()
fig1, ax1 = plt.subplots()
ax1.plot(time_array, action_array, '-r')
ax1.set_xlabel("time")
ax1.set_ylabel("acceleration")
fig1.savefig('acceleration.png')