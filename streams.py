import numpy as np
class Stream:
    def __init__(self, dt, x1 = 250,x2 = 550,y1 = 400 ,y2 = 600, field = np.array([0.,-10.])):
        self.x_1 = x1
        self.y_1 = y1
        self.x_2 = x2
        self.y_2 = y2
        self.dt = dt
        self.field = field
        self.viscosity = 0.1

    def flow(self, particle):
        pos = particle.position

        if pos[0]>self.x_1 and pos[0]<self.x_2  and pos[1]>self.y_1 and pos[1]<self.y_2:

            particle.speed += self.field


            
        