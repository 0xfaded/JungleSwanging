# vim:set sw=2 ts=2 sts=2 et:

import pngspritesheet

class GameSprites(pngspritesheet.PNGSpriteSheet):
  def __init__(self):
    #super(GameSprites, self).__init__((1024,1024))
    super(GameSprites, self).__init__('gamesprites.png')
    self.add_sprite('monkey', 'monkey.svg', (0, 0), (203, 204))
    self.add_sprite('monkey2', 'monkey2.svg', (210, 0), (203, 207))
    self.add_sprite('monkey_arm', 'monkey_arm.svg', (0, 214), (105, 22))
    self.add_sprite('beachball', 'beachball.svg', (0, 244), (104, 104))
    self.add_sprite('abomb', 'abomb.svg', (420, 0), (164, 205))
    self.add_sprite('pinapple', 'pinapple.svg', (0, 534), (91, 68))
    self.add_sprite('banana', 'banana.svg', (0, 354), (62, 34))
    self.add_sprite('orange', 'orange.svg', (0, 394), (61, 60))
    self.add_sprite('pinecone', 'pinapple.svg', (0, 454), (95, 73))
    self.add_sprite('burst', 'burst.svg', (0, 614), (112, 103))

    self.add_sprite('tent', 'tent.svg', (590,0), (401,402))

    self.set_texture()


# Singleton
GameSprites = GameSprites()

