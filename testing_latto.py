%matplotlib
import gym
import math
from latto_latto_model import LattoLatto

env = LattoLatto()
observation = env.reset()

for i in range(0,200):
    action = env.action_space.sample()
    print(env.observation_space.sample().shape)
    observation, reward, terminated, _ = env.step(action)
    # print("obs:", observation)
    # print("reward:", reward)
    env.render()
    if terminated:
        print('done')
        observation = env.reset()
env.close()