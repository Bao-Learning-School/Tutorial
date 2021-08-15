"""This is a monster defender game."""

import pygame
import random
import time

from pygame import image

import image_lib
import sprites


def process_events(cmd_spites):
  """Check if user hits the quit button"""
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      return False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        return False
    for sprite in cmd_spites:
      sprite.process_event(event)
  return True

class MainCharacter(pygame.sprite.Sprite):
  def __init__(self, screen_size, all_sprites):
    super().__init__()
    size = (100,100)
    images = image_lib.images_from_file('image/SsmWh_4x9.png')
    self.left_image_sequence = images[9:18]
    self.right_image_sequence = images[27:]
    self.image_index = 0
    self.default_image = images[1]
    self.image = self.default_image
    self.ipu = 2
    self.rect = pygame.Rect((screen_size[0] // 2,
                             screen_size[1] - size[1] - 20), size)
    self.boundary = pygame.Rect((0, 0), screen_size)
    self.all_sprites = all_sprites

  def update(self):
    speed = 5
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_LEFT]:
      self.rect = self.rect.move(-speed, 0)
      self.image_index += 1
      self.image_index %= len(self.left_image_sequence) * self.ipu
      self.image = self.left_image_sequence[self.image_index // self.ipu]
    elif keys_pressed[pygame.K_RIGHT]:
      self.rect = self.rect.move(speed, 0)
      self.image_index += 1
      self.image_index %= len(self.right_image_sequence) * self.ipu
      self.image = self.right_image_sequence[self.image_index // self.ipu]
    else:
      self.image = self.default_image
      self.image_index = 0
  
  def shoot(self):
    image = pygame.image.load('image/bullet64x64.ico')
    image = pygame.transform.scale(image, (32, 32))
    image_info = sprites.ImageInfo(
        image=image,
        direction=pygame.Vector2(-10, 0))  
    position = (self.rect.left + image_info.image.get_width() // 2,
                self.rect.top)
    bullet = sprites.Bullet(image_info, position,
        self.boundary,
        sprites.ShootgingStrategy.NO_TARGET, None)
    bullet.change_to_direction(pygame.Vector2(0, -10))
    self.all_sprites.add(bullet)
      
  def process_event(self, event):
    # Should not call pygame.event.get() here because it empties
    # the event queue so others won't get their events.
    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
      self.shoot()


class MainBoard():
  def __init__(self):
    pygame.display.set_caption('Monster Defender')
    self.display_size = (1200, 800)
    self.display = pygame.display.set_mode(self.display_size)

    # Set program icon
    icon = pygame.image.load('image/FOOCHIR.jpeg').convert_alpha()
    pygame.display.set_icon(icon)

    bg_image = pygame.image.load('image/background/bg_lawn.jpg')
    self.bg_image = pygame.transform.scale(bg_image, self.display_size)
    self.all_sprites = pygame.sprite.Group()
    self.cmd_sprites = pygame.sprite.Group()
    self.targets = pygame.sprite.Group()
    self.mc = MainCharacter(self.display_size, self.all_sprites)
    self.all_sprites.add(self.mc)
    self.cmd_sprites.add(self.mc)

  def create_targets(self):
    if random.randint(0, 70) != 0:
      return
    margin = 10
    image = pygame.image.load('image/targets/nectarine.png').convert_alpha()
    x_pos = random.randint(margin, self.display_size[0] - margin)
    y_pos = margin
    velocity = pygame.Vector2(0, random.randint(1, 5))
    target = sprites.Target(image, pygame.Rect((0, 0), self.display_size),
                            (x_pos, y_pos), (50, 50), velocity)
    self.targets.add(target)
    self.all_sprites.add(target)

  def update(self):
    if not process_events(self.cmd_sprites):
      return False
    self.create_targets()
    self.display.blit(self.bg_image, (0, 0))
    self.all_sprites.update()
    self.all_sprites.draw(self.display)

    pygame.display.flip()
    return True


def main():
  """Program main function."""
  pygame.init()

  board = MainBoard()
  clock = pygame.time.Clock()
  while board.update():
    clock.tick(60)

  pygame.quit()


if __name__ == '__main__':
  main()
 