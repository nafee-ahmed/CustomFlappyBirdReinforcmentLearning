from stable_baselines3 import PPO
import os
from flappy_bird_env import FlappyBirdEnv

models_dir = "models/PPO_FLAPPY"
log_dir = "logs"
TIMESTEPS = 10_000

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

env = FlappyBirdEnv()
env.reset()

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)

for i in range(1,100_000):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO_FLAPPY")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

env.close()
