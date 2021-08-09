"""This is a monster defender game."""

import pygame
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

def main():
  """Program main function."""
  pygame.init()

  display_size = (1200, 800)
  display = pygame.display.set_mode(display_size)
  pygame.display.set_caption('Monster Defender')

  # Set program icon
  icon = pygame.image.load('image/FOOCHIR.jpeg').convert_alpha()
  pygame.display.set_icon(icon)

  bg_image = pygame.image.load('image/background/bg_lawn.jpg')
  bg_image = pygame.transform.scale(bg_image, display_size)
  all_sprites = pygame.sprite.Group()
  cmd_sprites = pygame.sprite.Group()
  mc = MainCharacter(display_size,all_sprites)
  all_sprites.add(mc)
  cmd_sprites.add(mc)
  

  clock = pygame.time.Clock()
  while process_events(cmd_sprites):
    # display.fill((0, 0, 255))
    display.blit(bg_image, (0, 0))
    all_sprites.update()
    all_sprites.draw(display)

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()


if __name__ == '__main__':
  main()
