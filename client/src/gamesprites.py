# vim:set sw=2 ts=2 sts=2 et:

import spritesheet

class GameSprites(spritesheet.SpriteSheet):
  def __init__(self):
    super(GameSprites, self).__init__((1000,1000))
    self.add_sprite('monkey', 'wiki.svg', (100, 100), (100, 100))

    self.set_texture()


# Singleton
GameSprites = GameSprites()

