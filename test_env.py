from stable_baselines3.common.env_checker import check_env
from flappy_bird_env import FlappyBirdEnv

env = FlappyBirdEnv()
check_env(env)
print("check_env: okay")

env = FlappyBirdEnv()
episodes = 1000

for ep in range(episodes):
    terminated = False
    obs, _ = env.reset()

    while not terminated:
        random_action = env.action_space.sample()
        print("action: ", random_action)
        obs, reward, terminated, truncated, info = env.step(random_action)
        print("reward: ", reward)
