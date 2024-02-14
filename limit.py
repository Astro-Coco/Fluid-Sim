import numpy as np
class limits:
    def __init__(self, x,y, dt):
        self.x_1 = 0
        self.y_1 = 0
        self.x_2 = x
        self.y_2 = y
        self.dt = dt
        self.bounce_efficiency = 0.95


    def keep_all_in_range(self, all_particles):


        # Identify particles outside the screen

        # Update positions of particles outside the screen
        ypos = all_particles['pos'].apply(lambda x:x[1])
        y_mask = ((ypos < 0) | (ypos > self.y_2))
        pos = all_particles['pos'][y_mask]
        vel = all_particles['speed'][y_mask]
        for x,v in zip(pos, vel):
                v[1] *= -1
                x[1] += v[1]

        xpos = all_particles['pos'].apply(lambda x:x[0])
        x_mask = ((xpos < 5) | (xpos+5 > self.x_2))
        pos = all_particles['pos'][x_mask]
        vel = all_particles['speed'][x_mask]
        for x,v in zip(pos, vel):
                v[0] *= -1
                x[0] += v[0]

        

        