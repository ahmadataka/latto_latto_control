import gym

from stable_baselines3 import PPO

from latto_latto_model import LattoLatto

env = LattoLatto()
model_path = "ppo_latto_z_penalty"

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500000)
model.save(model_path)
print("Done")
