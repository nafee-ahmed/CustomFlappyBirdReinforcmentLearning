from stable_baselines3 import PPO
import os
from flappy_bird_env import FlappyBirdEnv

models_dir = "models/PPO_FLAPPY"
log_dir = "logs"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

env = FlappyBirdEnv()
env.reset()

model_path = f"{models_dir}/190000"
model = PPO.load(model_path, env=env)

episodes = 10
for ep in range(episodes):
    obs, info = env.reset()
    terminated = False
    while not terminated:
        action, _ = model.predict(obs)
        obs, reward, terminated, truncated, info = env.step(action)

env.close()
