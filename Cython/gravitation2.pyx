# collision_cy.pyx
# cython: boundscheck=False, wraparound=False, initializedcheck=False, nonecheck=False
cimport cython
from libc.math cimport floor, sqrt
import numpy as np
cimport numpy as cnp

@cython.cfunc
@cython.inline
cdef int _clamp_int(int v, int lo, int hi) nogil:
    if v < lo: return lo
    if v > hi: return hi
    return v

@cython.cfunc
@cython.inline
cdef long _pair_key(Py_ssize_t i, Py_ssize_t j, Py_ssize_t n) nogil:
    # store with i > j
    if i < j:
        i, j = j, i
    return <long>(i*n + j)

@cython.cfunc
cdef void _add_bin_pairs(cnp.int32_t[:] idxs, set pairs, Py_ssize_t n):
    cdef Py_ssize_t m = idxs.shape[0]
    cdef Py_ssize_t a, b
    for a in range(m):
        for b in range(a):
            pairs.add(_pair_key(idxs[a], idxs[b], n))

@cython.cfunc
@cython.inline
cdef void _resolve_pair(
    Py_ssize_t i, Py_ssize_t j,
    double[:, :] pos,       # (N,2)
    double[:, :] vel,       # (N,2)
    double[:] size_arr,     # (N,)
    double[:] mass_arr,     # (N,)
    double e,               # restitution [0..1]
    double pc_beta,         # positional-correction scale (0..1)
    double pc_slop          # slop (tolerance) to avoid micro-jitter
) noexcept:
    cdef double dx = pos[j,0] - pos[i,0]
    cdef double dy = pos[j,1] - pos[i,1]
    cdef double r2 = dx*dx + dy*dy
    if r2 == 0.0:
        return

    cdef double r = sqrt(r2)
    cdef double contact = (size_arr[i] + size_arr[j]) * 0.5  # sum of radii
    if r > contact:
        return

    # --- pre-correction normal & approach speed ---
    cdef double nx = dx / r
    cdef double ny = dy / r
    cdef double rvx = vel[j,0] - vel[i,0]
    cdef double rvy = vel[j,1] - vel[i,1]
    cdef double rvn = rvx*nx + rvy*ny

    # --- mass-weighted positional correction (COM preserved) ---
    cdef double pen = contact - r           # penetration depth
    cdef double corr = pc_beta * max(pen - pc_slop, 0.0)
    if corr > 0.0:
        cdef double mi = mass_arr[i]
        cdef double mj = mass_arr[j]
        cdef double inv_msum = 1.0 / (mi + mj)
        cdef double move_i = corr * (mj * inv_msum)
        cdef double move_j = corr * (mi * inv_msum)
        pos[i,0] -= move_i * nx
        pos[i,1] -= move_i * ny
        pos[j,0] += move_j * nx
        pos[j,1] += move_j * ny

    # --- normal impulse (antisymmetric), only if approaching ---
    if rvn < 0.0:
        cdef double mi = mass_arr[i]
        cdef double mj = mass_arr[j]
        # J = -(1+e) rvn / (1/mi + 1/mj)
        cdef double J = -(1.0 + e) * rvn * (mi*mj)/(mi + mj)
        vel[i,0] -= (J/mi) * nx
        vel[i,1] -= (J/mi) * ny
        vel[j,0] += (J/mj) * nx
        vel[j,1] += (J/mj) * ny


def check_collision(particles, double x, double y, double cell_size,
                    double fs=1.3, double e=1.0, bint zero_acc=False,
                    double pc_beta=1.0, double pc_slop=0.01):
    """
    Collision resolution with strict pair de-dup and COM-preserving correction.

    particles : list[Particle] with .position[2], .speed[2], .size, .mass
    x, y      : domain size (for binning)
    cell_size : base particle size for bin estimate
    fs        : bin scale (default 1.3)
    e         : restitution [0..1] (1 elastic)
    zero_acc  : if True, zero p.acc[:] once per call
    pc_beta   : positional-correction strength (0..1], default 1.0
    pc_slop   : tolerance to ignore tiny overlaps (~pixels)
    """
    cdef Py_ssize_t n = len(particles)
    if n == 0:
        return

    positions  = np.empty((n, 2), dtype=np.float64)
    velocities = np.empty((n, 2), dtype=np.float64)
    sizes      = np.empty((n,),    dtype=np.float64)
    masses     = np.empty((n,),    dtype=np.float64)

    cdef double[:, :] pos       = positions
    cdef double[:, :] vel       = velocities
    cdef double[:]     size_arr = sizes
    cdef double[:]     mass_arr = masses

    cdef Py_ssize_t i
    cdef object p
    for i in range(n):
        p = particles[i]
        pos[i,0] = <double>p.position[0]
        pos[i,1] = <double>p.position[1]
        vel[i,0] = <double>p.speed[0]
        vel[i,1] = <double>p.speed[1]
        size_arr[i] = <double>p.size
        mass_arr[i] = <double>p.mass
        if zero_acc and hasattr(p, "acc"):
            p.acc[0] = 0.0
            p.acc[1] = 0.0

    # grid estimate (coarse is fine; correctness does not depend on it)
    cdef int side_bins = <int>( (min(x, y) / (cell_size * fs)) )
    if side_bins < 1:
        side_bins = 1
    cdef double x_box = x / side_bins
    cdef double y_box = y / side_bins

    # build bins (two staggered grids)
    cdef dict bins1 = {}
    cdef dict bins2 = {}
    cdef int xb, yb, bin_id, xb2, yb2, bin_id2

    for i in range(n):
        xb  = _clamp_int(<int>floor(pos[i,0] / x_box), 0, side_bins-1)
        yb  = _clamp_int(<int>floor(pos[i,1] / y_box), 0, side_bins-1)
        bin_id = yb * side_bins + xb
        bins1.setdefault(bin_id, []).append(i)

        xb2 = <int>floor((pos[i,0] - 0.5*x_box) / x_box)
        yb2 = <int>floor((pos[i,1] - 0.5*y_box) / y_box)
        xb2 = _clamp_int(xb2, 0, side_bins-1)
        yb2 = _clamp_int(yb2, 0, side_bins-1)
        bin_id2 = yb2 * side_bins + xb2
        bins2.setdefault(bin_id2, []).append(i)

    # 1) collect UNIQUE pairs from both grids
    cdef set pairs = set()
    cdef cnp.ndarray arr
    cdef cnp.int32_t[:] mv
    for idx_list in bins1.values():
        if len(idx_list) > 1:
            arr = np.asarray(idx_list, dtype=np.int32)
            mv = arr
            _add_bin_pairs(mv, pairs, n)
    for idx_list in bins2.values():
        if len(idx_list) > 1:
            arr = np.asarray(idx_list, dtype=np.int32)
            mv = arr
            _add_bin_pairs(mv, pairs, n)

    # 2) resolve each unique pair exactly once
    cdef long key
    cdef Py_ssize_t I, J
    for key in pairs:
        J = key % n
        I = key // n
        _resolve_pair(I, J, pos, vel, size_arr, mass_arr, e, pc_beta, pc_slop)

    # write back
    for i in range(n):
        p = particles[i]
        p.position[0] = pos[i, 0]
        p.position[1] = pos[i, 1]
        p.speed[0]    = vel[i, 0]
        p.speed[1]    = vel[i, 1]
