import pygame
import random
import os

pygame.init()
pygame.mixer.init()
WIDTH = 1280
HEIGHT = 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My first game")

BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

clock = pygame.time.Clock()

music_path = os.path.join(BASE_DIR, "spaceinvaders1.mpeg")

try:
    pygame.mixer.music.load(music_path)
    
    pygame.mixer.music.set_volume(0.3) 
    
    pygame.mixer.music.play(-1)
    
except pygame.error:
    print("Could not load music.")

def load_image(file_name, width, height):
    full_path = os.path.join(BASE_DIR, file_name)

    try:
        image = pygame.image.load(full_path).convert_alpha()
        image = pygame.transform.scale(image, (width, height))

        return image
    except FileNotFoundError:
        print(f"ERROR: Could not find {file_name}.")
        return None

def load_sound(name):
    path = os.path.join(BASE_DIR, name)
    try:
        return pygame.mixer.Sound(path)
    except FileNotFoundError:
        return None

class Player:
    def __init__(self):
        center_x = WIDTH // 2
        center_y = HEIGHT // 2
        self.speed = 10
        self.width = 50
        self.height = 50
        self.hp = 3
        self.image = load_image("ship.png", self.width, self.height)

        self.rect = pygame.Rect(center_x, center_y, self.width, self.height)
    
    def move(self, keys):
        current_speed = self.speed

        if keys[pygame.K_LCTRL]:
            current_speed //= 2
        
        elif keys[pygame.K_LSHIFT]:
            current_speed *= 2
        
        if (self.rect.x - current_speed) > 0:
            if keys[pygame.K_a]:
                self.rect.x -= current_speed
        
        if (self.rect.x + current_speed + self.width) <= WIDTH:
            if keys[pygame.K_d]:
                self.rect.x += current_speed

        if (self.rect.y - current_speed) > 0:
            if keys[pygame.K_w]:
                self.rect.y -= current_speed
        
        if (self.rect.y + current_speed + self.height) <= HEIGHT:
            if keys[pygame.K_s]:
                self.rect.y += current_speed


    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, BLUE, self.rect)

class Enemy:
    def __init__(self):
        self.size = random.randint(20, 50)
        self.speed = random.randint(5, 10)
        random_x = random.randint(0, WIDTH - self.size)

        self.image = load_image("enemy.png", self.size, self.size)
        self.rect = pygame.Rect(random_x, -self.size, self.size, self.size)
    
    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.width = 5
        self.height = 20
        self.speed = 15

        self.image = load_image("bullet.png", self.width, self.height)
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self):
        self.rect.y -= self.speed
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, WHITE, self.rect)

player = Player()
enemies = []
bullets = []
current_time = 0

last_shot_time = 0
shoot_delay = 150

player_death_sound = load_sound("explosion.wav")
shoot_sound = load_sound("shoot.wav")
enemy_death_sound = load_sound("enemykilled.wav")

enemy_spawn_delay = 1000
enemy_last_spawn = 0
running = True
game_over = False

game_over_font = pygame.font.SysFont("Arial", 72, True)
font = pygame.font.SysFont("Arial", 32, True)
score = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not game_over:
        player.move(keys)

        current_time = pygame.time.get_ticks()

        if keys[pygame.K_x]:
            if current_time - last_shot_time > shoot_delay:
                bullets.append(Bullet(player.rect.centerx, player.rect.top))
                last_shot_time = current_time
                if shoot_sound: shoot_sound.play()

        if current_time - enemy_last_spawn > enemy_spawn_delay:
            enemies.append(Enemy())
            enemy_last_spawn = current_time

        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.y < 0:
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.update()
            if enemy.rect.y > HEIGHT:
                score -= 1
                enemies.remove(enemy)

        for enemy in enemies[:]:
            for bullet in bullets[:]:
                if enemy.rect.colliderect(bullet.rect):

                    try:
                        enemies.remove(enemy)
                        if enemy_death_sound: enemy_death_sound.play()
                        bullets.remove(bullet)
                        score += 1
                    except ValueError:
                        pass
                    break

        for enemy in enemies[:]:
            if player.rect.colliderect(enemy):
                player.hp -= 1
                enemies.remove(enemy)

                if player.hp <= 0:
                    if player_death_sound: player_death_sound.play()
                    game_over = True
                    pygame.mixer.music.stop()
    else:
        if keys[pygame.K_r]:
            enemies = []
            bullets = []
            player = Player()
            score = 0
            game_over = False
            pygame.mixer.music.play(-1)
        
        elif keys[pygame.K_q]:
            break

    screen.fill(BLACK)

    if not game_over:
        player.draw(screen)

        for bullet in bullets:
            bullet.draw(screen)

        for enemy in enemies:
            enemy.draw(screen)

        hp_text = font.render(f"HP: {player.hp}", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(hp_text, (10, 50))
        screen.blit(score_text, (10, 10))

    else:
        game_over_text = game_over_font.render("Game Over", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        quit_text = font.render("Press Q to Quit.", True, WHITE)

        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
        screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 60))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()