# vim:set sw=2 ts=2 sts=2 et:

import pngspritesheet

class GameSprites(pngspritesheet.PNGSpriteSheet):
  def __init__(self):
    #super(GameSprites, self).__init__((1024,1024))
    super(GameSprites, self).__init__('gamesprites.png')
    self.add_sprite('monkey', 'monkey.svg', (0, 0), (200, 200))
    self.add_sprite('monkey_arm', 'monkey_arm.svg', (0, 200), (100, 20))
    self.add_sprite('beachball', 'beachball.svg', (0, 220), (100, 100))
    self.add_sprite('abomb', 'abomb.svg', (200, 0), (160, 200))

    self.set_texture()


# Singleton
GameSprites = GameSprites()

