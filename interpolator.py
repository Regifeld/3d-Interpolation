'''
Created on Nov 25, 2013

@author: Temporary
'''
import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm


def rbf_interpolation(data_file, grid_size = 200):
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
    GRID_W = grid_size
    ti = np.linspace(0, GRID_W - 1, GRID_W)
    XI, YI = np.meshgrid(ti, ti)
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
    for xi in xrange(0, GRID_W):
        data.append([])
        for yi in xrange(0, GRID_W):
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
    
def neural_network_interpolation(data_file):
    pass

#this function takes specified number of samples from given data file and writes the scattered data to a new file
#if samples is too high(7000 is about 10-12gb on my system), memory error will occur!
#samples must be lower than the number of vertices in the original data set!
def scatter_data(data_file, samples = 0):
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
            
    vertices = np.asarray(vertices)
    #scatter data
    np.random.shuffle(vertices)
    NUM_POINTS = samples
    x = vertices[:NUM_POINTS, 0]
    y = vertices[:NUM_POINTS, 1]
    z = vertices[:NUM_POINTS, 2]
    r = vertices[:NUM_POINTS, 3]
    g = vertices[:NUM_POINTS, 4]
    b = vertices[:NUM_POINTS, 5]
    print("Building point cloud of scattered data")
    #build point cloud of scattered data
    vertices_str = ""
    for p in xrange(0, NUM_POINTS):
        x_val = x[p]
        y_val = y[p]
        z_val = z[p]
        r_val = r[p]
        g_val = g[p]
        b_val = b[p]
        #generate point cloud from broken image
        vertices_str += str(x_val) + "," + str(y_val) + "," + str(z_val)  + "," + str(r_val) + "," + str(g_val) + "," + str(b_val) + "\n"
        
    out_path = data_file.split('/')[-1].split('.')[0]
    out_path = "data/" + str(out_path)
    #Write out the point cloud
    out_file = open(str(out_path) + '_scattered.data', 'w')
    out_file.write(vertices_str)
    out_file.close()
    
if __name__ == "__main__":
    data_file ="data/tiny_g500.data"
    #scatter_data(data_file, 7000)
    rbf_interpolation("data/tiny_g500_scattered.data")




