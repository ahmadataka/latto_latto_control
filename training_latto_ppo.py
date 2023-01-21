import gym

from stable_baselines3 import PPO

from latto_latto_model import LattoLatto

env = LattoLatto()

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=250000)
model.save("ppo_latto")
print("Done")