import numpy as np
from OpenGL.GLU import *
from OpenGL.GL import *
import pygame
class Particle:
    def __init__(self, position, speed = np.array([5.,0.]), acc = np.array([0.,0.]),  color = (0,200,255), size = 8, heat_factor = 0.04, mass = 1, trace = False, ghost = False):
        self.position = np.array(position)
        self.speed = np.array(speed)
        self.acc = acc
        self.color = color
        self.size = size
        self.mass = mass
        self.trace = trace
        self.ghost = ghost
        

        self.heat_factor = heat_factor
        self.trace = [np.copy(position)]
        self.max_trail_length = 200

    def draw(self):
        glColor3fv(self.color)
        glPushMatrix()
        glTranslatef(*self.position, 0)
        quad = gluNewQuadric()
        gluDisk(quad, 0, self.size/2, 32, 1)
        glPopMatrix()

    def draw_trace(self):
        if len(self.trace) < 2:
            return

        # Normalize color to [0,1] if necessary
        r, g, b = self.color
        factor = 1.75
        r, g, b = r*factor, g*factor, b*factor
        if max(r, g, b) > 1.0:
            r, g, b = r / 255.0, g / 255.0, b / 255.0

        # Get window/world size (your ortho matches window size)
        surf = pygame.display.get_surface()
        W, H = (surf.get_size() if surf else (None, None))
        # If we know the size, use half-width/half-height as a wrap threshold
        # (any bigger jump than that is almost certainly a wrap)
        thr_x = W * 0.5 if W else float("inf")
        thr_y = H * 0.5 if H else float("inf")

        glColor3f(r, g, b)
        glLineWidth(3.0)

        # Draw multiple strips, restarting when a wrap-jump is detected
        glBegin(GL_LINE_STRIP)
        prev = self.trace[0]
        glVertex2f(*prev)
        for pos in self.trace[1:]:
            dx = abs(pos[0] - prev[0])
            dy = abs(pos[1] - prev[1])
            if dx > thr_x or dy > thr_y:
                glEnd()
                glBegin(GL_LINE_STRIP)  # start a new segment after wrap
                glVertex2f(*pos)
            else:
                glVertex2f(*pos)
            prev = pos
        glEnd()



    def step(self, dt):
        friction = True
        self.speed = self.speed + self.acc*dt

        if friction:
            v = np.linalg.norm(self.speed)
            term = dt*1/20000*self.speed*v if v > 300 else 0
            self.speed -= term
        if self.heat_factor > 0 and self.heat_factor is not None:
            self.speed += self.heat_factor*np.random.randn(2)
            
        
        self.position += self.speed*dt
    
        if self.trace:
            if self.color != (0,0,0):
                self.trace.append(np.copy(self.position))
            if len(self.trace) > self.max_trail_length:
                self.trace.pop(0)