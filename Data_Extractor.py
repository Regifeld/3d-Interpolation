'''
Created on Nov 22, 2013

@author: alalejini
'''
from PIL import Image
import numpy as np

def getZValFromImage(z_case = False, r = None, g = None, b = None):
    if (z_case == False):
        return 0
    else:
        return (r + b + g)/3.0
    
#Extracts vertices from an image and saves it in a file usable by out plotting tool
def fromImage(file_path, gen_z = False):
    #Open file using PIL
    img = Image.open(file_path)
    #Grab pixel data from image and load into numpy array
    img_data = np.array(img.getdata()).reshape(img.size[0], img.size[1], 3)
    vertices = ""
    for x in xrange(0, len(img_data)):
        for y in xrange(0, len(img_data[x])):
            r = img_data[x][y][0]
            g = img_data[x][y][1]
            b = img_data[x][y][2]
            #generate a z value
            z = getZValFromImage(gen_z)
            vertices += str(x) + "," + str(y) + "," + str(z)  + "," + str(r) + "," + str(g) + "," + str(b) + "\n"
    
    out_path = file_path.split('/')[-1].split('.')[0]
    out_path = "data/" + str(out_path) + ".data"
    out_file = open(out_path, 'w')
    out_file.write(vertices)
    out_file.close()
    
if __name__ == "__main__":
    fromImage('images/tommy.jpg', False)