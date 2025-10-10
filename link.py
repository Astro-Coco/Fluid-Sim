import numpy as np
from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, GL_LINES


class SpringLink:
    """
    Represents one spring-damper link between two Particle objects.
    Hooke's law + damping on relative velocity.
    """

    def __init__(self, p1, p2, rest_length=None, k=100.0, damping=1.0, color=(0.7, 0.7, 0.7)):
        self.p1 = p1
        self.p2 = p2
        self.k = k                  # spring stiffness (N/m)
        self.damping = damping      # viscous damping coefficient
        self.color = color
        self.rest_length = rest_length or np.linalg.norm(p2.position - p1.position)

    def apply_forces(self):
        r_vec = self.p2.position - self.p1.position
        r = np.linalg.norm(r_vec)
        if r < 1e-6:
            return
        n = r_vec / r

        # Hooke's law: F = -k * (x - x0)
        spring_force = -self.k * (r - self.rest_length)

        # Damping proportional to relative velocity along n
        rel_vel = np.dot(self.p2.speed - self.p1.speed, n)
        damping_force = -self.damping * rel_vel

        # Total scalar force along n
        F = spring_force + damping_force

        # Apply to each particle
        self.p1.acc += F * n / self.p1.mass
        self.p2.acc -= F * n / self.p2.mass

    def draw(self):
        glColor3f(*self.color)
        glBegin(GL_LINES)
        glVertex2f(self.p1.position[0], self.p1.position[1])
        glVertex2f(self.p2.position[0], self.p2.position[1])
        glEnd()


class ParticleChain:
    """
    Creates and manages a chain (or cluster) of particles connected by spring-dampers.
    If 3 particles are given, they are locked at 120° from each other.
    """

    def __init__(self, particles, k=100.0, damping=1.0, connect_all=False, color=(0.7, 0.7, 0.7)):
        self.links = []
        self.particles = particles
        self.color = color
        self.k = k
        self.damping = damping

        # Create spring links
        if connect_all:
            for i in range(len(particles)):
                for j in range(i + 1, len(particles)):
                    self.links.append(SpringLink(particles[i], particles[j], rest_length=20, k=k, damping=damping, color=color))
        else:
            for i in range(len(particles) - 1):
                self.links.append(SpringLink(particles[i], particles[i + 1], rest_length=20, k=k, damping=damping, color=color))

    def apply_forces(self):
        # Basic spring-damper forces
        for link in self.links:
            link.apply_forces()

        # --- Optional angle locking (for 3-particle equilateral triangle) ---
        if len(self.particles) == 3:
            p1, p2, p3 = self.particles
            # Compute current vectors
            v1 = p1.position - p2.position
            v2 = p3.position - p2.position
            n1 = v1 / np.linalg.norm(v1)
            n2 = v2 / np.linalg.norm(v2)

            # Compute current angle
            cos_angle = np.clip(np.dot(n1, n2), -1.0, 1.0)
            angle = np.arccos(cos_angle)

            # Target 120° = 2π/3
            target_angle = 2 * np.pi / 3
            angle_error = angle - target_angle

            if abs(angle_error) > 1e-3:
                # Small restoring torque direction
                perp1 = np.array([-n1[1], n1[0]])
                perp2 = np.array([n2[1], -n2[0]])

                strength = 5 * self.k * angle_error

                # Apply corrective forces (pseudo-torque)
                p1.acc +=  strength * perp1 / p1.mass
                p3.acc +=  strength * perp2 / p3.mass
                p2.acc -= (strength * (perp1 + perp2)) / p2.mass

    def draw(self):
        for link in self.links:
            link.draw()
