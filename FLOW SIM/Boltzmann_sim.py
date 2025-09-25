import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plot_every = 50
frames = []

def distance(x1,y1,x2,y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def main():
    Nx = 300
    Ny = 300
    tau = .53 #.53 initial
    Nt = 30000

    #lattice speeds and weights
    NL = 9
    #Discrete velocities (signs of speed)
    cxs = np.array([0, 0, 1, 1,  1,  0, -1, -1, -1])
    cys = np.array([0, 1, 1, 0, -1, -1, -1, 0,   1])

    weights = np.array([4/9, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36])

    #Initial conditions
    F = np.ones((Ny,Nx,NL)) + .01*np.random.randn(Ny,Nx, NL)

    #For all Ny, Nx, set the 3 values to a constant
    F[:, :, 3] = 3

    cylinder = np.full((Ny,Nx), False)
    radius_cylinder = 20

    for y in range(0, Ny):
        for x in range(0, Nx):
            if (distance(Nx//4, Ny//2, x, y) < radius_cylinder) :
                cylinder[y][x] = True

    #main loop
    for it in range(Nt):
        if (it%plot_every == 0):
            plt.pause(0.01)
            plt.cla()
            
        
        F[:,-1, [6,7,8]] = F[:,-2, [6,7,8]]
        F[:,0, [2,3,4]] = F[:,1, [2,3,4]]

        #Propagate speed in every direction, for all cells, in all directions
        for i, cx, cy, in zip(range(NL),cxs,cys):
            F[:, :, i] = np.roll(F[:, :, i], cx, axis = 1)
            F[:, :, i] = np.roll(F[:, :, i], cy, axis = 0)

        bndryF = F[cylinder, :]
        bndryF = bndryF[:, [0,5,6,7,8,1,2,3,4]]

        rho = np.sum(F,2) #Density
        ux = np.sum(F*cxs, 2)/rho #x momentum
        uy = np.sum(F*cys, 2)/rho #y momentum

        F[cylinder, :] = bndryF
        ux[cylinder] = 0
        uy[cylinder] = 0

        Feq = np.zeros(F.shape)

        for i,cx,cy,w in zip(range(NL),cxs, cys, weights):
            Feq[:, :, i] = rho*w*(
                1 + 3* (cx*ux + cy*uy) + 9 * (cx*ux + cy*uy)**2 /2 - 3*(ux**2 + uy**2)/2
            )

        F = F + -(1/tau)*(F-Feq)

        if (it%plot_every == 0):
            print(it)
            dfydx = ux[2:, 1:-1] - ux[0:-2, 1:-1]
            dfxdy = uy[1:-1, 2:] - uy[1:-1, 0:-2]

            curl = dfydx - dfxdy

            plt.imshow(curl, cmap='bwr')
            
            
            



if __name__ == '__main__':
    main()