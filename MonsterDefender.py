"""This is a monster defender game."""

import pygame
import time


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
  def __init__(self, screen_size):
    super().__init__()
    size = (100,100)
    image = pygame.image.load('cannon.png').convert_alpha()
    self.image = pygame.transform.scale(image, size)
    self.rect = pygame.Rect((0, screen_size[1] - size[1]), size)

  def update(self):
    speed = 5
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_LEFT]:
      self.rect = self.rect.move(-speed, 0)
    elif keys_pressed[pygame.K_RIGHT]:
      self.rect = self.rect.move(speed, 0)

def main():
  """Program main function."""
  pygame.init()

  display_size = (1200, 800)
  display = pygame.display.set_mode(display_size)
  pygame.display.set_caption('Monster Defender')

  # Set program icon
  icon = pygame.image.load('FOOCHIR.jpeg').convert_alpha()
  pygame.display.set_icon(icon)

  all_sprites = pygame.sprite.Group()
  cmd_sprites = pygame.sprite.Group()
  all_sprites.add(Cannon(display_size))
  

  clock = pygame.time.Clock()
  while process_events(cmd_sprites):
    display.fill((0, 0, 255))
    all_sprites.update()
    all_sprites.draw(display)

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()


if __name__ == '__main__':
  main()
