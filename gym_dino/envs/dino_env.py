import os
import pygame
import random
import numpy as np

import gym
from gym import spaces
from gym.utils import seeding

# If you have a local sprite_path function, adjust imports accordingly.
# from .sprites.sprite_path import sprite_path
def sprite_path(name):
    """
    Replace this stub with your actual path resolver.
    E.g.: return os.path.join(os.path.dirname(__file__), 'sprites', name)
    """
    return name

pygame.init()

scr_size = (width, height) = (600, 150)
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (235, 235, 235)

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")

def load_image(name, sizex=-1, sizey=-1, colorkey=None):
    # Hardcoded path for sprites
    base_path = '/content/gym-dino/gym_dino/envs/sprites'
    fullname = os.path.join(base_path, name)
    print(f"Trying to load image: {fullname}")  # Debug the file path
    if not os.path.exists(fullname):
        raise FileNotFoundError(f"Sprite file not found: {fullname}")

    image = pygame.image.load(fullname)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pygame.RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return image, image.get_rect()


def load_sprite_sheet(sheetname, nx, ny, scalex=-1, scaley=-1, colorkey=None):
    # Hardcoded path for sprites
    base_path = '/content/gym-dino/gym_dino/envs/sprites'
    fullname = os.path.join(base_path, sheetname)
    print(f"Trying to load sprite sheet: {fullname}")  # Debug the file path
    if not os.path.exists(fullname):
        raise FileNotFoundError(f"Sprite file not found: {fullname}")

    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()
    sheet_rect = sheet.get_rect()

    sprites = []
    sizex = sheet_rect.width / nx
    sizey = sheet_rect.height / ny

    for i in range(ny):
        for j in range(nx):
            rect = pygame.Rect((j * sizex, i * sizey, sizex, sizey))
            image = pygame.Surface(rect.size)
            image = image.convert()
            image.blit(sheet, (0, 0), rect)

            if colorkey is not None:
                if colorkey == -1:
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey, pygame.RLEACCEL)

            if scalex != -1 or scaley != -1:
                image = pygame.transform.scale(image, (scalex, scaley))

            sprites.append(image)

    sprite_rect = sprites[0].get_rect()
    return sprites, sprite_rect


def extractDigits(number):
    """ Utility to extract individual scoreboard digits from an integer. """
    if number > -1:
        digits = []
        while number // 10 != 0:
            digits.append(number % 10)
            number = number // 10
        digits.append(number % 10)
        while len(digits) < 5:
            digits.append(0)
        digits.reverse()
        return digits
    return [0, 0, 0, 0, 0]


class Dino:
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('dino.png', 5, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sprite_sheet('dino_ducking.png', 2, 1, 59, sizey, -1)
        self.rect.bottom = int(0.98 * height)
        self.rect.left = width / 15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isBlinking = False
        self.movement = [0, 0]
        self.jumpSpeed = 11.5

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    def draw(self):
        screen.blit(self.image, self.rect)

    def checkbounds(self):
        if self.rect.bottom > int(0.98 * height):
            self.rect.bottom = int(0.98 * height)
            self.isJumping = False

    def update(self):
        if self.isJumping:
            self.movement[1] += gravity

        if self.isJumping:
            self.index = 0
        elif self.isBlinking:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1) % 2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1) % 2
        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2
        else:
            if self.counter % 5 == 0:
                self.index = (self.index + 1) % 2 + 2

        if self.isDead:
            self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index % 2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        if not self.isDead and (self.counter % 7 == 6) and (not self.isBlinking):
            self.score += 1

        self.counter += 1


class Cactus(pygame.sprite.Sprite):
    containers = None  # Initialize containers attribute

    def __init__(self, speed=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('cacti-small.png', 3, 1, sizex, sizey, -1)
        self.rect.bottom = int(0.98 * height)
        self.rect.left = width + self.rect.width
        self.image = self.images[random.randrange(0, 3)]
        self.movement = [-speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Ptera(pygame.sprite.Sprite):
    containers = None  # Initialize containers attribute

    def __init__(self, speed=5, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images, self.rect = load_sprite_sheet('ptera.png', 2, 1, sizex, sizey, -1)
        self.ptera_height = [height * 0.82, height * 0.75, height * 0.60]
        self.rect.centery = random.choice(self.ptera_height)
        self.rect.left = width + self.rect.width
        self.image = self.images[0]
        self.movement = [-speed, 0]
        self.index = 0
        self.counter = 0

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index + 1) % 2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter += 1
        if self.rect.right < 0:
            self.kill()


class Ground:
    def __init__(self, speed=-5):
        self.image, self.rect = load_image('ground.png', -1, -1, -1)
        self.image1, self.rect1 = load_image('ground.png', -1, -1, -1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = speed

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed
        if self.rect.right < 0:
            self.rect.left = self.rect1.right
        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


class Cloud(pygame.sprite.Sprite):
    containers = None  # Initialize containers attribute

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image, self.rect = load_image('cloud.png', int(90*30/42), 30, -1)
        self.speed = 1
        self.rect.left = x
        self.rect.top = y
        self.movement = [-self.speed, 0]

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()


class Scoreboard:
    def __init__(self, x=-1, y=-1):
        self.score = 0
        self.tempimages, self.temprect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11*6/5), -1)
        self.image = pygame.Surface((55, int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = width * 0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = height * 0.1
        else:
            self.rect.top = y

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self, score):
        score_digits = extractDigits(score)
        self.image.fill(background_col)
        x_offset = 0
        for s in score_digits:
            self.image.blit(self.tempimages[s], (x_offset, 0))
            x_offset += self.temprect.width


class DinoEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(DinoEnv, self).__init__()
        # ----- Define Gym spaces properly -----
        self.action_space = spaces.Discrete(3)  
        # We use (150, 600, 3) because pygame.surfarray.array3d() returns RGB channels
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(150, 600, 3), dtype=np.uint8
        )

        self.gamespeed = 4
        self.gameOver = False
        self.playerDino = Dino(44, 47)
        self.new_ground = Ground(-1 * self.gamespeed)
        self.scb = Scoreboard()
        self.counter = 0
        self.done = False
        self.FPS = 60

        # Sprite groups
        self.cacti = pygame.sprite.Group()
        self.pteras = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.last_obstacle = pygame.sprite.Group()

        # Link containers
        Cactus.containers = self.cacti
        Ptera.containers = self.pteras
        Cloud.containers = self.clouds

        self.temp_images, self.temp_rect = load_sprite_sheet(
            'numbers.png', 12, 1, 11, int(11*6/5), -1
        )

        # This just creates "HI" scoreboard – not critical for RL
        HI_image = pygame.Surface((22, int(11*6/5)))
        HI_rect = HI_image.get_rect()
        HI_image.fill(background_col)
        HI_rect.top = height * 0.1
        HI_rect.left = width * 0.73

    def step(self, action):
        # If the game is not over, process the action
        if not self.gameOver:
            if pygame.display.get_surface() is None:
                print("Couldn't load display surface")
                self.gameOver = True
            else:
                # Actions: 0 = no-op, 1 = duck, 2 = jump
                if action == 1:  # duck
                    if not self.playerDino.isJumping and not self.playerDino.isDead:
                        self.playerDino.isDucking = True
                else:
                    # if action != 1 -> un-duck
                    self.playerDino.isDucking = False
                    if action == 2:  # jump
                        if self.playerDino.rect.bottom == int(0.98*height):
                            self.playerDino.isJumping = True
                            self.playerDino.movement[1] = -self.playerDino.jumpSpeed

            # Update obstacles movement and collision
            for c in self.cacti:
                c.movement[0] = -self.gamespeed
                if pygame.sprite.collide_mask(self.playerDino, c):
                    self.playerDino.isDead = True

            for p in self.pteras:
                p.movement[0] = -self.gamespeed
                if pygame.sprite.collide_mask(self.playerDino, p):
                    self.playerDino.isDead = True

            # Spawn obstacles
            if len(self.cacti) < 2:
                if len(self.cacti) == 0:
                    self.last_obstacle.empty()
                    self.last_obstacle.add(Cactus(self.gamespeed, 40, 40))
                else:
                    for l in self.last_obstacle:
                        if l.rect.right < width * 0.7 and random.randrange(0, 50) == 10:
                            self.last_obstacle.empty()
                            self.last_obstacle.add(Cactus(self.gamespeed, 40, 40))

            if len(self.pteras) == 0 and random.randrange(0, 200) == 10 and self.counter > 500:
                for l in self.last_obstacle:
                    if l.rect.right < width * 0.8:
                        self.last_obstacle.empty()
                        self.last_obstacle.add(Ptera(self.gamespeed, 46, 40))

            # Spawn clouds
            if len(self.clouds) < 5 and random.randrange(0, 300) == 10:
                y_pos = random.randrange(height // 5, height // 2)
                Cloud(width, y_pos)

            # Update game objects
            self.playerDino.update()
            self.cacti.update()
            self.pteras.update()
            self.clouds.update()
            self.new_ground.update()
            self.scb.update(self.playerDino.score)

            # Draw if display is available
            if pygame.display.get_surface() is not None:
                screen.fill(background_col)
                self.new_ground.draw()
                self.clouds.draw(screen)
                self.scb.draw()
                self.cacti.draw(screen)
                self.pteras.draw(screen)
                self.playerDino.draw()

            clock.tick(self.FPS)

            # Capture observation from screen (shape: [width, height, 3])
            # By default, it's [600, 150, 3], so we transpose to [150, 600, 3]
            screen_array = pygame.surfarray.array3d(pygame.display.get_surface())
            screen_array = np.transpose(screen_array, (1, 0, 2))
            self.obs = screen_array

            if self.playerDino.isDead:
                self.gameOver = True

            # Increase difficulty over time
            if self.counter % 700 == 699:
                self.new_ground.speed -= 1
                self.gamespeed += 1

            self.counter += 1

        if self.gameOver:
            self.done = True

        reward = self.playerDino.score
        info = {}
        return self.obs, reward, self.done, info

    def reset(self, seed=None, return_info=False, options=None):
        # Initialize pygame display if not already initialized
        if not pygame.display.get_init():
            pygame.display.init()

        # Set up a display surface if not already created
        if not pygame.display.get_surface():
            pygame.display.set_mode((600, 150))  # Use the appropriate size

        # Reset the environment state
        self.gamespeed = 4
        self.gameOver = False
        self.playerDino = Dino(44, 47)
        self.new_ground = Ground(-1 * self.gamespeed)
        self.scb = Scoreboard()
        self.counter = 0
        self.done = False

        # Fill the display surface
        screen.fill(background_col)
        pygame.display.flip()

        # Return the initial observation
        observation = pygame.surfarray.array3d(pygame.display.get_surface())
        observation = np.transpose(observation, (1, 0, 2))  # Ensure consistency with step
        return observation

    def render(self, mode='human'):
        # If you want a human-visible mode, just flip the display
        if mode == 'human':
            pygame.display.update()

    def close(self):
        pygame.quit()
