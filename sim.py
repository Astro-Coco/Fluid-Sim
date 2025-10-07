
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
from Collisions import Collision
from FLOW import Flow
from gravitation import Gravitation

class Particle:
    def __init__(self, position, speed = np.array([5.,0.]), acc = np.array([0.,0.]),  color = (0,200,255), size = 8, heat_factor = 0.04, mass = 1, trace = False):
        self.position = np.array(position)
        self.speed = np.array(speed)
        self.acc = acc
        self.color = color
        self.size = size
        self.mass = mass
        self.trace = trace
        

        self.heat_factor = heat_factor
        self.trace = [np.copy(position)]
        self.max_trail_length = 500

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
        if max(r, g, b) > 1.0:
            r, g, b = r / 255.0, g / 255.0, b / 255.0

        glColor3f(r, g, b)
        glLineWidth(3.0)
        glBegin(GL_LINE_STRIP)
        for pos in self.trace:
            glVertex2f(*pos)
        glEnd()


    def step(self, dt):
        friction = True
        if friction:
            term = self.speed**2*dt/1000
            if np.linalg.norm(self.speed)<40:
                term = 0
            self.speed = self.speed - term  + self.acc*dt
        else:
            self.speed = self.speed + self.acc*dt
        self.position += self.speed*dt
    
        if self.trace:
            if self.color != (0,0,0):
                self.trace.append(np.copy(self.position))
            if len(self.trace) > self.max_trail_length:
                self.trace.pop(0)

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
        while (np.linalg.norm(self.boule.speed) >= 250):
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
    def __init__(self, dt = 0.01, N = 600, heat = 0.01, reacteur = True, big = True, collision_force = 81000, constant_field = np.array([0.,0.]), warp = True, warp_radius = 30., gravity = 80000, trace_paths=False, full_screen = False) -> None:
        full_screen = True
        pygame.init()
        if full_screen:
            self.x, self.y = 1550, 850
        else:
            self.x, self.y = 800,600
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
        self.warp_intensity = -400
        self.gravity = gravity
        self.trace_paths = trace_paths
        self.flow = Flow(self.x,self.y)
        if self.gravity is not None:
            self.gravitational = Gravitation(grav_force = self.gravity)
        if reacteur:
            self.initialize_reactor()
        if warp:
            self.warp = Warp(dt = self.dt, radius = self.warp_radius, intensity= self.warp_intensity, y = self.y, x = self.x)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.x, 0, self.y)
        glMatrixMode(GL_MODELVIEW)
        self.particles = []
        self.generate_particles(N, x_max = self.x, y_max = self.y, custom = True, random= True, trace = True)
        self.collision = Collision(self.x,self.y,100)
        self.lj = lj_repulsion(collision_force=collision_force,constant_field=constant_field)
        
        

        if self.big:
            self.Boule = Particle( position=np.array([self.x/2,self.y/2]), speed = np.array([0.,0.]), acc = np.array([0.,0.]), size = 10, color = (1,0,0),mass = 25)
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



    def generate_particles(self, n_particles, random = True , x_max = 600, y_max = 600, regular = False, custom = False, trace = False):
        if custom:
            print("Custom particles")
            first_factor = int((np.random.random()+ 0.05)*45)
            self.particles.append(Particle((np.array((np.random.random()*self.x,np.random.random()*self.y))),speed = np.array([(np.random.random()-0.5)*300,(np.random.random()-0.5)*300]),  size = first_factor/3,color = (0,100,0), heat_factor = self.heat,mass = first_factor/6))
            self.particles.append(Particle((np.array((np.random.random()*self.x,np.random.random()*self.y))),speed = np.array([(np.random.random()-0.5)*300,(np.random.random()-0.5)*300]),  size = first_factor/1.5,color = (100,0,0), heat_factor = self.heat,mass = first_factor/3))
            self.particles.append(Particle((np.array((np.random.random()*self.x,np.random.random()*self.y))),speed = np.array([(np.random.random()-0.5)*300,(np.random.random()-0.5)*300]),  size = first_factor/0.75,color = (0,0,1), heat_factor = self.heat,mass = 2*first_factor/3))
            first_factor = int((np.random.random()+ 0.1)*40)
            #self.particles.append(Particle((np.array((np.random.random()*self.x,np.random.random()*self.y))),speed = np.array([(np.random.random()-0.5)*600,(np.random.random()-0.5)*600]),  size = first_factor,color = (0,0,0), heat_factor = self.heat,mass = first_factor/2))
        elif random:
            x_range = [np.random.random()*x_max for i in range(n_particles)]
            y_range = [np.random.random()*y_max for i in range(n_particles)]

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))),speed = np.array([np.random.random()*300,(np.random.random()-0.5)*400]),  size = 12, heat_factor = self.heat,mass = 2, trace = False))
        elif regular:
            base_x = 200.
            final_x = 600.
            base_y = 200.
            final_y = 400.
            x_range = np.linspace(base_x,final_x,n_particles)
            y_range = np.linspace(base_y,final_y,n_particles)

            for x,y in zip(x_range, y_range):
                self.particles.append(Particle((np.array((x,y))),speed = np.array([np.random.random()*300,(np.random.random()-0.5)*400]),  size = 5, heat_factor = self.heat, trace = False))
    
    def mainloop(self):
        i = 0
        running = True


        while running:
            i+=1


            for event in pygame.event.get():
                self.last_event = event
                if event.type == pygame.QUIT:
                    running = False
                if self.big:
                    self.BOULE.handle_events(event)

            self.warp.handle_events(self.last_event,self.particles,self.x,self.y)
                

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            self.collision.check_collision(all_parts = self.particles)
            if self.gravity is not None:
                self.gravitational.compute_gravity(all_particles = self.particles, x = self.x, y = self.y)

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
                
                if self.trace_paths:
                    particle.draw_trace()
                particle.draw()

            pygame.display.flip()
            self.clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    simulation( dt = 0.005,
                N = 200,
                  heat = 0.0,
                    reacteur = False,
                      big = False,
                        collision_force = -10000,
                            constant_field= np.array([0.,0.]),
                              warp = True,
                                warp_radius =80,
                                  gravity = 20000, 
                                   trace_paths=True)
