import pygame
import sys
import random

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

# Pygame window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Font for score and game over text
font = pygame.font.Font(None, 55)
small_font = pygame.font.Font(None, 35)

# Create bird and pipes
bird = Bird()
pipes = []

# Game variables
score = 0
game_over = False

# Clock setup
clock = pygame.time.Clock()

# Function to reset the game
def reset_game():
    global bird, pipes, score, game_over
    bird = Bird()
    pipes = []
    score = 0
    game_over = False

# Function to display text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    bird.jump()
                else:
                    # If the game is over, spacebar restarts it
                    reset_game()

    # --- Game Logic (only runs if game is not over) ---
    if not game_over:
        # Update bird
        bird.update()

        # Generate pipes
        if len(pipes) == 0 or pipes[-1].x < WIDTH - 250:
            pipes.append(Pipe())

        # Update pipes and check for score
        for pipe in pipes:
            pipe.update()
            # Check if the bird has passed the pipe
            if not pipe.passed and pipe.x < bird.x:
                score += 1
                pipe.passed = True

        # Check collisions
        for pipe in pipes:
            if bird.rect.colliderect(pipe.rect_top) or bird.rect.colliderect(pipe.rect_bottom):
                game_over = True

        # Check for collision with top/bottom of the screen
        if bird.y < 0 or bird.y > HEIGHT - BIRD_HEIGHT:
            game_over = True

        # Remove off-screen pipes
        pipes = [pipe for pipe in pipes if pipe.x + PIPE_WIDTH > 0]

    # --- Drawing ---
    screen.fill(BLACK)

    # Draw bird
    pygame.draw.rect(screen, GREEN, bird.rect)

    # Draw pipes
    for pipe in pipes:
        pygame.draw.rect(screen, WHITE, pipe.rect_top)
        pygame.draw.rect(screen, WHITE, pipe.rect_bottom)

    # Draw score
    draw_text(str(score), font, WHITE, screen, WIDTH // 2, 50)

    # --- Game Over Screen ---
    if game_over:
        draw_text("Game Over", font, WHITE, screen, WIDTH // 2, HEIGHT // 2 - 50)
        draw_text(f"Score: {score}", font, WHITE, screen, WIDTH // 2, HEIGHT // 2)
        draw_text("Press SPACE to restart", small_font, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 50)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(30)

# Quit Pygame and exit
pygame.quit()
sys.exit()
