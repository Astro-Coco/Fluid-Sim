from itertools import groupby
import numpy as np
import math



class Collision:
    def __init__(self,x,y,size) -> None:
        self.x = x
        self.y = y
        self.size = size
        fs = 1.3
        self.bins = (min(self.x,self.y)/(size*fs))**2
        self.side_bins = math.sqrt(self.bins)



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
                            gap =  mean - norme
                            portion2 = part2.size/mean
                            portion1 = part.size/mean

                            part.position -= gap*portion2*position_vector/norme
                            part2.position += gap*portion1*position_vector/norme

                            normal = position_vector/norme if norme != 0 else position_vector
                            relative_velocity_normal = np.dot(relative_velocity, normal)
                            
                            if relative_velocity_normal < 0:
                                # Calculate impulse
                                impulse = 2*part.mass*part2.mass / (part.mass + part2.mass)* relative_velocity_normal*normal
                                damp = 0.999
                                part.speed += damp*impulse / part.mass
                                part2.speed -= damp*impulse / part2.mass

                    else:
                        break
        else:
            pass
            #perfo.stop('compute in group')    

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

        