import numpy as np
from OpenGL.GLU import *
from OpenGL.GL import *
import pygame


class Particle:
    def __init__(self, position, speed = np.array([5.,0.]), acc = np.array([0.,0.]),  color = (0,0,0), size = 8, heat_factor = 0.04, mass = 1, trace = False, ghost = False, field = np.array([0.,0.]), charge = 0.0, friction = None):
        self.position = np.array(position)
        self.speed = np.array(speed)
        self.acc = acc
        self.size = size
        self.mass = mass
        self.trace = trace
        self.ghost = ghost
        self.field = field
        self.friction = friction
        self.charge = charge

        if color == (0,0,0):
            norm_charge = np.tanh(charge / 20)
            if norm_charge >= 0:
                self.color = (1.0, 1.0 - norm_charge, 1.0 - norm_charge)  # white→red
            else:
                self.color = (1.0 + norm_charge, 1.0 + norm_charge, 1.0)  # white→blue
        else:
            self.color = color
        
        

        self.heat_factor = heat_factor
        self.trace = [np.copy(position)]
        self.max_trail_length = 250

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
    
        self.acc += self.field
        #self.speed = self.speed + self.acc*dt

        #Runge-Kutta 4th Order Integration could go here
        k1 = dt*self.acc
        k2 = dt*(self.acc + 0.5*k1)
        k3 = dt*(self.acc + 0.5*k2)
        k4 = dt*(self.acc + k3)
        self.speed += (k1 + 2*k2 + 2*k3 + k4)/6



        if self.friction is not None:
            v = np.linalg.norm(self.speed)
            term = self.friction*dt*1/20000*self.speed*v if v > 200 else 0
            self.speed -= term
        if self.heat_factor > 0 and self.heat_factor is not None:
            self.speed += self.heat_factor*np.random.randn(2)
            
        
        #self.position += self.speed*dt

        #Runge-Kutta 4th Order Integration could go here
        k1 = dt*self.speed
        k2 = dt*(self.speed + 0.5*k1)
        k3 = dt*(self.speed + 0.5*k2)
        k4 = dt*(self.speed + k3)
        self.position += (k1 + 2*k2 + 2*k3 + k4)/6

        if self.trace:
            if self.color != (0,0,0):
                self.trace.append(np.copy(self.position))
            if len(self.trace) > self.max_trail_length:
                self.trace.pop(0)