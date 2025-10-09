# soft_collide.pyx
# cython: boundscheck=False, wraparound=False, initializedcheck=False, nonecheck=False
cimport cython
from libc.math cimport sqrt
import numpy as np
cimport numpy as cnp

@cython.boundscheck(False)
@cython.wraparound(False)
def soft_collide_particles(particles,
                           double k=2.0e4,        # spring (N/m-ish in sim units)
                           double c=40.0,         # damping along the normal
                           double beta=0.2,       # positional correction fraction (0..1)
                           bint size_is_diameter=True,
                           double dt=0.016):
    """
    Soft-sphere collisions for 2D disks (stable & simple).

    particles: list of objects with
        - position[2], speed[2], size, mass (float)
    k:     spring stiffness for overlap force
    c:     damping along the collision normal (critical-ish damping: increase if bouncy)
    beta:  small positional correction fraction of overlap to reduce sticking
    size_is_diameter: if True, 'size' is a diameter (so radius = size/2)
    dt:    simulation time step (seconds)

    Effect:
      - For each overlapping pair, apply equal & opposite velocity updates:
          J = ( k*overlap - c*(v_rel·n) ) * dt   along normal n
      - Apply tiny COM-preserving position corrections (beta * overlap).
    """
    cdef Py_ssize_t n = len(particles)
    if n <= 1:
        return

    # Extract to raw arrays (fast)
    pos = np.empty((n, 2), dtype=np.float64)
    vel = np.empty((n, 2), dtype=np.float64)
    rad = np.empty((n,),    dtype=np.float64)
    mass = np.empty((n,),   dtype=np.float64)

    cdef double[:, :] P = pos
    cdef double[:, :] V = vel
    cdef double[:]     R = rad
    cdef double[:]     M = mass

    cdef Py_ssize_t i, j
    cdef object p

    cdef double r
    for i in range(n):
        p = particles[i]
        P[i,0] = <double>p.position[0]
        P[i,1] = <double>p.position[1]
        V[i,0] = <double>p.speed[0]
        V[i,1] = <double>p.speed[1]
        r = <double>p.size
        if size_is_diameter:
            r *= 0.5
        R[i] = r
        M[i] = max(1e-9, <double>p.mass)  # avoid div by zero

    # Pairwise soft forces
    cdef double dx, dy, d2, d, sumR, overlap
    cdef double nx, ny, rvx, rvy, rvn
    cdef double mi, mj, inv_msum, move_i, move_j
    cdef double Fn, J

    for i in range(n):
        for j in range(i):
            dx = P[j,0] - P[i,0]
            dy = P[j,1] - P[i,1]
            d2 = dx*dx + dy*dy
            sumR = R[i] + R[j]

            if d2 == 0.0:
                # identical positions; nudge apart on x
                nx, ny = 1.0, 0.0
                d = 0.0
            else:
                d = sqrt(d2)
                if d >= sumR:
                    continue
                nx = dx / d
                ny = dy / d

            # overlap depth
            overlap = sumR - d

            # relative velocity along normal
            rvx = V[j,0] - V[i,0]
            rvy = V[j,1] - V[i,1]
            rvn = rvx*nx + rvy*ny

            # normal force (spring - damper), impulse over dt
            Fn = k*overlap - c*rvn
            J  = Fn * dt  # impulse magnitude

            # apply equal & opposite velocity changes
            V[i,0] -= (J / M[i]) * nx
            V[i,1] -= (J / M[i]) * ny
            V[j,0] += (J / M[j]) * nx
            V[j,1] += (J / M[j]) * ny

            # small mass-weighted positional correction (COM preserved)
            mi = M[i]; mj = M[j]
            inv_msum = 1.0 / (mi + mj)
            move_i = beta * overlap * (mj * inv_msum)
            move_j = beta * overlap * (mi * inv_msum)
            P[i,0] -= move_i * nx
            P[i,1] -= move_i * ny
            P[j,0] += move_j * nx
            P[j,1] += move_j * ny

    # Write back
    for i in range(n):
        p = particles[i]
        p.position[0] = P[i,0]
        p.position[1] = P[i,1]
        p.speed[0]    = V[i,0]
        p.speed[1]    = V[i,1]
