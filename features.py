import pygame
import numpy as np
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

