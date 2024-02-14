import pygame
import numpy as np
import part
import limit
import random
from lj_interaction import lj_repulsion
# initializing imported module 
pygame.init() 
dt = 0.12
# displaying a window of height 
# 500 and width 400 
window = pygame.display.set_mode((500, 500), pygame.RESIZABLE) 
x, y = window.get_size()  

# creating a bool value which checks 
# if game is running 
running = True

border = limit.limits(x,y,dt)
lj = lj_repulsion()

all_parts = {}
for i in range(150):
    all_parts[i] = part.particle(np.array([random.random()*x, random.random()*y]), speed = np.array([random.random()*10,random.random()*-10]), acc = np.array([0.,5.]), dt = dt)


# keep game running till running is true 
while running: 
    #update borders
    border.x_2, border.y_2 = window.get_size()

    window.fill((0,0,0)) 
    # Check for event if user has pushed 
    # any event in queue 
    for event in pygame.event.get(): 
          
        # if event is of type quit then  
        # set running bool to false 
        if event.type == pygame.QUIT: 
            running = False
    
    lj.repulse(all_particles = all_parts)

    for index, particle in all_parts.items():

        
        particle.step(dt = dt)
        border.in_range(particle)

        pygame.draw.circle(window, (0, 200, 255),particle.position, 6, 0)
        
 
# Draws the surface object to the screen.
    pygame.display.update()