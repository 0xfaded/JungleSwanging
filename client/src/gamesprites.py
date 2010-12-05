# vim:set sw=2 ts=2 sts=2 et:

import spritesheet

class GameSprites(spritesheet.SpriteSheet):
  def __init__(self):
    super(GameSprites, self).__init__((1024,1024))
    self.add_sprite('monkey', 'monkey.svg', (0, 0), (160, 160))

    self.set_texture()


# Singleton
GameSprites = GameSprites()

