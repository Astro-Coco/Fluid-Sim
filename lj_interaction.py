import numpy as np
class lj_repulsion:
    def __init__(self):
        self.factor = 3000

    def repulse(self, all_particles):
        for index1, particle in all_particles.items():
            particle.acc = np.array([0.,5.])
            for index2, second_particle in all_particles.items():
                if index1 < index2:
                    position_vector = second_particle.position - particle.position
                    norme = np.linalg.norm(position_vector)

                    if norme < 5:
                        norme = 5

                    if norme < 50:
                        intensity = self.factor/norme**2
                        unit_acc = position_vector * intensity/norme

                        particle.acc = particle.acc - 1*unit_acc
                        second_particle.acc = second_particle.acc + unit_acc