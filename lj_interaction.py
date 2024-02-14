import numpy as np
import math
from itertools import groupby
class lj_repulsion:
    def __init__(self):
        self.factor = 10000
        self.bins = 100
        self.side_bins = math.sqrt(self.bins)


    def repulse(self, all_particles,x = 800, y = 600, field = np.array([0,-50])):

        for particle in all_particles:
            particle.acc = field
            pos_x = particle.position[0]
            pos_y = particle.position[1]
            x_bin = pos_x//(x/self.side_bins)
            y_bin = pos_y//(y/self.side_bins)
            

            bin_number = y_bin*self.side_bins + x_bin
            particle.bin_number = bin_number
        

        sorted_parts = sorted(all_particles, key=lambda particle: particle.bin_number)

        grouped_objects = {}
        for key, group in groupby(sorted_parts, key=lambda x: x.bin_number):
            grouped_objects[key] = list(group)

        # Example: Print the grouped objects
        for group in grouped_objects.values():

            for index1, part in enumerate(group):
                for index2, part2 in enumerate(group):
                    if index1 < index2:

                        position_vector = np.array(part2.position) - np.array(part.position)
                        norme = np.linalg.norm(position_vector)

                        if norme < 3:
                            norme = 3


                        intensity = self.factor/norme**2
                        unit_acc = position_vector * intensity/norme

                        part.acc = part.acc - unit_acc
                        part2.acc = part2.acc + unit_acc

            
