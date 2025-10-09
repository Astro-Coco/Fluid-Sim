import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from pygame.locals import *

from limit import limits
from lj_interaction import lj_repulsion
from streams import Stream
from Collisions import Collision
from FLOW import Flow
from particle import Particle
from gravitation import Gravitation


# ---------------------------------------------------------------------------
# WARP TOOL
# ---------------------------------------------------------------------------
class Warp:
    def __init__(self, dt, radius=60, intensity=10.0, y=600, x=600):
        self.dt = dt
        self.radius = radius
        self.intensity = intensity
        self.dragging = False
        self.inverted = False
        self.last_event = None
        self.y = y
        self.x = x

    def handle_events(self, event, all_particle, x, y):
        """Handles interactive warp attraction/repulsion."""
        self.y, self.x = y, x

        # Toggle intensity direction
        if event.type == 771 and self.last_event != 771:
            self.intensity = -self.intensity
            self.inverted = not self.inverted

        # Mouse drag behavior
        if self.dragging and event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif (event.type == pygame.MOUSEMOTION and self.dragging) or event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True
            mouse_pos = np.array(pygame.mouse.get_pos(), dtype=float)
            mouse_pos = np.array([mouse_pos[0], self.y - mouse_pos[1]])

            for part in all_particle:
                vector = part.position - mouse_pos
                distance = np.linalg.norm(vector)
                if distance < self.radius and distance > 1e-3:
                    part.speed += (self.intensity / distance) * vector

        self.last_event = event


# ---------------------------------------------------------------------------
# MAIN SIMULATION CLASS
# ---------------------------------------------------------------------------
class Simulation:
    def __init__(
        self,
        dt=0.01,
        N=600,
        heat=0.01,
        reacteur=True,
        big=True,
        collision_force=81000,
        constant_field=np.array([0.0, 0.0]),
        warp=True,
        warp_radius=30.0,
        gravity=80000,
        trace_paths=False,
        full_screen=False,
    ):

        # ---------------------- CONFIGURATION ----------------------
        pygame.init()
        self.dt = dt
        self.N = N
        self.heat = heat
        self.reacteur = reacteur
        self.big = big
        self.collision_force = collision_force
        self.constant_field = constant_field
        self.gravity = gravity
        self.trace_paths = trace_paths

        # Screen configuration
        self.full_screen = full_screen
        self.x, self.y = (2500, 1000) if full_screen else (1850, 900)
        self.screen = pygame.display.set_mode(
            (self.x, self.y),
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()

        # Warp configuration
        self.warp_radius = warp_radius
        self.warp_intensity = -400
        if warp:
            self.warp = Warp(
                dt=self.dt,
                radius=self.warp_radius,
                intensity=self.warp_intensity,
                y=self.y,
                x=self.x,
            )

        # Field / physics components
        self.border = limits(x=self.x, y=self.y, dt=self.dt)
        self.flow = Flow(self.x, self.y)
        self.collision = Collision(self.x, self.y, 75)
        self.lj = lj_repulsion(collision_force=collision_force, constant_field=constant_field)
        self.gravitational = Gravitation(grav_force=self.gravity) if self.gravity else None

        # OpenGL setup
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.x, 0, self.y)
        glMatrixMode(GL_MODELVIEW)

        # Particles setup
        self.particles = []
        self.generate_particles(N, x_max=self.x, y_max=self.y, custom=True, random=True, trace=True)

        # Optional main particle
        if self.big:
            self.initialize_main_particle()

        # Optional reactor
        if self.reacteur:
            self.initialize_reactor()

        # Start simulation
        self.mainloop()

    # -------------------------------------------------------------------
    # INITIALIZATION HELPERS
    # -------------------------------------------------------------------
    def initialize_main_particle(self):
        """Creates central 'Boule' particle for interaction."""
        self.Boule = Particle(
            position=np.array([self.x / 2, self.y / 2]),
            speed=np.array([0.0, 0.0]),
            acc=np.array([0.0, 0.0]),
            size=50,
            color=(1, 0, 0),
            mass=75,
        )
        self.particles.append(self.Boule)
        self.BOULE = DraggableCircle(self.Boule, self.dt)

    def initialize_reactor(self):
        """Defines flow regions for the 'reactor' setup."""
        dt = self.dt
        self.stream = Stream(300, 500, 300, 600, dt, np.array([0.0, -10]))
        self.Istream = Stream(350, 450, 350, 600, dt, np.array([0.0, -50]))
        self.Lstream = Stream(100, 300, 400, 600, dt, np.array([7.0, -2.0]))
        self.Rstream = Stream(500, 700, 400, 600, dt, np.array([-7.0, -2.0]))
        self.llstream = Stream(300, 400, 0, 175, dt, np.array([-5.0, 1.0]))
        self.lrstream = Stream(400, 500, 0, 175, dt, np.array([5.0, 1.0]))
        self.lustream = Stream(25, 300, 25, 300, dt, np.array([0.5, 8.0]))
        self.rustream = Stream(500, 775, 25, 300, dt, np.array([-0.5, 8.0]))

    # -------------------------------------------------------------------
    # PARTICLE GENERATION
    # -------------------------------------------------------------------
    def generate_particles(self, n_particles, random=True, x_max=600, y_max=600, regular=False, custom=True, trace=False):
        """Populates the particle list."""
        if custom:
            print("Custom particles")
            first_factor, mass_size = 20, 3
            for color in [(100, 0, 0), (0, 100, 0), (0, 0, 100)]:
                pos = np.array([np.random.random() * self.x, np.random.random() * self.y])
                vel = np.array([(np.random.random() - 0.5) * 300, (np.random.random() - 0.5) * 300])
                self.particles.append(
                    Particle(pos, speed=vel, size=first_factor, color=color, heat_factor=self.heat, mass=first_factor * mass_size)
                )

        elif random:
            for _ in range(n_particles):
                pos = np.array([np.random.random() * x_max, np.random.random() * y_max])
                vel = np.array([np.random.random() * 300, (np.random.random() - 0.5) * 400])
                self.particles.append(Particle(pos, speed=vel, size=12, heat_factor=self.heat, mass=2, trace=False))

        elif regular:
            xs = np.linspace(200, 600, n_particles)
            ys = np.linspace(200, 400, n_particles)
            for x, y in zip(xs, ys):
                vel = np.array([np.random.random() * 300, (np.random.random() - 0.5) * 400])
                self.particles.append(Particle(np.array([x, y]), speed=vel, size=5, heat_factor=self.heat, trace=False))

    # -------------------------------------------------------------------
    # MAIN LOOP
    # -------------------------------------------------------------------
    def mainloop(self):
        running, frame = True, 0

        while running:
            frame += 1
            for event in pygame.event.get():
                self.last_event = event
                if event.type == pygame.QUIT:
                    running = False
                if self.big:
                    self.BOULE.handle_events(event)

            # Warp interaction
            if hasattr(self, "warp"):
                self.warp.handle_events(self.last_event, self.particles, self.x, self.y)

            # Clear frame
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Collisions and gravity
            self.collision.check_collision(all_parts=self.particles)
            if self.gravitational:
                self.gravitational.compute_gravity(all_particles=self.particles, x=self.x, y=self.y)

            # Particle physics + rendering
            for particle in self.particles:
                particle.step(dt=self.dt)
                self.border.in_range(particle)

                if self.reacteur:
                    for s in [self.stream, self.Istream, self.Lstream, self.Rstream,
                              self.llstream, self.lrstream, self.lustream, self.rustream]:
                        s.flow(particle)

                if self.trace_paths:
                    particle.draw_trace()
                particle.draw()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sim_params = dict(
        dt=0.002,
        N=100,
        heat=0.0,
        reacteur=False,
        big=False,
        collision_force=-10000,
        constant_field=np.array([0.0, 0.0]),
        warp=True,
        warp_radius=80,
        gravity=30000,
        trace_paths=True,
        full_screen=False,
    )

    Simulation(**sim_params)
