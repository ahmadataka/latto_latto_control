%matplotlib
import gym
import math
from latto_latto_model import LattoLatto
from stable_baselines3 import PPO

env = LattoLatto()
observation = env.reset()

model = PPO.load("ppo_latto", env=env)
print(observation)
for i in range(0,500):
    # action = env.action_space.sample()
    action, _state = model.predict(observation[0], deterministic=True)
    observation, reward, terminated, _ = env.step(action)
    env.render()
    if terminated:
        print('done')
        observation = env.reset()
env.close()