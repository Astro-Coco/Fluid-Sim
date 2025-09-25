
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from limit import limits
import numpy as np
from lj_interaction import lj_repulsion
import random
from streams import Stream
from pygame.locals import *

class Particle:
    def __init__(self, position, speed = np.array([5.,0.]), acc = np.array([0.,-20.]),  color = (0,200,255), size = 5, heat_factor = 0.04, mass = 1):
        self.position = np.array(position)
        self.speed = np.array(speed)
        self.acc = acc
        self.color = color
        self.size = size
        self.mass = mass
        

        self.heat_factor = heat_factor

    def draw(self):
        glColor3fv(self.color)
        glPushMatrix()
        glTranslatef(*self.position, 0)
        quad = gluNewQuadric()
        gluDisk(quad, 0, self.size/2, 32, 1)
        glPopMatrix()

    def step(self, dt):

        self.speed = np.array([1-random.random()*self.heat_factor,1-random.random()*self.heat_factor])*self.speed*(1-dt/10) + self.acc*dt
        self.position += self.speed*dt

class DraggableCircle():
    def __init__(self, boule,dt):
        self.dragging = False
        self.boule = boule
        self.dt = dt

    def update_position(self):
        self.last_pos =  self.boule.position
        self.boule.position = self.new_position

    def update_speed(self):
        self.boule.speed = (self.new_position-self.last_pos)/self.dt
        while np.linalg.norm(self.boule.speed) >= 1500:
            self.boule.speed *= 0.9

    def check_collision(self, mouse_pos):
        mouse_pos[1] = 600-mouse_pos[1]
        distance = np.linalg.norm(self.boule.position - mouse_pos)
        return distance < self.boule.size

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = np.array(pygame.mouse.get_pos())
            if self.check_collision(mouse_pos):
                self.dragging = True
        elif self.dragging and (event.type == pygame.MOUSEBUTTONUP):
            self.dragging = False

            self.update_speed()

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.new_position = np.array(pygame.mouse.get_pos())
            self.new_position = np.array([float(self.new_position[0]), float(600. - self.new_position[1])])
            self.update_position()

class Warp():
    def __init__(self,dt, radius = 60, intensity = 10.,y = 600,x = 600):
        self.dt = dt
        self.radius = radius
        self.intensity = intensity
        self.dragging = False
        self.inverted = False
        self.last_event = None

        self.y = y
        self.x = x

    def handle_events(self, event, all_particle, x, y):
        self.y = y
        self.x = x
        if event.type == 771 and self.last_event != 771:
            if not self.inverted:
                self.intensity = abs(self.intensity)
                self.inverted = True
            else:
                self.intensity = -abs(self.intensity)
                self.inverted = False
            

    

        if self.dragging and (event.type == pygame.MOUSEBUTTONUP):
            self.dragging = False

        elif (event.type == pygame.MOUSEMOTION and self.dragging) or event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True
            mouse_pos = np.array(pygame.mouse.get_pos())

            mouse_pos = np.array([float(mouse_pos[0]), float(self.y - mouse_pos[1])])


            for part in all_particle:
                vector = part.position - mouse_pos

                distance = np.linalg.norm(vector)
                
                if distance < self.radius:
                    part.speed += (self.intensity/distance)*vector

        self.last_event = event 
class simulation():
    def __init__(self, dt, N = 600, heat = 0.01, reacteur = True, big = True, collision_force = 81000, constant_field = np.array([0.,-100.]), warp = True, warp_radius = 30.) -> None:
        full_screen = True
        pygame.init()
        if full_screen:
            self.x, self.y = 1550, 850
        else:
            self.x, self.y = 1550/2,850
        self.screen = pygame.display.set_mode((self.x,self.y), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE) 
        self.clock = pygame.time.Clock()
        self.dt = dt
        self.N = N
        self.heat = heat
        self.border = limits(x = self.x,y =  self.y, dt = self.dt)
        self.reacteur = reacteur
        self.big = big
        self.collision_force = collision_force
        self.warp_radius = warp_radius
        self.warp_intensity = -600
        if reacteur:
            self.initialize_reactor()
        if warp:
            self.warp = Warp(dt = self.dt, radius = self.warp_radius, intensity= self.warp_intensity, y = self.y, x = self.x)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.x, 0, self.y)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self.particles = []
        self.collision = lj_repulsion(self.collision_force, constant_field= constant_field)
        self.generate_particles(N, x_max = self.x, y_max = self.y)
        

        if self.big:
            self.Boule = Particle( position=np.array([self.x/2,self.y/2]), speed = np.array([0.,0.]), acc = np.array([0.,0.]), size = 50, color = (1,0,0),mass = 25)
            self.particles.append(self.Boule)
            self.BOULE = DraggableCircle(self.Boule,self.dt)

        self.mainloop()

    def initialize_reactor(self):
        self.stream = Stream(x1 = 300,x2 = 500, y1 = 300, y2= 600,dt = self.dt, field = np.array([0.,-10]))
        self.Istream = Stream(x1 = 350,x2 = 450, y1 = 350, y2= 600,dt = self.dt, field = np.array([0.,-50]))

        self.Lstream = Stream(x1 = 100,x2 = 300, y1 = 400, y2= 600,dt = self.dt, field = np.array([7.,-2.]))
        self.Rstream = Stream(x1 = 500,x2 = 700, y1 = 400, y2= 600,dt = self.dt, field = np.array([-7.,-2.]))

        self.llstream = Stream(x1 =300, x2 = 400, y1 = 0, y2 = 175, dt = self.dt, field = np.array([-5.,1]))
        self.lrstream = Stream(x1 =400, x2 = 500, y1 = 0, y2 = 175, dt = self.dt, field = np.array([5.,1]))

        self.lustream = Stream(x1 =25 , x2 = 300, y1 = 25, y2 = 300, dt = self.dt, field = np.array([0.5,8]))
        self.rustream = Stream(x1 =500, x2 = 775, y1 = 25, y2 = 300, dt = self.dt, field = np.array([-0.5,8]))



    def generate_particles(self, n_particles, random = True , x_max = 600, y_max = 600):

        if random:
            x_range = [np.random.random()*x_max for i in range(n_particles)]
            y_range = [np.random.random()*y_max for i in range(n_particles)]

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))),speed = np.array([50.,0.]),  size = 10, heat_factor = self.heat))
        else:
            base_x = 200.
            final_x = 600.
            base_y = 200.
            final_y = 400.
            x_range = np.linspace(base_x,final_x,n_particles)
            y_range = np.linspace(base_y,final_y,n_particles)

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))),speed = np.array([300.,0.]),  size = 10, heat_factor = self.heat))


    def mainloop(self):
        running = True
        while running:
            for event in pygame.event.get():
                self.last_event = event
                if event.type == pygame.QUIT:
                    running = False
                if self.big:
                    self.BOULE.handle_events(event)

            self.warp.handle_events(self.last_event,self.particles,self.x,self.y)
                

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            self.collision.repulse(all_particles = self.particles,x = self.x, y = self.y)
            for particle in self.particles:
                particle.step(dt = self.dt)
                self.border.in_range(particle)
                if self.reacteur:
                    self.stream.flow(particle)
                    self.Istream.flow(particle)
                    self.Lstream.flow(particle)
                    self.Rstream.flow(particle)
                    self.llstream.flow(particle)
                    self.lrstream.flow(particle)
                    self.lustream.flow(particle)
                    self.rustream.flow(particle)
                
                particle.draw()


            pygame.display.flip()
            self.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    
    simulation( dt = 0.01, N = 350, heat = 0.01, reacteur = False, big = True, collision_force = 90000, constant_field= np.array([0.,-300.]), warp = True, warp_radius =120)
