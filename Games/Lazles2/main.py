import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# ZEGA Engineering Standards
APP_TITLE = "ZEGA - 3D STRYKER"
ZEGA_GREEN = (88, 240, 27) # #58f01b

class ZegaEngine:
    def __init__(self):
        pygame.init()
        self.display = (1000, 800)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption(APP_TITLE)
        
        # Enable 3D Depth so closer things hide farther things
        glEnable(GL_DEPTH_TEST) #
        
        # Set up Perspective (Field of View, Aspect Ratio, Near Clip, Far Clip)
        gluPerspective(45, (self.display[0]/self.display[1]), 0.1, 50.0) #
        
        self.player_pos = [0, 0, -5]
        self.angle_y = 0
        self.clock = pygame.time.Clock()

    def draw_floor(self):
        """Draws a perspective grid like in the original shader"""
        glBegin(GL_LINES)
        glColor3f(0.34, 0.94, 0.11) # ZEGA Green
        for i in range(-20, 21, 2):
            # Horizontal lines
            glVertex3f(i, -1, -20)
            glVertex3f(i, -1, 20)
            # Vertical lines
            glVertex3f(-20, -1, i)
            glVertex3f(20, -1, i)
        glEnd()

    def draw_player(self):
        """Draws a simple player cube at the center"""
        glPushMatrix()
        glTranslatef(0, -0.5, 0) # Sit on the floor
        # In a real ZEGA game, we'd load a 3D model here
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.1, 0.1) # Dark body
        for x, y, z in [(-0.2,0,0.2), (0.2,0,0.2), (0.2,0.5,0.2), (-0.2,0.5,0.2)]:
            glVertex3f(x, y, z)
        glEnd()
        glPopMatrix()

    def run(self):
        pygame.event.set_grab(True) # Lock mouse to screen
        pygame.mouse.set_visible(False)

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return

            # Handle Movement
            keys = pygame.key.get_pressed()
            if keys[K_w]: self.player_pos[2] += 0.1
            if keys[K_s]: self.player_pos[2] -= 0.1
            if keys[K_a]: self.player_pos[0] += 0.1
            if keys[K_d]: self.player_pos[0] -= 0.1
            
            # Handle Mouse Look
            rel_x, _ = pygame.mouse.get_rel()
            self.angle_y += rel_x * 0.2

            # Render Scene
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # Camera Math: Follow player from behind
            cam_x = self.player_pos[0] + 5 * math.sin(math.radians(self.angle_y))
            cam_z = self.player_pos[2] - 5 * math.cos(math.radians(self.angle_y))
            
            # View Matrix: Eye Position, Looking At, Up Vector
            gluLookAt(cam_x, 2, cam_z, self.player_pos[0], 0, self.player_pos[2], 0, 1, 0) #

            self.draw_floor()
            self.draw_player()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    app = ZegaEngine()
    app.run()