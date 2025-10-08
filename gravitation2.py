
import math
import numpy as np
from itertools import groupby

class Gravitation():
    def __init__(self, grav_force):
        self.bins = 400
        self.side_bins = math.sqrt(self.bins)
        self.grav_force = grav_force

    def compute_gravity(self, all_particles, x= 800, y = 600):
        x_box = x / self.side_bins
        y_box = y / self.side_bins

        for particle in all_particles:
            pos_x = particle.position[0]
            pos_y = particle.position[1]
            x_bin = pos_x // x_box
            y_bin = pos_y // y_box
            bin_number = y_bin * self.side_bins + x_bin
            particle.bin_number = bin_number


        sorted_parts1 = sorted(all_particles, key=lambda particle: particle.bin_number)
        grouped_objects1 = {key: list(group) for key, group in groupby(sorted_parts1, key=lambda x: x.bin_number)}
        self.compute_in_group(grouped_objects1.values(), len(all_particles), bins=self.bins)

    def compute_in_group(self, groups, N, bins = 16):
        for group in groups:
            factor = len(group) * bins / N

            for index1, part in enumerate(group):

                for index2, part2 in enumerate(group):
                    if index1 > index2:
                        

                        position_vector = part2.position - part.position
                        norme = np.linalg.norm(position_vector)
                        intensity = -part.mass * part2.mass * self.grav_force / norme

                        unit_acc = position_vector * intensity / norme
                        part.acc = part.acc - unit_acc / part.mass
                        part2.acc = part2.acc + unit_acc / part2.mass
                        

                    else:
                        break