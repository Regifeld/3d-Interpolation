'''
Created on Nov 25, 2013

@author: Temporary
'''
import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm

data_file ="data/tiny_g500.data"

##############################################
#scipy interpolator (Radial basis function)
vertices = []
with open(data_file, 'r') as f:
    for line in f:
        vertex = str(line).replace('\n', '').split(',')
        #Create 4 vertices from single input vertex (create a square)
        x = float(vertex[0])
        y = float(vertex[1])
        z = float(vertex[2])
        r = float(vertex[3])
        g = float(vertex[4])
        b = float(vertex[5])
        #Add generated vertices from point
        #top face
        vertices.append([x, y, z, r, g, b])
        
vertices = np.asarray(vertices)
#scattered data
np.random.shuffle(vertices)
NUM_POINTS = 7000
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
print("Interpolating")
#want to interpolate scattered data into mesh grid of size max_x by max_y
GRID_W = 200
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
out_path = "data/" + str(out_path)
#Write out the numpy surface description
np.save(str(out_path) + '_interpolated.npy', np.asarray(data))
#Write out the point cloud
out_file = open(str(out_path) + '_scattered.data', 'w')
out_file.write(vertices_str)
out_file.close()
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




