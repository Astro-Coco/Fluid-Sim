import numpy as np
class particle:
    
    def __init__(self, position : np.array, speed : np.array = np.array([0.,0.]) ,acc : np.array = np.array([0.,0.]), dt = 0.001, x_2 = 600, y_2 = 600):
        self.position = position
        self.speed = speed
        self.acc = acc
        

        self.dt = dt
        self.talk = False

    def step(self, dt):

        #réévalue les positons et vitesses
        if self.talk:
            print(f" pos : {self.position}, speed : {self.speed}, acc : {self.acc}")

        self.speed = self.speed*(1-dt/25) + self.acc*dt
        self.position += self.speed*dt
        

   