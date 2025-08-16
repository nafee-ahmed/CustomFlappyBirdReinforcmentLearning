import pygame
import sys
import random
from gymnasium import spaces
import gymnasium as gym
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
BIRD_WIDTH, BIRD_HEIGHT = 40, 40
PIPE_WIDTH, PIPE_HEIGHT = 50, 300
GAP_SIZE = 150
GRAVITY = 1
JUMP_VELOCITY = -15
PIPE_SPEED = 5
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Bird class
class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT)

    def jump(self):
        self.velocity = JUMP_VELOCITY

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = self.y

# Pipe class
class Pipe:
    def __init__(self):
        self.x = WIDTH
        # Ensure the gap is not too close to the top or bottom
        self.gap_start = random.randint(50, HEIGHT - GAP_SIZE - 50)
        self.rect_top = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_start)
        self.rect_bottom = pygame.Rect(self.x, self.gap_start + GAP_SIZE, PIPE_WIDTH, HEIGHT - self.gap_start - GAP_SIZE)
        self.passed = False # To track if the bird has passed this pipe for scoring

    def update(self):
        self.x -= PIPE_SPEED
        self.rect_top.x = self.x
        self.rect_bottom.x = self.x

def agent_observations(bird, pipes):
    bird_x = bird.x
    # bird_x_end = bird.x + BIRD_WIDTH
    bird_y = bird.y
    # bird_y_end = bird.y + BIRD_HEIGHT
    bird_velocity = bird.velocity

    # find the next pipe ahead of the bird
    next_pipe = None
    for pipe in pipes:
        if pipe.x + PIPE_WIDTH > bird.x:
            next_pipe = pipe
            break

    if next_pipe:
        # horizontal distance to the pipe
        pipe_x = next_pipe.x - bird.x
        pipe_gap_start = next_pipe.gap_start
        pipe_gap_end = next_pipe.gap_start + GAP_SIZE
    else:
        pipe_x = WIDTH  # Distance to next pipe (far right)
        pipe_gap_start = HEIGHT // 2 - GAP_SIZE // 2  # Center gap
        pipe_gap_end = HEIGHT // 2 + GAP_SIZE // 2

    return [
        bird_x / WIDTH, # normalize for better learning
        bird_y / HEIGHT,
        bird_velocity / 20.0,
        pipe_x / WIDTH,
        pipe_gap_start / HEIGHT,
        pipe_gap_end / HEIGHT,
    ]


class FlappyBirdEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": FPS}
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(2) # 0 = NO_JUMP, 1 = JUMP
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -1, 0, 0, 0], dtype=np.float32),  # All normalized
            high=np.array([1, 1, 1, 1, 1, 1], dtype=np.float32),   # All normalized
            shape=(6,),
            dtype=np.float32
        )

        # Pygame window setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")

        # Font for score and game over text
        self.font = pygame.font.Font(None, 55)
        self.small_font = pygame.font.Font(None, 35)

        # Create bird and pipes
        self.bird = Bird()
        self.pipes = []

        # Game variables
        self.score = 0
        self.game_over = False

        # Clock setup
        self.clock = pygame.time.Clock()

    # Function to reset the game
    def reset(self, seed=1142, options=None):
        super().reset(seed=seed)
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.observation = agent_observations(self.bird, self.pipes)
        self.observation = np.array(self.observation, dtype=np.float32)

        return self.observation, {}

    # Function to display text
    def draw_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.center = (x, y)
        surface.blit(textobj, textrect)

    def render(self):
                # # --- Drawing ---
        self.screen.fill(BLACK)

        # Draw bird
        pygame.draw.rect(self.screen, GREEN, self.bird.rect)

        # Draw pipes
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, WHITE, pipe.rect_top)
            pygame.draw.rect(self.screen, WHITE, pipe.rect_bottom)

        # Draw score
        self.draw_text(str(self.score), self.font, WHITE, self.screen, WIDTH // 2, 50)

        # --- Game Over Screen ---
        if self.game_over:
            self.draw_text("Game Over", self.font, WHITE, self.screen, WIDTH // 2, HEIGHT // 2 - 50)
            self.draw_text(f"Score: {self.score}", self.font, WHITE, self.screen, WIDTH // 2, HEIGHT // 2)
            self.draw_text("Press SPACE to restart", self.small_font, WHITE, self.screen, WIDTH // 2, HEIGHT // 2 + 50)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        # Control the frame rate
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        pygame.quit()
        sys.exit()

    def step(self, action):
        if action == 1:
            if not self.game_over:
                self.bird.jump()
            else:
                # If the game is over, spacebar restarts it
                self.reset()

        # --- Game Logic (only runs if game is not over) ---
        if not self.game_over:
            # Update bird
            self.bird.update()

            # Generate pipes
            if len(self.pipes) == 0 or self.pipes[-1].x < WIDTH - 250:
                self.pipes.append(Pipe())

            reward = 0.01 # small reward for surviving each frame
            # Update pipes and check for score
            for pipe in self.pipes:
                pipe.update()
                # Check if the bird has passed the pipe
                if not pipe.passed and pipe.x < self.bird.x:
                    self.score += 1
                    pipe.passed = True
                    reward += 1

            # Check collisions
            for pipe in self.pipes:
                if self.bird.rect.colliderect(pipe.rect_top) or self.bird.rect.colliderect(pipe.rect_bottom):
                    self.game_over = True
                    reward = -5  # Penalty for dying

            # Check for collision with top/bottom of the screen
            if self.bird.y < 0 or self.bird.y > HEIGHT - BIRD_HEIGHT:
                self.game_over = True
                reward = -5

            # Remove off-screen pipes
            self.pipes = [pipe for pipe in self.pipes if pipe.x + PIPE_WIDTH > 0]


        self.observation = agent_observations(self.bird, self.pipes)
        self.observation = np.array(self.observation, dtype=np.float32)

        info = {}
        self.render()
        return self.observation, reward, self.game_over, False, info


