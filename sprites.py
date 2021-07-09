"""Game sprites"""

import collections
import enum
import random
from typing import Tuple
import pygame

import image_lib

ImageInfo = collections.namedtuple('ImageInfo', 'image direction')

class MovingSprite(pygame.sprite.Sprite):
  """A pygame sprite that can move."""

  def __init__(self, image: pygame.Surface,
               position: Tuple[int, int],
               size: Tuple[int, int]=None,
               velocity: pygame.Vector2=None,
               boundary: pygame.rect=None,
               kill_if_out_of_boundary: bool=False):
    """
    Args:
      image: pygame Sprite image, for example, photo loaded from a file.
      rect: Sprite rect.
      boundary: The boundary that this sprite must be in.
      position: (x, y) position of the sprite.
      velocity: Velocity of the sprite.
    """
    super().__init__()
    if size is None:
      size = image.get_size()
      self.image = image
    else:
      self.image = pygame.transform.scale(image, size)

    self.rect = pygame.Rect(position, size)
    self.velocity = velocity
    self.boundary = boundary
    self.kill_if_out_of_boundary = kill_if_out_of_boundary

  def update(self):
    """Update this sprite for this frame.0"""
    if self.velocity:
      self.rect.move_ip(self.velocity.x, self.velocity.y)
    if self.boundary:
      if self.kill_if_out_of_boundary:
        if not self.boundary.contains(self.rect):
          self.kill()
      else:
        self.rect.clamp_ip(self.boundary)

  def center(self):
    """Center of this sprite."""
    return self.rect.center


class DyingEffect(object):
  """Effects rigth before a sprite dies."""

  def __init__(self, animator, sound):
    self.animator = animator
    self.sound = sound

  @property
  def image(self):
    """Image of current dying stage."""
    return self.animator.image

  @property
  def rect(self):
    """Rect of the dying effect."""
    return self.animator.rect

  @property
  def is_dying(self):
    """Whether the sprite is dying."""
    return self.animator.is_active

  def die_at(self, rect):
    """Start to die."""
    self.animator.start()
    self.animator.rect = rect
    if self.sound:
      self.sound.play()

  def update(self):
    """Update dying stage."""
    self.animator.update()


class ShootgingStrategy(enum.Enum):
  """How to find shooting target."""
  NO_TARGET = 1
  CLOSEST_X = 2
  CLOSEST_Y = 3
  CLOSEST_DISTANCE = 4
  RANDOM = 5

class Bullet(MovingSprite):
  """A sprite that can kill other sprites."""

  def __init__(self,
               image_info: ImageInfo,
               position: Tuple[int, int],
               boundary: pygame.Rect,
               shooting_strategy: ShootgingStrategy,
               targets: pygame.sprite.Group,
               dying_animator_factory: image_lib.SequenceAnimatorFactory=None,
               dying_sound: pygame.mixer.Sound=None):
    """Creates a bullet instance.
    Args:
      image_info: Bullet image and image direction.
      position: Bullet initial position.
      boundary: Bullet boundary.
      shooting_strategy: How target is choosen.
      targets: All sprites that can be killed by this bullet.
      dying_animator_factory: Factory to create dying effect.
      dying_source: Sound to play when dies.
    """
    super().__init__(image_info.image, position, None, velocity=image_info.direction,
                     boundary=boundary, kill_if_out_of_boundary=True)
    self.image_info = image_info
    self.shooting_strategy = shooting_strategy
    self.target = pygame.sprite.GroupSingle()
    self.targets = targets
    if dying_animator_factory:
      dying_animator = dying_animator_factory.create(self)
    else:
      dying_animator = None
    if dying_animator or dying_sound:
      self.dying_effect = DyingEffect(dying_animator, dying_sound)
    else:
      self.dying_effect = None


  def update(self):
    """Update this bullet."""
    if self.dying_effect is not None and self.dying_effect.is_dying:
      self.dying_effect.update()
      self.image = self.dying_effect.image
      self.rect = self.dying_effect.rect
      return
    self._find_target()
    if self.target.sprite:
      # Change velocity toward the target
      target_center = self.target.sprite.center()
      bullet_center = self.center()
      direction = pygame.Vector2(target_center[0] - bullet_center[0],
                                 target_center[1] - bullet_center[1])
      self.change_to_direction(direction)
    super().update()

    if self.targets:
      hit_targets = pygame.sprite.spritecollide(self, self.targets, dokill=True)
      if not hit_targets:
        return
      if self.dying_effect is None:
        self.kill()
      else:
        self.velocity = pygame.Vector2(0, 0)
        self.dying_effect.die_at(hit_targets[0].rect)

  def change_to_direction(self, direction: pygame.Vector2):
    """Adjust the bullet torward the vector direction.
    Args:
      direction: The new direction.
    """

    if abs(self.velocity.angle_to(direction)) > 0.01:
      self.image = pygame.transform.rotate(self.image_info.image,
                                           direction.angle_to(self.image_info.direction))

    direction.scale_to_length(self.velocity.length())
    self.velocity = direction

  def _find_target(self):
    if self.target.sprite:
      return

    if (self.shooting_strategy == ShootgingStrategy.NO_TARGET or
        len(self.targets.sprites()) == 0):
      self.target = pygame.sprite.GroupSingle()
      return

    if self.shooting_strategy == ShootgingStrategy.CLOSEST_X:
      self.target = pygame.sprite.GroupSingle(
          min(self.targets.sprites(),
              key=lambda s: abs(s.rect.centerx - self.rect.centerx)))
    elif self.shooting_strategy == ShootgingStrategy.CLOSEST_Y:
      self.target = pygame.sprite.GroupSingle(
          min(self.targets.sprites(),
              key=lambda s: abs(s.rect.centery - self.rect.centery)))
    elif self.shooting_strategy == ShootgingStrategy.CLOSEST_DISTANCE:
      self.target = pygame.sprite.GroupSingle(
          min(self.targets.sprites(),
              key=lambda s: pygame.Vector2(s.rect.centerx - self.rect.centerx,
                                           s.rect.centery - self.rect.centery).length()))
      return


class ShootingCapability(object):
  """Describes the shooting capability of a sprite."""
  def __init__(self,
               bullet_image_info: ImageInfo,
               boundary: pygame.Rect,
               shooting_strategy: ShootgingStrategy,
               targets: pygame.sprite.Group,
               sprite_group: pygame.sprite.Group,
               dying_animator_factory: image_lib.SequenceAnimatorFactory,
               dying_sound: pygame.mixer.Sound):
    """Create shooting capability.
    Args:
      bullet_image_info: Bullet image info.
      boudary: Boundary of the bullet shoot by this capability.
      shooting_strategy: The strategy to find target.
      targets: All targets that can be killed by this capability.
      sprite_group: The sprite group that the bullets belongs to.
    """
    self.image_info = bullet_image_info
    self.boundary = boundary
    self.shooting_strategy = shooting_strategy
    self.targets = targets
    self.bullets = pygame.sprite.Group()
    self.sprite_group = sprite_group
    self.dying_animator_factory = dying_animator_factory
    self.dying_sound = dying_sound

  def create_bullet(self, position: Tuple[int, int],
                    direction: pygame.Vector2):
    """Shoot a bullet.
    Args:
      position: Bullet initial position.
      direction: Bullet direction.
    """
    if direction.x < 0:
      position = (position[0]-self.image_info.image.get_width(), position[1])
    bullet = Bullet(self.image_info, position, self.boundary,
                    self.shooting_strategy, self.targets,
                    self.dying_animator_factory, self.dying_sound)
    bullet.change_to_direction(direction)
    self.bullets.add(bullet)
    self.sprite_group.add(bullet)



class Ball(MovingSprite):
  """A ball object."""

  def __init__(self, image, boundary,
               position, radius, velocity, bouncy_rate=1.0, score=1):
    super().__init__(image, position, (radius*2, radius*2), velocity, boundary)
    self.bouncy_rate = bouncy_rate
    self.score = score

  def get_hit_norm(self, sprite):
    """Hit norm of the two balls."""
    return (pygame.math.Vector2(*sprite.center()) -
            pygame.math.Vector2(*self.rect.center))