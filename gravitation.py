
import numpy as np
from particle import Particle

class Gravitation():
    def __init__(self, grav_force, electric_force = 50000) -> None:

        self.grav_force = grav_force
        self.electric_force = electric_force  # Coulomb's constant in N·m²/C²

    def compute_gravity(self, all_particles, x= 800, y = 600, periodic=False):

        all_parts = all_particles
        if periodic:
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if i == 0 and j == 0:
                        continue
                    for part in all_particles:
                        new_part = Particle(part.position + np.array((i*x,j*y)), speed = part.speed.copy(), acc = part.acc.copy(), color = part.color, size = part.size, heat_factor = part.heat_factor, mass = part.mass, trace = False, ghost = True)
                        all_parts.append(new_part)
        
        for index1, part1 in enumerate(all_parts):
            

            for index2, part2 in enumerate(all_parts):
                if index1 > index2:
                    position_vector = part2.position - part1.position
                    norme = np.linalg.norm(position_vector)
                    intensity = -part1.mass * part2.mass * self.grav_force / norme

                    unit_acc = position_vector * intensity / norme
                    part1.acc -= unit_acc / part1.mass
                    part2.acc += unit_acc / part2.mass

                    intensity = part1.charge * part2.charge * self.electric_force / norme

                    unit_acc = position_vector * intensity / norme
                    part1.acc -= unit_acc / part1.mass
                    part2.acc += unit_acc / part2.mass


                    
                else:
                    break
