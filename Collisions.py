from itertools import groupby
import numpy as np
import math



class Collision:
    def __init__(self,x,y,size, bounce_efficiency = 0.999) -> None:
        self.x = x
        self.y = y
        self.size = size
        fs = 1.3
        self.bins = (min(self.x,self.y)/(size*fs))**2
        self.side_bins = math.sqrt(self.bins)
        self.bounce_efficiency = bounce_efficiency



    def compute_in_group(self,groups):
        for group in groups:
            for index1, part in enumerate(group):
                part.acc = np.array((0.,0.))
                for index2, part2 in enumerate(group):
                    if index1 > index2:
                        relative_velocity = part2.speed - part.speed
                        position_vector = part2.position - part.position
                        norme = np.linalg.norm(position_vector)
                        
                        mean = (part.size + part2.size)/2
                        if norme <= mean:
                            self.resolve_overlap(part, part2)

                            normal = position_vector/norme if norme != 0 else position_vector
                            relative_velocity_normal = np.dot(relative_velocity, normal)
                            
                            if relative_velocity_normal < 0:
                                # Calculate impulse
                                impulse = 2*part.mass*part2.mass / (part.mass + part2.mass)* relative_velocity_normal*normal
                                part.speed += self.bounce_efficiency*impulse / part.mass
                                part2.speed -= self.bounce_efficiency*impulse / part2.mass

                    else:
                        break
        else:
            pass
            #perfo.stop('compute in group')  

    def resolve_overlap(self, p1, p2, percent=0.9, slop=0.01):
        # Radii (if size is diameter, use r = size*0.5)
        r1 = 0.5 * p1.size
        r2 = 0.5 * p2.size
        delta = p2.position - p1.position
        d = np.linalg.norm(delta)
        if d == 0.0:
            # Perfectly coincident: pick an arbitrary axis
            n = np.array([1.0, 0.0], dtype=float)
            d = 1e-8
        else:
            n = delta / d

        # Overlap amount
        overlap = (r1 + r2) - d
        if overlap <= 0.0:
            return  # no overlap

        # Erin Catto's positional correction:
        correction = max(overlap - slop, 0.0) * percent
        # Inverse masses (treat mass<=0 as immovable/static)
        inv1 = 0.0 if p1.mass <= 0 else 1.0 / p1.mass
        inv2 = 0.0 if p2.mass <= 0 else 1.0 / p2.mass
        inv_sum = inv1 + inv2 if (inv1 + inv2) > 0 else 1e-8

        p1.position -= (inv1 / inv_sum) * correction * n
        p2.position += (inv2 / inv_sum) * correction * n
  

    def check_collision(self, all_parts):
        x_box = self.x / self.side_bins
        y_box = self.y / self.side_bins
        for particle in all_parts:
            pos_x = particle.position[0]
            pos_y = particle.position[1]
            
            x_bin = pos_x // x_box
            y_bin = pos_y // y_box
            bin_number = y_bin * self.side_bins + x_bin
            particle.bin_number = bin_number
            x2_bin = (pos_x - 0.5*x_box) // x_box
            y2_bin = (pos_y-0.5*y_box) // y_box
            bin_number2 = y2_bin * self.side_bins + x2_bin
            particle.bin_number2 = bin_number2
            
            
        ################################################################
        sorted_parts1 = sorted(all_parts, key=lambda particle: particle.bin_number)
        grouped_objects1 = {key: list(group) for key, group in groupby(sorted_parts1, key=lambda x: x.bin_number)}
        sorted_parts2 = sorted(all_parts, key=lambda particle: particle.bin_number2)
        grouped_objects2 = {key: list(group) for key, group in groupby(sorted_parts2, key=lambda x: x.bin_number2)}
        self.compute_in_group(grouped_objects1.values())
        self.compute_in_group(grouped_objects2.values())

        