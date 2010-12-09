from OpenGL.GL import *
from OpenGL.GLU import *

import pygame
from pygame.locals import *



import sys

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

    def draw(self, i):
        #MUST MAKE ALL SHAPES COUNTER-CLOCKWISE
        
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
        if menu_item == 1:
            self.selection = [(.55, 1.3), (.55, -1.3), (3.35, -1.3), (3.35, 1.3)]
        elif menu_item == 2:
            self.selection = [(-1.4, 1.3), (-1.4, -1.3), (1.4, -1.3), (1.4, 1.3)]
	elif menu_item == 3:
	    self.selection = [(-.7, 1.3), (-.7, -1.3), (2.1, -1.3), (2.1, 1.3)]
            
    def selection_right(self, menu_item):
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
                                """
                                
                                INSERT START GAME HERE
                                
                                """
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


if __name__ == '__main__':
    main_menu = Main_Menu()
    main_menu.main()

