from itertools import groupby
import numpy as np
import math

import time

class opération():
    def __init__(self,name):
        self.name = name
        self.i = None
        self.f = None
        self.temps = []

class performance():
    def __init__(self):
        self.operations = {}

    def time(self, name = 'name of operation'):
        if name not in self.operations:
            self.operations[name] = opération(name)

    def start(self, operation_name = 'operation name'):
        self.operations[operation_name].i = time.time()

    def stop(self, operation_name = 'operation name'):
        self.operations[operation_name].f = time.time()
        self.operations[operation_name].temps.append(self.operations[operation_name].f-self.operations[operation_name].i)

        if len(self.operations[operation_name].temps)%200 == 0:
            print(operation_name, ' : ' , np.mean(np.array(self.operations[operation_name].temps)))

#perfo = performance()
class Collision:
    def __init__(self,x,y,size) -> None:
        self.x = x
        self.y = y
        self.size = size
        fs = 1.3
        self.bins = (min(self.x,self.y)/(size*fs))**2
        self.side_bins = math.sqrt(self.bins)
        #perfo.time('compute in group')
        #perfo.time('check collision')


    def compute_in_group(self,groups):
        #perfo.start('compute in group')
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

                            part.position -= gap*portion1*position_vector/norme
                            part2.position += gap*portion2*position_vector/norme

                            normal = position_vector/norme if norme != 0 else position_vector
                            relative_velocity_normal = np.dot(relative_velocity, normal)
                            
                            if relative_velocity_normal < 0:
                                # Calculate impulse
                                impulse = 2*part.mass*part2.mass / (part.mass + part2.mass)* relative_velocity_normal*normal

                                part.speed += impulse / part.mass
                                part2.speed -= impulse / part2.mass

                    else:
                        break
        else:
            pass
            #perfo.stop('compute in group')    

    def check_collision(self, all_parts):
        #perfo.start('check collision')
        multi = False
        two =True
        x_box = self.x / self.side_bins
        y_box = self.y / self.side_bins
        for particle in all_parts:
            pos_x = particle.position[0]
            pos_y = particle.position[1]
            
            x_bin = pos_x // x_box
            y_bin = pos_y // y_box
            bin_number = y_bin * self.side_bins + x_bin
            particle.bin_number = bin_number

            if two:
                x2_bin = (pos_x - 0.5*x_box) // x_box
                y2_bin = (pos_y-0.5*y_box) // y_box
                bin_number2 = y2_bin * self.side_bins + x2_bin
                particle.bin_number2 = bin_number2
            
            
        ################################################################
        sorted_parts1 = sorted(all_parts, key=lambda particle: particle.bin_number)
        grouped_objects1 = {key: list(group) for key, group in groupby(sorted_parts1, key=lambda x: x.bin_number)}
        if two:
            sorted_parts2 = sorted(all_parts, key=lambda particle: particle.bin_number2)
            grouped_objects2 = {key: list(group) for key, group in groupby(sorted_parts2, key=lambda x: x.bin_number2)}
        #perfo.stop('check collision')
        threads = []
        if multi:
            pass
            #thread = threading.Thread(target=compute_in_group, args=(grouped_objects1.values(),), kwargs={'N': len(all_parts), 'bins': self.bins, 'collision_force': self.factor}).start()
        else:
            self.compute_in_group(grouped_objects1.values())
        
        if multi:
            pass
            #thread = threading.Thread(target=compute_in_group, args=(grouped_objects2.values(),), kwargs={'N': len(all_parts), 'bins': self.bins, 'collision_force': self.factor}).start()
        elif two:
            self.compute_in_group(grouped_objects2.values())

        