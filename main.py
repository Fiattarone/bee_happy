import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 640
HEIGHT = 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the clock
clock = pygame.time.Clock()

# Define the colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
YELLOW_OFF = (200, 200, 0)
SKY_BLUE = (135, 206, 250)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (0, 0, 0)


class Bee(pygame.sprite.Sprite):
    def __init__(self, color=YELLOW, speed=5):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((32, 12),  pygame.SRCALPHA)
        self.image.fill(self.color)

        # Draw the bee's body
        pygame.draw.rect(self.image, BLACK, (7, 0, 6, 12))
        pygame.draw.rect(self.image, BLACK, (19, 0, 6, 12))

        # Set the bee's initial position and speed
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = speed

        # Set bee's stats
        self.energy = 5
        self.health = 5
        self.happy = 5

    def wrap_around_screen(self):
        # Wrap the bee around if it goes off-screen
        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif self.rect.top > HEIGHT:
            self.rect.bottom = 0

    def check_size_increase(self):
        # If bee is over 50 happy, double its size
        if self.happy > 50:
            self.image = pygame.transform.scale(self.image, (48, 18))
            self.rect = self.image.get_rect(center=self.rect.center)

        # If bee is over 200 happy, triple its size
        if self.happy > 200:
            self.image = pygame.transform.scale(self.image, (64, 24))
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        # Handle input and update bee position
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Wrap the bee around if it goes off-screen
        self.wrap_around_screen()

        # Check size
        self.check_size_increase()




class NPCBee(Bee):
    def __init__(self):
        super().__init__(color=YELLOW_OFF)
        self.move_timer = 0
        self.move_duration = 0
        self.move_direction = None
        self.pause_timer = 0
        self.pause_duration = random.randint(1000, 5000)

    def start_new_move(self):
        self.move_duration = random.randint(1000, 5000)
        self.move_timer = 0
        self.move_direction = random.randint(0, 359)

    def update(self):
        if self.pause_timer >= self.pause_duration:
            if self.move_timer < self.move_duration:
                dx = math.cos(math.radians(self.move_direction)) * 5
                dy = math.sin(math.radians(self.move_direction)) * 5
                self.rect.x += dx
                self.rect.y += dy
                self.move_timer += clock.get_time()
            else:
                self.pause_timer = 0
                self.pause_duration = random.randint(250, 1250)
                self.start_new_move()
        else:
            self.pause_timer += clock.get_time()

        super().wrap_around_screen()
        super().check_size_increase()

# why is the mouse never detected as hovering over the beeui?
class BeeUI(pygame.sprite.Sprite):
    def __init__(self, bee):
        super().__init__()
        self.bee = bee
        self.image = pygame.Surface((64, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=bee.rect.center)
        self.stats_visible = False
        self.alpha = 230  # Set initial transparency to 90%

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Check if mouse is hovering over the BeeUI
            if self.rect.collidepoint(event.pos):
                self.stats_visible = True
            else:
                self.stats_visible = False

    def update(self):
        # Sync with Bee
        self.rect.center = self.bee.rect.center

        # Draw the stats display
        stats_surface = pygame.Surface((64, 12), pygame.SRCALPHA)

        # Create a transparent surface for the text
        text_surface = pygame.Surface((64, 12), pygame.SRCALPHA)

        # Create a font object with size 24
        font = pygame.font.Font(None, 24)

        # Display the health, energy, and speed on the stats surface
        health_text = font.render(str(self.bee.health), True, RED)
        energy_text = font.render(str(self.bee.energy), True, BLUE)
        speed_text = font.render(str(self.bee.happy), True, GREEN)

        # make the stats surface 90% transparent unless mouse is hovering over
        alpha = 230 if self.stats_visible else 23

        # Set the alpha value of the text surface
        text_surface.set_alpha(alpha)

        # Fill the text surface with a transparent background
        text_surface.fill((255, 255, 255, 0))

        # Blit the text on the stats surface
        text_surface.blit(health_text, (16, 0))
        text_surface.blit(energy_text, (28, 0))
        text_surface.blit(speed_text, (40, 0))

        self.image.fill((255, 255, 255, 0))

        # Blit the transparent surface onto the stats surface
        stats_surface.blit(text_surface, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

        # Draw the stats surface above the bee's image
        self.image.blit(stats_surface, (0, 0))


class Game:
    def __init__(self):
        self.player_group = pygame.sprite.GroupSingle()
        self.player = Bee()
        self.player_group.add(self.player)
        self.worker_group = pygame.sprite.Group()
        self.bee_ui_group = pygame.sprite.Group()
        bee_ui = BeeUI(self.player)
        self.bee_ui_group.add(bee_ui)
        self.npc_timer = 0
        self.show_alert = False

    def spawn_worker(self):
        worker = NPCBee()
        worker.rect.x = random.randrange(WIDTH - worker.rect.width)
        worker.rect.y = random.randrange(HEIGHT - worker.rect.height)
        self.worker_group.add(worker)
        bee_ui = BeeUI(worker)
        self.bee_ui_group.add(bee_ui)

    def run(self):
        while True:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEMOTION:
                    for beeui in self.bee_ui_group:
                        beeui.handle_event(event)

            # Update game state
            self.player_group.update()
            self.worker_group.update()
            self.bee_ui_group.update()

            # Spawn worker bees every 5 seconds
            self.npc_timer += clock.get_time()
            if self.npc_timer >= 5000:
                self.npc_timer = 0
                self.spawn_worker()

            # Check for collisions between player and worker bees
            for worker in self.worker_group:
                if pygame.sprite.collide_rect(self.player, worker):
                    self.player.happy += 1
                    worker.happy += 1
                    self.show_alert = True
                else:
                    self.show_alert = False



            # Clear the screen
            screen.fill(SKY_BLUE)

            # Draw sprites
            self.worker_group.draw(screen)
            self.player_group.draw(screen)
            self.bee_ui_group.draw(screen)

            # Draw alert icon
            if self.show_alert:
                pygame.draw.rect(screen, GREEN, (WIDTH-64, 0, 64, 64))
            else:
                pygame.draw.rect(screen, RED, (WIDTH-64, 0, 64, 64))

            # Update the display
            pygame.display.update()

            # Limit the framerate
            clock.tick(60)


if __name__ == '__main__':
    game = Game()
    game.run()


