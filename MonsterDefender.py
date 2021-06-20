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


def main():
  """Program main function."""
  pygame.init()

  display_width = 1200
  display_height = 800

  display = pygame.display.set_mode((display_width, display_height))
  display.fill((0, 0, 255))
  pygame.display.set_caption('Monster Defender')

  # Set program icon
  icon = pygame.image.load('main.png').convert_alpha()
  pygame.display.set_icon(icon)

  pygame.display.flip()
  while not is_quitting():
    time.sleep(0.5)

  pygame.quit()


if __name__ == '__main__':
  main()