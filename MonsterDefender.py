"""This is a monster defender game."""

import pygame
import time

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


class Cannon(pygame.sprite.Sprite):
  def __init__(self, screen_size, all_sprites):
    super().__init__()
    size = (100,100)
    image = pygame.image.load('image/cannon.png').convert_alpha()
    self.image = pygame.transform.scale(image, size)
    self.rect = pygame.Rect((screen_size[0] // 2,
                             screen_size[1] - size[1] - 20), size)
    self.boundary = pygame.Rect((0, 0), screen_size)
    self.all_sprites = all_sprites

  def update(self):
    speed = 5
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_LEFT]:
      self.rect = self.rect.move(-speed, 0)
    elif keys_pressed[pygame.K_RIGHT]:
      self.rect = self.rect.move(speed, 0)
    if keys_pressed[pygame.K_SPACE]:
      image_info = sprites.ImageInfo(
          image=pygame.image.load('image/bullet32x32.ico'),
          direction=pygame.Vector2(-10, 0))  
      position = (self.rect.centerx, self.rect.top)
      bullet = sprites.Bullet(image_info, position,
          self.boundary,
          sprites.ShootgingStrategy.NO_TARGET, None)
      self.all_sprites.add(bullet)
      

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
  all_sprites.add(Cannon(display_size,all_sprites))
  

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
