"""Manages pygame images"""

import collections
import os
from typing import List, Optional, Tuple
import pygame

ImageInfo = collections.namedtuple('ImageInfo', 'image direction')

class Animator(object):
  """Animates a sequence of images."""

  def __init__(self, owner: Optional[pygame.sprite.Sprite]=None):
    """Creates an image animator.
    Args:
      owner: Owner of this animator class.
    """
    self._owner = pygame.sprite.GroupSingle(owner)
    self._rect = None

  @property
  def owner(self):
    """Owner of this animator."""
    return self._owner.sprite

  @property
  def image(self) -> pygame.Surface:
    """Image of current state."""
    raise NotImplementedError('Derived class should override this property')

  @property
  def rect(self) -> Optional[pygame.Rect]:
    """Rect of this animator."""
    return self._rect

  @property
  def size(self) -> Optional[Tuple[int, int]]:
    """Size of current image."""
    if self.image is None:
      return None
    return self.image.get_size()

  @property
  def is_active(self) -> bool:
    """Whether the animator is active."""
    return self.image is not None


class FilesAnimator(object):
  """Animator for a sequence of image files."""

  def __init__(self,
               image_files: List[str],
               size: Optional[Tuple[int, int]],
               display_time: int,
               transition_time: int,
               loops: Optional[int]):
    """Create an image sequence animator.
    Args:
      image_files: List of image files to be animated.
      size: Image size.
      display_time: How long (in frames, and include transition time) an image
          should be displayed.
      transition_time: How long is the image transition time.
      interval: Intervals (frames) between two images.
      loops: Number of loops of the images. None: no loop, -1: infinite loops.
    """
    self._image_files = image_files
    self._image=None
    self._next_image = None
    self._size = size
    self._display_time = display_time
    self._index = None
    self._transition_time = transition_time
    self._transition_index = None
    self._loops = loops

  @property
  def image(self):
    """Current image of this animator."""
    return self._image
    '''
    # Need to figure a way to blend two images.
    if self._next_image is None:
      return self._image
    # Merge two images
    alpha2 = self._transition_index / self._transition_time
    alpha1 = 1.0 - alpha2
    image = self._image.convert()
    image.set_alpha(alpha1)
    self._next_image.set_alpha(alpha2)
    image.blit(self._next_image, (0, 0))
    image.set_alpha(1.0)
    return image
    '''

  def blit(self, surface, position):
    """Blit image into the surface."""
    if self._next_image is None:
      surface.blit(self._image, position)
      return

    # Merge two images
    alpha2 = self._transition_index / self._transition_time
    alpha1 = 1.0 - alpha2
    self._image.set_alpha(alpha1)
    self._next_image.set_alpha(alpha2)
    surface.blit(self._image, position)
    surface.blit(self._next_image, position)

  def start(self):
    """Starts the animation."""
    self._image = scale_image(pygame.image.load(self._image_files[0]),
                              self._size)
    self._size = self._image.get_size()
    self._index = 0

  def update(self):
    """Update the animator."""
    self._index += 1
    if self._index % self._display_time == 0:
      # Transition begins
      image_index = self._index // self._display_time % len(self._image_files)
      self._next_image = scale_image(
          pygame.image.load(self._image_files[image_index]), self._size)
      self._transition_index = 0
      return

    if self._transition_index is None:
      return

    self._transition_index += 1
    if self._transition_index >= self._transition_time:
      # Transition done
      self._image = self._next_image
      self._next_image = None
      self._transition_index = None



class SequenceAnimator(Animator):
  """Animator for a sequence of images."""

  def __init__(self,
               owner: Optional[pygame.sprite.Sprite],
               image_iterator: collections.abc.Iterator,
               interval: int):
    """Create an image sequence animator.
    Args:
      owner: Owner of this animator class.
      image_iterator: Iterator of the images to be animated.
      interval: Intervals (frames) between two frames.
    """
    super().__init__(owner)
    self._images_iterator = image_iterator
    self._index = None
    self._image = None
    self._interval = interval
    self._rect = None
    self.shift_up_factor = 0.2

  @property
  def image(self):
    """Current image."""
    return self._image

  @property
  def is_active(self):
    """Whether the sprite is dying."""
    return self._image is not None

  @property
  def rect(self):
    return self._rect

  @rect.setter
  def rect(self, rect):
    if not self._image:
      return
    self._rect = self._image.get_rect()
    self._rect.center = (
        rect.centerx,
        rect.centery + rect.height // 2 - self._rect.height * (1 - self.shift_up_factor) // 2)

  def start(self):
    """Starts the animation."""
    self._index = -1  # The update function below will increment the index.
    self.update()

  def update(self):
    """Update dying stage."""
    if self._index is None:
      return
    self._index += 1
    self._index %= self._interval
    if self._index != 0:
      return
    self._image = next(self._images_iterator, None)
    if self._image is None:
      self.owner.kill()


class SequenceAnimatorFactory(object):

  """Factory class that create SequenceAnimator."""

  def __init__(self,
               images: List[pygame.Surface],
               interval: int):
    """Create a sequence animator factory.
    Args:
      images: List of images for SequenceAnimator.
      interval: Interval between neighboring images.
    """
    self._images = images
    self._interval = interval

  def create(self, owner: Optional[pygame.sprite.Sprite]=None):
    """Creates a SequenceAnimator."""
    return SequenceAnimator(owner, iter(self._images), self._interval)


def split_image(image: pygame.Surface,
                y_pieces: int,
                x_pieces: int,
                target_size: Optional[Tuple[int, int]]=None) -> List[pygame.Surface]:
  """Split an image evenly into pieces.
  Args:
    image: The original image.
    x_pieces: Number of pieces horizontally.
    y_pieces: Number of pieces vertically.
    target_size: Output sub-image size.
  Returns:
    A list of sub-images.
  """
  piece_width = image.get_width() // x_pieces
  piece_height = image.get_height() // y_pieces
  images = []
  for x in range(x_pieces):
    for y in range(y_pieces):
      rect = pygame.Rect(y * piece_width, x * piece_height, piece_width, piece_height)
      surface = pygame.Surface((piece_width, piece_height), pygame.SRCALPHA, 32)
      surface.blit(image, (0,0), rect)
      if target_size is not None:
        surface = pygame.transform.scale(surface, target_size)
      images.append(surface)
  return images


def scale_image(image: pygame.Surface,
                size: Tuple[Optional[int], Optional[int]]) -> pygame.Surface:
  """Scale an image.
  If one of the size dimension is None, scale proportionally.
  Args:
    image: The original image.
    size: Target size.
  """
  x_size, y_size = size
  if x_size is None and y_size is None:
    return image
  if x_size is None:
    x_size = image.get_width() * y_size // image.get_height()
  elif y_size is None:
    y_size = image.get_height() * x_size // image.get_width()

  return pygame.transform.scale(image, (x_size, y_size))


def sequence_animator_factory_from_file(
    image_path: str,
    grid_size: Optional[Tuple[int, int]],
    size: Tuple[int, int],
    interval: int) -> SequenceAnimatorFactory:
  """Create an sequence image animator from a file.
  Args:
      owner: Owner of this animator class.
      grid_size: Number of rows/columns of sub-images.
      size: Size of each sub-image.
      interval: Intervals (frames) between two frames.
  """
  if grid_size is None:
    # Infer grid size from file name
    file_name_pieces = os.path.splitext(image_path)[0].rsplit('_', 1)
    if len(file_name_pieces) == 2:
      grid_size = file_name_pieces[1].split('x')
      if len(grid_size) == 2:
        row = int(grid_size[0])
        col = int(grid_size[1])
  images = split_image(pygame.image.load(image_path), row, col, size)
  return SequenceAnimatorFactory(images, interval)