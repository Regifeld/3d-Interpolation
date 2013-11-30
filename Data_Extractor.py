'''
Created on Nov 22, 2013

@author: alalejini
'''
from PIL import Image
import numpy as np
import math

def getZValFromImage(z_case = False, r = None, g = None, b = None):
    if (z_case == False):
        return 1
    else:
        return ((r + b + g) * 255)/3.0
#Extracts vertices from an image and saves it in a file usable by out plotting tool
def cloudFromImage(file_path, gen_z = False):
    #Open file using PIL
    img = Image.open(file_path)
    #Grab pixel data from image and load into numpy array
    img_data = np.asarray(img)
    img_data = np.rot90(np.rot90(np.rot90(img_data)))

    vertices = ""
    for x in xrange(0, len(img_data)):
        for y in xrange(0, len(img_data[x])):
            r = img_data[x][y][0]/255.0
            g = img_data[x][y][1]/255.0
            b = img_data[x][y][2]/255.0
            #generate a z value
            z = getZValFromImage(gen_z, r, g, b)
            vertices += str(x) + "," + str(y) + "," + str(z)  + "," + str(r) + "," + str(g) + "," + str(b) + "\n"
    
    out_path = file_path.split('/')[-1].split('.')[0]
    out_path = "data/" + str(out_path)
    out_file = open(str(out_path) + '.data', 'w')
    out_file.write(vertices)
    out_file.close()

    
def surfaceDescriptionFromImage(file_path):
    #Open file using PIL
    img = Image.open(file_path)
    #Grab pixel data from image and load into numpy array
    img_data = np.asarray(img)
    surface = []
    for x in xrange(0, len(img_data)):
        surface.append([])
        for y in xrange(0, len(img_data[x])):
            r = img_data[x][y][0]/255.0
            g = img_data[x][y][1]/255.0
            b = img_data[x][y][2]/255.0
            #generate a z value
            z = getZValFromImage(True, r, g, b)
            surface[x].append([z, r, g, b])
    
    out_path = file_path.split('/')[-1].split('.')[0]
    out_path = "data/" + str(out_path)
    surface = np.asarray(surface) 
    #gross
    surface = np.rot90(np.rot90(np.rot90(surface)))
    np.save(str(out_path) + '.npy', surface)

#create a surface description from z(x, y) = sin(x)cos(y)
def surfaceDescriptionFromFunction(grid_size = 200):
    surface = []
    vertices = ""
    for x in xrange(0, grid_size):
        surface.append([])
        for y in xrange(0, grid_size):
            f = math.sin(x) + math.cos(y)
            c1 = y/float(grid_size)
            c2 = x/float(grid_size)
            c3 = f/2
            r = float(abs(c1))
            b = float(abs(c2))
            g = float(abs(c3))
            z = f * 100
            surface[x].append([z, r, g, b])
            vertices += str(x) + "," + str(y) + "," + str(z)  + "," + str(r) + "," + str(g) + "," + str(b) + "\n"

    out_path = "function"
    out_path = "data/" + str(out_path)
    out_file = open(str(out_path) + '.data', 'w')
    out_file.write(vertices)
    out_file.close()
    surface = np.asarray(surface)
    np.save(str(out_path) + '.npy', surface)
    
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
    #Gross and janky input logic
    #Grab file input
    img_file = str(raw_input("Enter image path: "))
    #make sure the file is solid
    try:
        f = open(img_file)
    except:
        print("Invalid file path!")
        exit(1)
    else:
        f.close()
    #Point cloud?
    response = str(raw_input("Generate point cloud? (y or n): "))
    if (response.lower() == 'y'):
        print("Generating...")
        cloudFromImage(img_file, True)
        print("Done")
        #Generate sparse point cloud?
        response = str(raw_input("Generate sparse point cloud? (y or n): "))
        if (response.lower() == 'y'):
            print("Generating...")
            data_file = img_file.split('.')[0] + str('.data')
            data_file = "data/" + data_file.split('/')[-1]
            scatter_data(data_file, 7000)
            print("Done")
        elif (response.lower() != 'n'):
            print("Invalid response!")
    elif (response.lower() != 'n'):
        print("Invalid response!")
    #Surface descrip?
    response = str(raw_input("Generate surface description? (y or n): "))
    if (response.lower() == 'y'):
        print("Generating...")
        surfaceDescriptionFromImage(img_file)
        print("Done")
    elif (response.lower() != 'n'):
        print("Invalid response!")

    