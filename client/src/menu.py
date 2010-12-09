from OpenGL.GL import *
from OpenGL.GLU import *


from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import pygame
from pygame.locals import *

import sys

pygame.mixer.init()
select_sound = pygame.mixer.Sound('select.wav')
accept_sound = pygame.mixer.Sound('accept.wav')
cancel_sound = pygame.mixer.Sound('cancel.wav')

menu_music = pygame.mixer.Sound('jungle.ogg')


def load_image(image):
    textureSurface = pygame.image.load(image)

    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

    width = textureSurface.get_width()
    height = textureSurface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    return texture, width, height

class Main_Menu(object):


    mm = True

    main_points = [(-1.4, 1.3), (-1.4, -1.3), (1.4, -1.3), (1.4, 1.3)]
    selection =  [(-.7, 1.3), (-.7, -1.3), (2.1, -1.3), (2.1, 1.3)]
    back_tex = []
    buttons_tex = []
    cursor_tex = []

    #selection = [(leftmost + gap, boxbottom - selection_gap - selection_height), (leftmost + gap, boxbottom - selection_gap), (leftmost + gap + boxlength, boxbottom - selection_gap), (leftmost + gap + boxlength, boxbottom - selection_gap - selection_height)]

    def __init__(self):
        self.init_gl()

        self.host = 'localhost'
        self.host_port = 8007
        self.client_port = 9999

        if len(sys.argv) >= 2:
          self.host = sys.argv[1]
        if len(sys.argv) >= 3:
          self.host_port = int(sys.argv[2])
        if len(sys.argv) >= 4:
          self.client_port = int(sys.argv[3])
        menu_music.play(-1)


    def draw(self, i):
        #MUST MAKE ALL SHAPES COUNTER-CLOCKWISE
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


        glEnable(GL_TEXTURE_2D)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glBindTexture(GL_TEXTURE_2D, self.texture[0])


        if i == 1:
            glBegin(GL_QUADS)

            self.back_tex = [(.5, 1), (.5, .5), (1, .5), (1, 1)]
	    self.cursor_tex = [(0, 1), (0, .5), (.5, .5), (.5, 1)]

	    back_coords = zip(self.main_points, self.back_tex)
	    cursor_coords = zip(self.selection, self.cursor_tex)


            for ((px, py), (tx, ty)) in back_coords:
                glTexCoord2f(tx, ty)
                glVertex3f(px, py, 0)

	    """
            for ((px, py), (tx, ty)) in buttons_coords:
                glTexCoord2f(tx, ty)
                glVertex3f(px, py, 0)
            """

            for ((px, py), (tx, ty)) in cursor_coords:
                glTexCoord2f(tx, ty)
		glVertex3f(px, py, 0)


            glEnd()

        if i == 3:

            glBegin(GL_QUADS)

            self.back_tex = [(0, .5), (0, 0), (.5, 0), (.5, .5)]

            back_coords = zip(self.main_points, self.back_tex)

            for ((px, py), (tx, ty)) in back_coords:
                glTexCoord2f(tx, ty)
                glVertex3f(px, py, 0)

            glEnd()

        if i == 2:

            glBegin(GL_QUADS)
            self.back_tex = [(.5, .5), (.5, 0), (1, 0), (1, .5)]

            back_coords = zip(self.main_points, self.back_tex)

            for ((px, py), (tx, ty)) in back_coords:
                glTexCoord2f(tx, ty)
                glVertex3f(px, py, 0)

            glEnd()



    def selection_left(self, menu_item):
      select_sound.play()
      if menu_item == 1:
        self.selection = [(.55, 1.3), (.55, -1.3), (3.35, -1.3), (3.35, 1.3)]
      elif menu_item == 2:
        self.selection = [(-1.4, 1.3), (-1.4, -1.3), (1.4, -1.3), (1.4, 1.3)]
      elif menu_item == 3:
        self.selection = [(-.7, 1.3), (-.7, -1.3), (2.1, -1.3), (2.1, 1.3)]

    def selection_right(self, menu_item):
      select_sound.play()
      if menu_item == 1:
        self.selection = [(-.7, 1.3), (-.7, -1.3), (2.1, -1.3), (2.1, 1.3)]
      elif menu_item == 2:
        self.selection = [(.55, 1.3), (.55, -1.3), (3.35, -1.3), (3.35, 1.3)]
      elif menu_item == 3:
        self.selection = [(-1.4, 1.3), (-1.4, -1.3), (1.4, -1.3), (1.4, 1.3)]


    def init_gl(self):
        # Initialise Display and GL
        SCREEN_SIZE = (800, 600)

        pygame.init()
        screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF)

        glViewport(0, 0, SCREEN_SIZE[0], SCREEN_SIZE[1])

        # GL's COORDINATE SYSTEM FOR RENDERING:
        # (camera view):
        #
        # ^ +z      positive z is away from us (zero at top of screen)
        # |
        # o--> +x   x increases left to right
        # |
        # v +y      positive y is down
        #
        # (side view):
        # o_  <--- camera
        #  \
        #    o--> +z
        #    |
        #    v +y

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        ratio = float(SCREEN_SIZE[0]) / SCREEN_SIZE[1]
        glOrtho(-ratio, ratio, -1, 1, 1000, -1000)

        glMatrixMode(GL_MODELVIEW)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL) # hmm

        # discard any fragments with alpha <= 0
        glEnable(GL_ALPHA_TEST)
        glAlphaFunc(GL_GREATER, 0)

        # set background and alpha blending
        glClearColor(0, 0, 0, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def main(self):
        self.texture = load_image('b.png')

        fps = 30
        clock = pygame.time.Clock()
        menu_item = 2
        max_menu_items = 3
        menu_page = 1


        while 1:
            deltat = clock.tick(fps)

            if self.mm:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == K_RETURN or event.unicode == 'a':
                            if menu_item == 2:
                                pygame.mixer.stop()
                                accept_sound.play()
                                client = Client(self.host, self.host_port,
                                                self.client_port)
                                client.run()
                            elif menu_item == 1:
                                menu_page = 2
                                self.mm = False

                            else:
                                menu_page = 3
                                self.mm = False

                        if event.key == K_LEFT:
                            self.selection_left(menu_item)
                            menu_item = menu_item - 1
                            if menu_item < 1:
                                menu_item = max_menu_items

                        if event.key == K_RIGHT:
                            self.selection_right(menu_item)
                            menu_item = menu_item + 1
                            if menu_item > max_menu_items:
                                menu_item = 1

                        if event.unicode == 'q':
                            cancel_sound.play()
                            sys.exit(0)
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit(0)
                    elif event.type == pygame.KEYDOWN:
                        if event.key == 13:
                            self.mm = True
                            menu_item = 2
			    self.selection = [(-.7, 1.3), (-.7, -1.3), (2.1, -1.3), (2.1, 1.3)]
                            menu_page = 1


            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.draw(menu_page)

            pygame.display.flip()

    pygame.quit()


class ClientProtocol(DatagramProtocol):

  def __init__(self, game_world):
    self.game_world = game_world
    self.our_monkey = None

  def datagramReceived(self, data, address):

    import monkey

    msg = data.strip().split(',')
    msg.reverse()

    client_id = int(msg.pop())

    self.game_world.children = []
    self.game_world.tree_from_network(msg)

    monkeys = self.game_world.children_of_type(monkey.Monkey)
    for m in monkeys:
      if m.player_id == client_id:
        self.our_monkey = m
        break

class Client(object):
  def __init__(self, host, host_port, client_port):

    self.host = host
    self.host_port = host_port
    self.client_port = client_port

  def run(self):

    import objectfactory
    import objectid

    import keymap

    game_world = objectfactory.ObjectFactory.from_id(objectid.world_id)

    client_proto = ClientProtocol(game_world)

    reactor.listenUDP(self.client_port, client_proto)
    reactor.fireSystemEvent('startup')

    fps = 30
    clock = pygame.time.Clock()

    sequence_number = 0

    keys = keymap.KeyMap()
    active = True

    try:
      while active:
        delta_t = clock.tick(fps)

        msg = [sequence_number]
        sequence_number += 1

        keys.read_keys(pygame.key.get_pressed())
        keys.to_network(msg)

        msg = map(str, msg)
        msg = ','.join(msg)

        client_proto.transport.write(msg, (self.host, self.host_port))

        reactor.iterate(0)

        if client_proto.our_monkey == None:
          continue

        events = []
        for event in pygame.event.get():
          events.append(event)

          if event.type == pygame.QUIT:
            active = False
          elif event.type == pygame.KEYDOWN:
            if event.unicode == 'q':
              active = False

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        zoom = 0.1
        glScale(zoom, zoom, 1)

        # center camera on monkey
        mx, my = client_proto.our_monkey.body.position
        glTranslate(-mx, -my, 0)

        game_world.tree_render()

        pygame.display.flip()

    except Exception as e:
      print e

    reactor.fireSystemEvent('shutdown')



if __name__ == '__main__':
    main_menu = Main_Menu()
    main_menu.main()

