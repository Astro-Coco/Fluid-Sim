import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from limit import limits
import numpy as np
import lj_interaction as lj
import pandas as pd


class particles:
    def __init__(self, dt):
        self.all = pd.DataFrame({'id' : [], 'pos' : np.ndarray([]), 'speed' :  np.ndarray([]), 'acc' :  np.ndarray([]), 'color' : [], 'size' : []})

        self.field = np.array([0,-20])

        self.dt = dt
    
    def add_part(self,pos, id = None, speed = np.array([10.,0.]), acc = np.array([0.,-10.]), color = (0,200,255), size = 10):
        if id == None:
            id = self.all['id'].max()+1
            if id == None:
                id = 0

        self.all = pd.concat([self.all, pd.DataFrame({'id' : [id], 'pos' : [pos], 'speed' : [speed], 'acc' : [acc], 'color' : [color], 'size' : [size]})], ignore_index=True)
        

    def step(self):
        self.all['speed'] += self.all['acc']
        self.all['pos'] += self.all['speed']

    def draw(self):
        for index, part in self.all.iterrows(): 
            glColor3fv(part['color'])
            glPointSize(part['size'])
            glBegin(GL_POINTS)
            glVertex2f(*part['pos'])
            glEnd()

class simulation():
    def __init__(self) -> None:

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.DOUBLEBUF | pygame.OPENGL) 
        self.clock = pygame.time.Clock()
        self.dt = 0.1
        self.border = limits(800, 600, self.dt)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.particles = particles(dt = self.dt)
        self.collision = lj.lj_repulsion()
        self.generate_particles(600)

        self.mainloop()

    def generate_particles(self, n_particles, random = True, x_max = 800, y_max = 600):

        if random:
            x_range = [np.random.random()*x_max for i in range(n_particles)]
            y_range = [np.random.random()*y_max for i in range(n_particles)]

            for x,y in zip(x_range, y_range):
                self.particles.add_part((np.array((x,y))))
        else:
            base_x = 200.
            final_x = 600.
            base_y = 200.
            final_y = 400.
            x_range = np.linspace(base_x,final_x,n_particles)
            y_range = np.linspace(base_y,final_y,n_particles)

            for x,y in zip(x_range, y_range):
                self.particles.add_part((np.array((x,y))))

            



    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            '''self.collision.repulse(all_particles = self.particles)'''

            self.particles.step()

            self.border.keep_all_in_range(self.particles.all)
            self.particles.draw()


            pygame.display.flip()
            self.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    simulation()
