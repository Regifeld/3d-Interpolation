'''
Created on Nov 25, 2013

@author: Temporary
'''
import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm
from neural_network import *


def rbf_interpolation(data_file, grid_x = 200, grid_y = 200):
    ##############################################
    #scipy interpolator (Radial basis function)
    with open(data_file, 'r') as f:
        x = []
        y = []
        z = []
        r = []
        g = []
        b = []
        for line in f:
            vertex = str(line).replace('\n', '').split(',')
            x.append(float(vertex[0]))
            y.append(float(vertex[1]))
            z.append(float(vertex[2]))
            r.append(float(vertex[3]))
            g.append(float(vertex[4]))
            b.append(float(vertex[5]))                    
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    r = np.asarray(r)
    g = np.asarray(g)
    b = np.asarray(b)
    print("Interpolating")
    #want to interpolate scattered data into mesh grid of size max_x by max_y
    GRID_X = grid_x
    GRID_Y = grid_y
    tx = np.linspace(0, GRID_X - 1, GRID_X)
    ty = np.linspace(0, GRID_Y - 1, GRID_Y)
    XI, YI = np.meshgrid(tx, ty)
    #INTERPOLATE VALUES
    rbf = Rbf(x, y, z, epsilon = 2)
    ZI = rbf(XI, YI)
    rbf = Rbf(x, y, r, epsilon = 2)
    RI = rbf(XI, YI)
    rbf = Rbf(x, y, g, epsilon = 2)
    GI = rbf(XI, YI)
    rbf = Rbf(x, y, b, epsilon = 2)
    BI = rbf(XI, YI)
    print("Writing results to file")
    data = []
    for xi in xrange(0, GRID_X):
        data.append([])
        for yi in xrange(0, GRID_Y):
            z_val = ZI[xi][yi]
            r_val = RI[xi][yi]
            g_val = GI[xi][yi]
            b_val = BI[xi][yi]
            #generate surface description from broken image
            data[xi].append([z_val, r_val, g_val, b_val])
    
    out_path = data_file.split('/')[-1].split('.')[0]
    out_path = out_path.replace('_scattered', '')
    out_path = "data/" + str(out_path)
    data = np.asarray(data)
    data = np.fliplr(data)
    data = np.rot90(data)
    #Write out the numpy surface description
    np.save(str(out_path) + '_rbf_interpolated.npy', data)
    print("DONE")
    #n = plt.normalize(0., 200)
    #plt.subplot(1, 1, 1)
    #plt.pcolor(XI, YI, ZI)
    #plt.scatter(x, y, 100, z)
    #plt.title('RBF interpolation - multiquadrics')
    #plt.xlim(0, 200)
    #plt.ylim(0, 200)
    #plt.colorbar()
    #plt.show()
    
def neural_network_interpolation(data_file, grid_size = 200):
    vertices = []
    with open(data_file, 'r') as f:
        for line in f:
            vertex = str(line).replace('\n', '').split(',')
            x = float(vertex[0])
            y = float(vertex[1])
            z = float(vertex[2])
            r = float(vertex[3])
            g = float(vertex[4])
            b = float(vertex[5])
            vertices.append([x, y, z, r, g, b])
    #initialize neural network
    network = NeuralNetwork()
    #train the neural network
    network.train(vertices, 2000, 0.25)
    surface = []
    #interpolate the grid using trained network
    for i in xrange(0, grid_size):
        surface.append([])
        for j in xrange(0, grid_size):
            output = network.calculate(x = i, y = j)
            surface[i].append(output)
            
    out_path = data_file.split('/')[-1].split('.')[0]
    out_path = out_path.replace('_scattered', '')
    out_path = "data/" + str(out_path)
    surface = np.asarray(surface)
    #Write out the numpy surface description
    np.save(str(out_path) + '_nn_interpolated.npy', surface)
    
def shepards_interpolation(data_file, grid_x = 200, grid_y = 200, power = 5):
    GRID_X = grid_x
    GRID_Y = grid_y
    #Parse data file and build x, y, z, r, g, b np arrays  
    with open(data_file, 'r') as f:
        x = []
        y = []
        z = []
        r = []
        g = []
        b = []
        for line in f:
            vertex = str(line).replace('\n', '').split(',')
            x.append(float(vertex[0]))
            y.append(float(vertex[1]))
            z.append(float(vertex[2]))
            r.append(float(vertex[3]))
            g.append(float(vertex[4]))
            b.append(float(vertex[5]))
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    r = np.asarray(r)
    g = np.asarray(g)
    b = np.asarray(b)
    
    #import pdb; pdb.set_trace()
    
    #want to interpolate scattered data into mesh grid of size max_x by max_y
    #Initialize grid
    surface = np.zeros((GRID_X, GRID_Y, 4))
    for xi in xrange(0, GRID_X):
        for yi in xrange(0, GRID_Y):
            idx = np.logical_and(x == xi, y == yi)
            if np.any(idx):            
                surface[xi, yi, 0] = z[idx][0]
                surface[xi, yi, 1] = r[idx][0]
                surface[xi, yi, 2] = g[idx][0]
                surface[xi, yi, 3] = b[idx][0]
            else:
                #Calculate distance from current point to all other points in the cloud
                dist = ((xi - x)**2 + (yi - y)**2)**0.5
                #Calculate the weights
                w = 1.0/(dist**power)
                #Calculate interpolated value(z, r, g, b) for current grid cell
                #Z        
                u = np.sum( (w*z)/w.sum() )              
                surface[xi,yi,0] = u      
                #r
                u = np.sum((w*r)/w.sum())
                surface[xi,yi,1] = u
                #g
                u = np.sum((w*g)/w.sum())
                surface[xi,yi,2] = u
                #b
                u = np.sum((w*b)/w.sum())
                surface[xi,yi,3] = u        
    
    out_path = data_file.split('/')[-1].split('.')[0]
    out_path = "data/" + str(out_path)
    out_path = out_path.replace("_scattered", "")
    #Write out the numpy surface description
    np.save(str(out_path) + '_shepard_interpolated.npy', surface)

    
if __name__ == "__main__":
    data_file = raw_input("Data file to interpolate: ")
    #make sure the file is solid (mostly)
    try:
        f = open(data_file)
        if (data_file.split('.')[-1] != 'data'):
            print("Invalid file type!")
            exit(1)
    except:
        print("Invalid file path!")
        exit(1)
    else:
        f.close()
    #Give the options
    print("Select an interpolation mode (1, 2, 3)")
    print("1: rbf\n2: neural network (you really don't want to do this)\n3: Shepard's")
    mode = raw_input("mode: ")
    if (mode == '1'):
        rbf_interpolation(data_file , 200, 200)
    elif (mode == '2'):
        neural_network_interpolation(data_file, 200)
    elif (mode == '3'):
        shepards_interpolation(data_file, 200, 200, 3)
    else:
        print("Invalid selection")
    




