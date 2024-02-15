import numpy as np
import math
from itertools import groupby
def smoothstep(edge0, edge1, x):
    # Scale, bias and saturate x to 0..1 range
    x = max(0.0, min((x - edge0) / (edge1 - edge0), 1.0))
    # Evaluate polynomial
    return x * x * (1 - 0.35 * x)
class lj_repulsion:
    def __init__(self, collision_force, constant_field = np.array([0., -100.])):
        self.factor = collision_force
        self.bins = 100
        self.side_bins = math.sqrt(self.bins)
        self.field  = constant_field


    def repulse(self, all_particles,x = 800, y = 600):

        for particle in all_particles:
            particle.acc = self.field
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

        N = len(all_particles)
    # Example: Print the grouped objects
        for group in grouped_objects.values():
            factor = len(group)*self.bins/N
            red = smoothstep(0.1, 1.8, factor)
            blue = smoothstep(1.3, 0.3, factor)
            # Green is constant
            green = smoothstep(0.05,0.5,factor)
            for index1, part in enumerate(group):
                for index2, part2 in enumerate(group):
                    if index1 > index2:

                        position_vector = part2.position - part.position
                        norme = np.linalg.norm(position_vector)

                        
                        
                        
                        if part.mass > 10 or part2.mass > 10:
                            maxsize = max(part.size, part2.size)
                            if norme < maxsize*1.3:
                                norme = 17
                        elif norme < 8:
                            norme = 4

                        intensity = part.mass*part2.mass*self.factor/norme**2
                        unit_acc = position_vector * intensity/norme
                        
                        

                        part.acc = part.acc - unit_acc/part.mass
                        part2.acc = part2.acc + unit_acc/part2.mass

                        part.color, part2.color = (red,green,blue),(red,green,blue)
                        
                    else:
                        break

            
