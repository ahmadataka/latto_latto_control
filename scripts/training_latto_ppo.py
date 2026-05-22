from pathlib import Path
import sys
from stable_baselines3 import PPO

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from latto_latto_model import LattoLatto

env = LattoLatto()
model_path = ROOT / "models" / "baselines" / "ppo_latto_z_penalty"

model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=500000)
model.save(str(model_path))
print("Done")
