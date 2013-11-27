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
    
if __name__ == "__main__":
    img_file = 'images/terrain.jpg'
    cloudFromImage(img_file, True)
    surfaceDescriptionFromImage(img_file)
#    surfaceDescriptionFromFunction(200)
    