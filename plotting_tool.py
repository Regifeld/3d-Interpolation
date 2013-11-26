#!/usr/bin/env pythonw
# Transform assignment
# Name: Alex Lalejini
# NetID: aml386
from __future__ import division

import platform
from ctypes import * 

import pyglet

# Required for my darwin patch
if platform.system() == 'Darwin':
    pyglet.options['shadow_window'] = False

from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *
import array
import numpy as np
import math

class Window(pyglet.window.Window):

    def __init__(self):
        # Create an OpenGL 3.2 context; initialize with that
        config = pyglet.gl.Config(double_buffer = True, 
                                  depth_size = 24, 
                                  major_version=3, 
                                  minor_version=2, 
                                  forward_compatible = True)

        super(Window, self).__init__(caption ="Plotting Tool",
                                     width = 600, height = 600, 
                                     resizable = True,
                                     config = config)
        
        #Used to store c style array of interweaved color and vertex data
        self.vertexData = None
        self.triIndices = None
        self.numIndices = 0
        #Used to store list of vertices from original data file
        self.vertices = None
        #self.parseData('data/tiny_g500.data')
        #self.parseData('data/tiny_g500_scattered.data', mode = 'POINT_CLOUD')
        self.parseData('data/tiny_g500_interpolated.npy', mode = 'TRIANGLE_MESH')
        #self.parseData('data/tommy.npy', mode = 'TRIANGLE_MESH')
        
        ####################################################################################
        #----------TO BE CHANGED----------.
        self.screen_width = 600.0
        self.screen_height = 600.0
        self.aspect = float(self.screen_width)/self.screen_height
        near = 0.1
        far = 100.0
        #store initial screen values
        #Galaxy values
        x_max = 220
        x_min = 0
        y_max = 220
        y_min = 0
        #Tommy values
#        x_max = 300
#        x_min = 0
#        y_max = 400
#        y_min = 0
        z_max = 300.0 #near
        z_min = -300.0 #far
        #Same as viewer location (p_0)
        e_x = 0
        e_y = 0
        e_z = 290
        
        
        
        self.local_to_world = np.array([[1, 0, 0, 0], 
                                          [0, 1, 0, 0], 
                                          [0, 0, 1, 0], 
                                          [0, 0, 0, 1]])
        
        #rotate obj locally by 90 degrees
        self.local_to_world = np.dot(self.translate(x = 220, y = 220, z = 0), self.rot_z(180))
        #self.local_to_world = np.dot(self.translate(x = 0, y = 220, z = 0), self.rot_z(270))
        #self.local_to_world = np.dot(self.local_to_world, )
        
        #double check this transform
        self.world_to_camera = np.array([[1, 0, 0, 0], 
                                          [0, 1, 0, 0], 
                                          [0, 0, 1, 0], 
                                          [0, 0, 0, 1]])
        
        self.eye_transform = np.array([[1, 0, 0, -e_x], 
                                       [0, 1, 0, -e_y], 
                                       [0, 0, 1, -e_z], 
                                       [0, 0, 0, 1]])

        
        self.p_ortho = np.array([[2/(x_max - x_min), 0, 0, -(x_max + x_min)/(x_max - x_min)], 
                                 [0, 2/(y_max - y_min), 0, -(y_max + y_min)/(y_max - y_min)],
                                 [0, 0, -2/(z_min - z_max), -(z_min + z_max)/(z_min - z_max)], 
                                 [0, 0, 0, 1]])
#        self.p_ortho = np.array([[far/self.aspect, 0, 0, 0],
#                               [0, far, 0, 0],
#                               [0, 0, (far + near)/(near - far), (2*far*near)/(near - far)],
#                               [0, 0, -1, 0]])
                

        
        self.transform = np.array([[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, 0], 
                                   [0, 0, 0, 1]])
        ####################################################################################
           
        # Initialize GL state: Enable depth testing
        glClearColor(0, 0, 0, 0)
        glEnable(GL_DEPTH_TEST)

        # Initialize OpenGL data         
        self.createBuffers()
        self.createShaders()
        
        
    #Parses given data file, loads data into self.vertexData as c style array
    #Assumes file structure: X,Y,Z,R,G,B\n
    def parseData(self, data_file, mode = None):
        #stores vertices read in from file (vertices and color interweaved)
        vertices = []
        indices = []
        if (mode == "POINT_CLOUD"):
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
                    d = 0.5
                    #Add generated vertices from point
                    #top face
                    vertices.append([x - d, y - d, z + d, r, g, b])
                    p0 = len(vertices) - 1
                    vertices.append([x + d, y - d, z + d, r, g, b])
                    p1 = len(vertices) - 1
                    vertices.append([x + d, y + d, z + d, r, g, b])
                    p2 = len(vertices) - 1
                    vertices.append([x - d, y + d, z + d, r, g, b])
                    p3 = len(vertices) - 1
                    #bottom face
                    vertices.append([x - d, y - d, z - d, r, g, b])
                    p4 = len(vertices) - 1
                    vertices.append([x + d, y - d, z - d, r, g, b])
                    p5 = len(vertices) - 1
                    vertices.append([x + d, y + d, z - d, r, g, b])
                    p6 = len(vertices) - 1
                    vertices.append([x - d, y + d, z - d, r, g, b])
                    p7 = len(vertices) - 1
                    #index the geometry (USE WHEN USING TRIANGLES)
                    #FRONT FACE
                    indices.append([p0, p1, p3])
                    indices.append([p2, p3, p1])
                    #BACK FACE
                    indices.append([p4, p5, p7])
                    indices.append([p6, p7, p5])
                    #TOP FACE
                    indices.append([p3, p7, p2])
                    indices.append([p6, p2, p7])
                    #BOTTOM FACE
                    indices.append([p0, p4, p1])
                    indices.append([p5, p1, p4])
                    #RIGHT FACE
                    indices.append([p1, p5, p2])
                    indices.append([p6, p2, p5])
                    #LEFT FACE
                    indices.append([p7, p4, p3])
                    indices.append([p0, p3, p4])
                    #USE WHEN USING POINTS
#                    vertices.append([x, y, z, r, g, b])
#                    indices.append(len(vertices) - 1)
        #Requires numpy array of vertices of the form [x][y][z, r, g, b]
        elif (mode == "TRIANGLE_MESH"):
            surface_descrip = np.load(data_file)
            index_ref = []
            #generate vertices and an index look up table
            for x in xrange(0, len(surface_descrip)):
                index_ref.append([])
                for y in xrange(0, len(surface_descrip[x])):
                    z = surface_descrip[x][y][0]
                    r = surface_descrip[x][y][1]
                    g = surface_descrip[x][y][2]
                    b = surface_descrip[x][y][3]
                    vertices.append([x, y, z, r, g, b])
                    index_ref[x].append(len(vertices) - 1)
            for x in xrange(0, len(surface_descrip) - 1):
                for y in xrange(0, len(surface_descrip[x]) - 1):
                    p1 = index_ref[x][y]
                    p2 = index_ref[x][y + 1]
                    p3 = index_ref[x + 1][y + 1]
                    p4 = index_ref[x + 1][y]
                    indices.append([p2, p1, p3])
                    indices.append([p4, p3, p1])
                           
        #Build vertices array          
        vertices = np.array(vertices).flatten()
        self.vertexData = (GLfloat * vertices.size)()
        for i in xrange(0, vertices.size):
            self.vertexData[i] = vertices[i]
        #Build indices array 
        indices = np.array(indices).flatten()
        self.numIndices = indices.size
        self.triIndices = (GLuint * indices.size)()
        for i in xrange(0, indices.size):
            self.triIndices[i] = indices[i]
    
    ##################################################################
    # Buffer management
    
    def createBuffers(self):
        #holds the arrayID of our vertex array given by openGL
        self.arrayID = GLuint()
        #n = 1 (we want 1 vertex array object)
        glGenVertexArrays(1, byref(self.arrayID))
        glBindVertexArray(self.arrayID)
                  
        self.bufferID = GLuint()
        glGenBuffers(1, byref(self.bufferID))
        #inits the buffer as a vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferID)
        #load data into buffer.  
        glBufferData(GL_ARRAY_BUFFER, sizeof(self.vertexData), self.vertexData, GL_STATIC_DRAW)
        
        #Associate the buffer data with the vertex array.  Ignore all the unused stuff
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(GLfloat * 6), 0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(GLfloat * 6), sizeof(GLfloat * 3))
        #turn on the arrays for OpenGL
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        #Now, create index buffers
        self.indexBufferID = GLuint()
        glGenBuffers(1, self.indexBufferID)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBufferID)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(self.triIndices), self.triIndices, GL_STATIC_DRAW)
        
    def destroyBuffers(self):
        #Make the vertex attribute arrays inactive
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        
        #unbind the buffer memory and delete it
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glDeleteBuffers(1, byref(self.bufferID))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glDeleteBuffers(1, self.indexBufferID)
        
        #unbind the vertex array and delete it
        glBindVertexArray(0)
        glDeleteVertexArrays(1, byref(self.arrayID))
    
    ##################################################################
    # Shader management
    
    def createShaders(self):
        # Create, load, and compile the vertex shader.
        # Requires an ugly ctypes cast, unfortunately 
        with open('plot.vert') as vertexFile:
            vertexShader = vertexFile.read()
        self.vertexShaderID = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertexShaderID, 1, 
                       cast(pointer(c_char_p(vertexShader)),
                            POINTER(POINTER(c_char))),
                       None)
        glCompileShader(self.vertexShaderID)
        
        # Print an error log
        length = GLsizei()
        log = (c_char_p)(" " * 1023)
        glGetShaderInfoLog(self.vertexShaderID, 1023, byref(length), log)
        print "Vertex Log:", log.value
        
        # Create, load, and compile the fragment shader
        # Requires an ugly ctypes cast, unfortunately 
        with open('plot.frag') as fragFile:
            fragShader = fragFile.read()
        self.fragShaderID = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragShaderID, 1, 
                       cast(pointer(c_char_p(fragShader)), 
                            POINTER(POINTER(c_char))),
                       None)
        glCompileShader(self.fragShaderID)
        
        # Print an error log
        length = GLsizei()
        log = (c_char_p)(" " * 1023)
        glGetShaderInfoLog(self.fragShaderID, 1023, byref(length), log)
        print "Frag Log:", log.value
        
        # Create the final program
        self.programID = glCreateProgram()
        glAttachShader(self.programID, self.vertexShaderID)
        glAttachShader(self.programID, self.fragShaderID)
        
        # Associate the vertex shader with the vertex attributes:
        #   Attrib array 0 stores the vertices
        glBindAttribLocation(self.programID, 0, "position")
        glBindAttribLocation(self.programID, 1, "inColor")
        
        
        # Link and enable the program
        glLinkProgram(self.programID)
        glUseProgram(self.programID)
        
        # TODO: Get and set the uniform variable values as needed
        # Store their locations as member variables for later
        self.mvpTransformLoc = glGetUniformLocation(self.programID, "mvpTransform")
        
    def destroyShaders(self):
        # Disable the current program
        glUseProgram(0)
     
        # Detach the shaders
        glDetachShader(self.programID, self.vertexShaderID)
        glDetachShader(self.programID, self.fragShaderID)
        
        # Destroy the shaders
        glDeleteShader(self.vertexShaderID)
        glDeleteShader(self.fragShaderID)
        
        # Destroy the program
        glDeleteProgram(self.programID)
        
    ##################################################################
    # Window events
    
    # Window closed
    def on_close(self):
        self.destroyShaders()
        self.destroyBuffers()
        super(Window, self).on_close()
    
    # Window resized
    def on_resize(self, width, height):
        # Update the viewport and associated shader variable
        gl.glViewport(0, 0, width, height)

        # Always redraw
        self.on_draw()

    # Draw the window
    def on_draw(self):
        # Handles glClear calls
        self.clear()
        #BUILD MV Matrix
        mvMatrix = np.dot(self.local_to_world, self.transform)
        mvMatrix = np.dot(self.world_to_camera, mvMatrix)
        mvMatrix = np.dot(self.eye_transform, mvMatrix)
#        mvMatrix = np.dot(self.world_to_camera, self.local_to_world)
#        mvMatrix = np.dot(self.eye_transform, mvMatrix)
#        mvMatrix = np.dot(self.transform, mvMatrix)        
        
        #apply ortho perspective matrix to model view matrix
        mvpMatrix = np.dot(self.p_ortho, mvMatrix)
        mvpMatrix = mvpMatrix.transpose()        
        mvpTransform = (GLfloat * 16)()
        #Janky way to build our matrix
        for i in xrange(0, 16):
            mvpTransform[i] = mvpMatrix.flatten()[i]
           
        glUniformMatrix4fv(self.mvpTransformLoc, 1, GL_FALSE, *([mvpTransform]))
        glDrawElements(GL_TRIANGLES, self.numIndices, GL_UNSIGNED_INT, None)

    
    def rot_x(self, theta = 10):
            #Rotate about the local x axis
            theta = math.radians(theta)
            rotate = np.array([[1, 0, 0, 0], 
                               [0, math.cos(theta), -math.sin(theta), 0], 
                               [0, math.sin(theta), math.cos(theta), 0], 
                               [0, 0, 0, 1]])
            return rotate
            #self.transform = np.dot(self.transform, rotate)
            
    def rot_y(self, theta = 10):
            theta = math.radians(theta)
            rotate = np.array([[math.cos(theta), 0, math.sin(theta), 0], 
                               [0, 1, 0, 0], 
                               [-math.sin(theta), 0, math.cos(theta), 0], 
                               [0, 0, 0, 1]])
            return rotate
            
    def rot_z(self, theta = 10):
            theta = math.radians(theta)
            #rotate on local z axis
            rotate = np.array([[math.cos(theta), -math.sin(theta), 0, 0], 
                               [math.sin(theta), math.cos(theta), 0, 0], 
                               [0, 0, 1, 0], 
                               [0, 0, 0, 1]])
            return rotate
            
    def translate(self, x = 0, y = 0, z = 0):
            translate = np.array([[1, 0, 0, x], 
                                  [0, 1, 0, y], 
                                  [0, 0, 1, z], 
                                  [0, 0, 0, 1]])
            return translate
            
    def reset(self):
        # reset transformation matrix to identity matrix
        self.transform = np.array([[1, 0, 0, 0], 
                                   [0, 1, 0, 0], 
                                   [0, 0, 1, 0], 
                                   [0, 0, 0, 1]])
    def on_key_release(self, keycode, modifiers):
        
        if keycode == key.BRACKETLEFT:
            self.transform = np.dot(self.transform, self.rot_z(-5))
        elif keycode == key.BRACKETRIGHT:
            self.transform = np.dot(self.transform, self.rot_z(5))
        elif keycode == key.RIGHT:
            self.transform = np.dot(self.transform, self.rot_y(5))
        elif keycode == key.LEFT:
            self.transform = np.dot(self.transform, self.rot_y(-5))
        elif keycode == key.UP:
            self.transform = np.dot(self.transform, self.rot_x(5))
        elif keycode == key.DOWN:
            self.transform = np.dot(self.transform, self.rot_x(-5))
        elif keycode == key.H:
            self.reset()
        elif keycode == key.B:
            #scale
            s = 1.1
            scale = np.array([[s, 0, 0, 0], 
                              [0, s, 0, 0],
                              [0, 0, s, 0], 
                              [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, scale)
        elif keycode == key.Y:
            x = 1
            z = 1
            shear = np.array([[1, x, 0, 0], 
                                               [0, 1, 0, 0], 
                                               [0, z, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        elif keycode == key.X:
            y = 1
            z = 1
            shear =  np.array([[1, 0, 0, 0], 
                                               [y, 1, 0, 0], 
                                               [z, 0, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        elif keycode == key.Z:
            x = 1
            y = 1
            shear = np.array([[1, 0, x, 0], 
                                               [0, 1, y, 0], 
                                               [0, 0, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        # Always redraw after keypress
        elif keycode == key.W:
            #rotate about local x axis
            self.transform = np.dot(self.transform, self.translate(0, 0, 10))
            
        self.on_draw()
    
# Run the actual application
if __name__ == "__main__":
    window = Window()
    pyglet.app.run()