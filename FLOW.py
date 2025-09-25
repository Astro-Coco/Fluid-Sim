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



class Bin:
    def __init__(self,x,y):
        self.x = 0
        self.y = 0
        self.density = 1
        self.up = 1
        self.down = 1
        self.right = 1
        self.left = 1
        self.flows = [self.up,self.down,self.right,self.left]
        self.parts = []
        self.first = True
    
    def flow(self):
        max_flow = abs(max(self.flows))
        if self.first:
            self.first = False
        else:
            if max_flow is self.up:
                for part in self.parts:
                    part.speed[1] += max_flow


            if max_flow is self.down:
                for part in self.parts:
                    part.speed[1] -= max_flow


            if max_flow is self.right:
                for part in self.parts:
                    part.speed[0] += max_flow


            if max_flow is self.left:
                for part in self.parts:
                    part.speed[0] -= max_flow





class Bins:
    def __init__(self, side_bins):
        self.side_bins = int(side_bins)
        self.bins = np.ndarray(shape= (self.side_bins, self.side_bins),dtype = Bin)
        for i in range(self.side_bins):
            for j in range(self.side_bins):

                self.bins[i,j] = Bin(x = i, y = j)

    def compute_flows(self):
        factor = 260.1
        for i in range(self.side_bins):
            for j in range(self.side_bins):

                bin = self.bins[i,j]
                bin.density = len(bin.parts)
                density = bin.density

                if j-1 >= 0:
                    bin.down = (len(self.bins[i,j-1].parts)-density)*factor 
                else:
                    bin.down =  -10


                if j+1 <= self.side_bins-1:  

                    bin.up = (len(self.bins[i,j+1].parts)-density)*factor
                else:
                    bin.up = -10


                if i+1 <= self.side_bins-1:    
                    bin.right = (len(self.bins[i+1,j].parts)-density)*factor
                else:
                    bin.right = -10


                if i-1 >= 0:   
 
                    bin.left = (len(self.bins[i-1,j].parts)-density)*factor
                else:
                    bin.left = -10

                bin.flows = [bin.up, bin.down, bin.right, bin.left]
 
                bin.flow()

        for i in range(self.side_bins):
            for j in range(self.side_bins):
                bin = self.bins[i,j]
                bin.parts = []
                

#perfo = performance()
class Flow:

    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
        self.bins = 25
        self.side_bins = int(math.sqrt(self.bins))
        self.BINS = Bins(self.side_bins)
        #perfo.time('compute in group')
        #perfo.time('check collision')





    def compute_flow(self, all_parts):

        x_box = self.x / self.side_bins
        y_box = self.y / self.side_bins
        for particle in all_parts:
            pos_x = particle.position[0]
            pos_y = particle.position[1]
            
            x_bin = pos_x // x_box
            y_bin = pos_y // y_box

            self.BINS.bins[int(x_bin),int(y_bin)].parts.append(particle)


        self.BINS.compute_flows()

  


        