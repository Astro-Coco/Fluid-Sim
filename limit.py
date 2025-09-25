import numpy as np
class limits:
    def __init__(self, x,y, dt):
        self.x_1 = 0
        self.y_1 = 0
        self.x_2 = x
        self.y_2 = y
        self.dt = dt
        self.bounce_efficiency = 1

    def in_range(self, particle):
        pos = particle.position

        if pos[0]<self.x_1 or pos[0]>self.x_2 :

            particle.position -= particle.speed*self.dt
            particle.speed = self.bounce_efficiency*np.array([-1*particle.speed[0], particle.speed[1]])

            return particle.position, particle.speed
            
        
        if pos[1]<self.y_1 or pos[1]>self.y_2 :

            particle.position -= particle.speed*self.dt
            particle.speed = self.bounce_efficiency*np.array([particle.speed[0], -1*particle.speed[1]])

            return particle.position, particle.speed

        