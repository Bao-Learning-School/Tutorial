"""This is a monster defender game."""

import pygame
import time


def is_quitting():
  """Check if user hits the quit button"""
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      return True
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        return True
  return False


class Canon(pygame.sprite.Sprite):
  def __init__(self, screen_size):
    super().__init__()
    size = (100,100)
    image = pygame.image.load('cannon.png').convert_alpha()
    self.image = pygame.transform.scale(image, size)
    self.rect = pygame.Rect((0, screen_size[1] - size[1]), size)

def main():
  """Program main function."""
  pygame.init()

  display_size = (1200, 800)
  display = pygame.display.set_mode(display_size)
  display.fill((0, 0, 255))
  pygame.display.set_caption('Monster Defender')

  # Set program icon
  icon = pygame.image.load('main.png').convert_alpha()
  pygame.display.set_icon(icon)

  all_sprites = pygame.sprite.Group()
  all_sprites.add(Canon(display_size))
  clock = pygame.time.Clock()
  while not is_quitting():
    # Update()
    all_sprites.draw(display)

    pygame.display.flip()
    clock.tick(60)

  pygame.quit()


if __name__ == '__main__':
  main()
