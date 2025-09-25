import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random

class StaggeredGrid:
    def __init__(self, n, cell_size):
        self.n = n
        self.cell_size = cell_size
        self.u_velocity_grid = np.zeros((n, n+1))  # Staggered grid for u-velocity
        self.v_velocity_grid = np.zeros((n+1, n))  # Staggered grid for v-velocity

    def get_u_velocity(self, i, j):
        return self.u_velocity_grid[i, j]

    def get_v_velocity(self, i, j):
        return self.v_velocity_grid[i, j]

    def set_u_velocity(self, i, j, value):
        self.u_velocity_grid[i, j] = value

    def set_v_velocity(self, i, j, value):
        self.v_velocity_grid[i, j] = value

class Cell():
    def __init__(self, x, y,g = 0, cell_size = 7, Vy = 0, Vx = 0, u_velocity = 0, v_velocity = 0):
        self.g = g
        self.cell_size = cell_size
        self.half_cell_size = cell_size // 2
        self.x = x
        self.y = y

        self.u_velocity = u_velocity
        self.v_velocity = v_velocity

        self.Vy = Vy
        self.Vx = Vx

        self.not_wall = True
        self.id = None
        self.color = (np.random.random(),np.random.random(),np.random.random())

        self.p = None
        self.s = None
        self.density = None

    def gravity(self):
        self.Vy += self.g

    def compute_divergence(self):
        self.divergence = (self.neighbors[0].Vy -  self.neighbors[1].Vy + self.neighbors[2].Vx - self.neighbors[3].Vx)
        return self.divergence
    
    def compute_number_of_non_walls(self):
        self.s = 0
        for next_cell in self.neighbors:
            if next_cell.not_wall:
                self.s += 1
        return self.s

    def step(self):
        self.u_velocity = self.Vx
        self.v_velecity = self.Vy
        self.gravity()
        self.compute_divergence()

    def step(self):
        # Update velocities based on staggered grid values
        self.Vx = self.u_velocity
        self.Vy = self.v_velocity

    def apply_external_force(self, force_x, force_y):
        # Apply external force to staggered grid
        i = int((self.x) // self.cell_size)
        j = int((self.y) // self.cell_size)
        self.simulation.staggered_grid.set_u_velocity(i, j, self.simulation.staggered_grid.get_u_velocity(i, j) + force_x)
        self.simulation.staggered_grid.set_v_velocity(i, j, self.simulation.staggered_grid.get_v_velocity(i, j) + force_y)

    def apply_external_force(self, force_x, force_y):
        # Apply external force (if any) to the cell's velocities
        self.Vx += force_x
        self.Vy += force_y


class Wall():
    def __init__(self,cell_size = 7):
        self.cell_size = cell_size
        self.half_cell_size = cell_size // 2

        self.Vy = 0
        self.Vx = 0

        self.p = None
        self.s = None
        self.density = None

        self.not_wall = False

class Cells():
    def __init__(self,simulation):
        self.all = np.array([])
        self.simulation = simulation
        self.current_id = 0

    def add_cell(self, cell):
        cell.id = self.current_id
        self.current_id += 1
        self.all = np.append(self.all, np.array(cell))
    
    def select_id(self, id):
        if id < self.simulation.n**2:
            return self.all[id]
        else:
            return self.simulation.wall

    def neighbors(self,cell):
        id = cell.id
        cell.up = id + self.simulation.n
        cell.down = id - self.simulation.n
        cell.left = id - 1
        cell.right = id + 1

        cell.neighbors = self.select_id(cell.up), self.select_id(cell.down),self.select_id(cell.right),self.select_id(cell.left)
        return cell.neighbors

    def find_neighbors(self):
        
        for cell in self.all:
            cell.neighbors = self.neighbors(cell)


    def force_zero_div(self):
        for iterations in range(10):
            for cell in self.all:
                div = cell.compute_divergence()
                s = cell.compute_number_of_non_walls()
                cell.neighbors[0].Vy -= div*cell.neighbors[0].not_wall/s
                cell.neighbors[1].Vy += div*cell.neighbors[1].not_wall/s
                cell.neighbors[2].Vx += div*cell.neighbors[2].not_wall/s
                cell.neighbors[3].Vx -= div*cell.neighbors[3].not_wall/s

 
class simulation():
    def __init__(self,dt,n = 100) -> None:
        full_screen = False
        pygame.init()
        self.time = 0
        self.dt = dt
        self.n = n
        self.gravity = 100
        

        self.x, self.y = 800, 800
        self.screen = pygame.display.set_mode((self.x, self.y), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.x, 0, self.y)
        glMatrixMode(GL_MODELVIEW)

        self.wall = Wall()

        self.cells = Cells(self)
        self.generate_grid_points(n=self.n, margin=0)  # Adjust n and margin as needed
        self.cells.find_neighbors()

        self.staggered_grid = StaggeredGrid(n, cell_size=5)

        self.mainloop()


    def generate_grid_points(self, n, margin):
        cell_size_x = (self.x - 2 * margin) / n
        cell_size_y = (self.y - 2 * margin) / n
        stagger = False
        for i in range(n):
            for j in range(n):
                x = margin + i * cell_size_x + cell_size_x // 2
                y = margin + j * cell_size_y + cell_size_y // 2
                u_velocity = 0  # Initialize u-velocity component
                v_velocity = 0  # Initialize v-velocity component
                if stagger:
                    u_velocity = 0  # Set staggered u-velocity
                else:
                    v_velocity = 0  # Set staggered v-velocity
                self.cells.add_cell(Cell(x, y, cell_size=5, Vy=np.random.random() * 400,
                                            u_velocity=u_velocity, v_velocity=v_velocity))
            stagger = not stagger


    def draw_gradient_cells(self):
        max_speed = max([(cell.Vy**2 + cell.Vx**2) for cell in self.cells.all])
        max_speed = max_speed if max_speed != 0 else 1
        
        for cell in self.cells.all:
            color = self.set_color(cell,max_speed)
            
            glBegin(GL_QUADS)
            glColor3f(*color)
            glVertex2f(cell.x - cell.half_cell_size, cell.y - cell.half_cell_size)  # Bottom right
            glVertex2f(cell.x + cell.half_cell_size, cell.y - cell.half_cell_size)  # Top right
            glVertex2f(cell.x + cell.half_cell_size, cell.y + cell.half_cell_size)  # Bottom left
            glVertex2f(cell.x - cell.half_cell_size, cell.y + cell.half_cell_size)  # Top left
            glEnd()


            draw_line = False
            if draw_line:
                # Draw lines connecting neighbors
                glColor3f(1.0, 1.0, 1.0)  # White color for lines
                glBegin(GL_LINES)
                for neighbor_id in [cell.up, cell.down, cell.left, cell.right]:
                    if 0 <= neighbor_id < len(self.cells.all):
                        neighbor_cell = self.cells.select_id(neighbor_id)
                        glVertex2f(cell.x, cell.y)  # Start point of line
                        glVertex2f(neighbor_cell.x, neighbor_cell.y)  # End point of line
                glEnd()


    def set_color(self,cell, max_speed):

        speed = cell.Vy**2 + cell.Vx**2
        
        return (1- speed/max_speed,0, speed/max_speed)

    def mainloop(self):
        i = 0
        running = True

        while running:
            i += 1
            self.time += self.dt
            for event in pygame.event.get():
                self.last_event = event
                if event.type == pygame.QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            self.draw_gradient_cells()  # Draw gradient colored cell

            for cell in self.cells.all:
                cell.apply_external_force(0, self.gravity)

            for i in range(self.n):
                for j in range(self.n):
                    self.staggered_grid.set_u_velocity(i, j, self.cells.all[i * self.n + j].u_velocity)
                    self.staggered_grid.set_v_velocity(i, j, self.cells.all[i * self.n + j].v_velocity)    

            pygame.display.flip()
            self.clock.tick(60)



        pygame.quit()

simulation(dt = 0.001)  # Example initialization with dt = 0.1
