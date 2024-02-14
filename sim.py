import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from limit import limits
import numpy as np
import lj_interaction as lj
class Particle:
    def __init__(self, position, speed = np.array([5.,0.]), acc = np.array([0.,-1.]),  color = (0,200,255), size = 5):
        self.position = np.array(position)
        self.speed = np.array(speed)
        self.acc = acc
        self.color = color
        self.size = size
        self.talk = False
        self.bin = 25

    def draw(self):
        glColor3fv(self.color)
        glPointSize(self.size)
        glBegin(GL_POINTS)
        glVertex2f(*self.position)
        glEnd()

    def step(self, dt):
        #réévalue les positons et vitesses
        if self.talk:
            print(f" pos : {self.position}, speed : {self.speed}, acc : {self.acc}")

        self.speed = self.speed*(1-dt/100) + self.acc*dt
        self.position += self.speed*dt

class simulation():
    def __init__(self) -> None:

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL) 
        self.clock = pygame.time.Clock()
        self.dt = 0.03
        self.border = limits(800, 600, self.dt)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.particles = []
        self.collision = lj.lj_repulsion()
        self.generate_particles(600)

        self.mainloop()

    def generate_particles(self, n_particles, random = True, x_max = 800, y_max = 600):

        if random:
            x_range = [np.random.random()*x_max for i in range(n_particles)]
            y_range = [np.random.random()*y_max for i in range(n_particles)]

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))), size = 8))
        else:
            base_x = 200.
            final_x = 600.
            base_y = 200.
            final_y = 400.
            x_range = np.linspace(base_x,final_x,n_particles)
            y_range = np.linspace(base_y,final_y,n_particles)

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))), size = 25))

            



    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            self.collision.repulse(all_particles = self.particles)
            for particle in self.particles:
                particle.step(dt = self.dt)
                self.border.in_range(particle)
                particle.draw()


            pygame.display.flip()
            self.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    simulation()
