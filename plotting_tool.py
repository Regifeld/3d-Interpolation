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
                                     width = 1000, height = 1000, 
                                     resizable = True,
                                     config = config)
        
        #Used to store c style array of interweaved color and vertex data
        self.vertexData = None
        self.triIndices = None
        self.numIndices = 0
        #Used to store list of vertices from original data file
        self.vertices = None
        self.parseData('data/tommy.data')
        
        ####################################################################################
        #----------TO BE CHANGED----------
        #store initial screen values
        x_max = 300.0
        x_min = 0
        y_max = 450.0
        y_min = 0
        z_max = 5.0 #near
        z_min = -5.0 #far
        #Same as viewer location (p_0)
        e_x = 0
        e_y = 0
        e_z = 10

        #double check this transform
        world_cameraTransform = np.array([[1, 0, 0, 0], 
                                          [0, 1, 0, 0], 
                                          [0, 0, 1, 0], 
                                          [0, 0, 0, 1]])
        trans_eyeTransform = np.array([[1, 0, 0, -e_x], 
                                       [0, 1, 0, -e_y], 
                                       [0, 0, 1, -e_z], 
                                       [0, 0, 0, 1]])
        #calculate the model view transform
        self.modelViewTransform = np.dot(world_cameraTransform, trans_eyeTransform)
        
        self.p_ortho = np.array([[2/(x_max - x_min), 0, 0, -(x_max + x_min)/(x_max - x_min)], 
                                 [0, 2/(y_max - y_min), 0, -(y_max + y_min)/(y_max - y_min)],
                                 [0, 0, -2/(z_min - z_max), -(z_min + z_max)/(z_min - z_max)], 
                                 [0, 0, 0, 1]])
        
        self.p_perspective = np.array([[(2 * z_max)/(x_max - x_min), 0,                          -(x_max + x_min)/(x_max - x_min), 0],
                                       [0,                          (2 * z_max)/(y_max - y_min), -(y_max + y_min)/(y_max - y_min), 0],
                                       [0,                          0,                           -(z_min + z_max)/(z_min - z_max), -(2 * z_min * z_max)/(z_min - z_max)],
                                       [0,                          0,                           -1,                               0]])
        
        self.transform = np.array([[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, 0], 
                                   [0, 0, 0, 1]])
        ####################################################################################
           
        # Initialize GL state: Enable depth testing
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)

        # Initialize OpenGL data         
        self.createBuffers()
        self.createShaders()
        
        
    #Parses given data file, loads data into self.vertexData as c style array
    #Assumes file structure: X,Y,Z,R,G,B\n
    def parseData(self, data_file):
        #stores vertices read in from file (vertices and color interweaved)
        vertices = []
        indices = []
        #self.vertices = []
        hs = 0.5 #stores half of length of side
        with open(data_file, 'r') as f:
            i = 0
            for line in f:
                vertex = str(line).replace('\n', '').split(',')
                #Create 4 vertices from single input vertex (create a square)
                x = float(vertex[0])
                y = float(vertex[1])
                z = float(vertex[2])
                r = float(vertex[3])
                g = float(vertex[4])
                b = float(vertex[5])
                index = i * 5
                #TRIANGLE 1
                vertices.append([x - hs, y + hs, z, r, g, b])
                indices.append(index + 0)
                vertices.append([x - hs, y - hs, z, r, g, b])
                indices.append(index + 1)
                vertices.append([x + hs, y + hs, z, r, g, b])
                indices.append(index + 2)
                #TRIANGLE 2
                vertices.append([x + hs, y - hs, z, r, g, b])
                indices.append(index + 3)
                indices.append(index + 2) #Reuse indices
                indices.append(index + 1)
                i += 1
        #Build vertices array          
        vertices = np.array(vertices).flatten()
        self.vertexData = (GLfloat * vertices.size)()
        for i in xrange(0, vertices.size):
            self.vertexData[i] = vertices[i]
        #Build indices array 
        indices = np.array(indices)
        self.numIndices = indices.size
        self.triIndices = (GLshort * indices.size)()
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
        # TODO: Render your geometry. Update any uniforms (e.g., colors,
        # matrices) you may need.
        #apply local modelViewTransform to local transforms
        mvpMatrix = np.dot(self.modelViewTransform, self.transform)
        #apply ortho perspective matrix to model view matrix
        mvpMatrix = np.dot(self.p_ortho, mvpMatrix)
        mvpMatrix = mvpMatrix.transpose()
        mvpTransform = (GLfloat * 16)()
        #Janky way to build our matrix
        for i in xrange(0, 16):
            mvpTransform[i] = mvpMatrix.flatten()[i]
           
        glUniformMatrix4fv(self.mvpTransformLoc, 1, GL_FALSE, *([mvpTransform]))
        glDrawElements(GL_TRIANGLES, self.numIndices, GL_UNSIGNED_SHORT, None)


    def on_key_release(self, keycode, modifiers):
        if keycode == key.RIGHT:
            # TODO: Turn car right
            theta = 10
            theta = math.radians(theta)
            #rotate right on local z axis
            rotate = np.array([[math.cos(theta), -math.sin(theta), 0, 0], 
                               [math.sin(theta), math.cos(theta), 0, 0], 
                               [0, 0, 1, 0], 
                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, rotate)
            # multiply current_transform * rotation_transform            
        elif keycode == key.LEFT:
            # TODO: Turn car left
            theta = -10
            theta = math.radians(theta)
            #rotate right on local z axis
            rotate = np.array([[math.cos(theta), -math.sin(theta), 0, 0], 
                               [math.sin(theta), math.cos(theta), 0, 0], 
                               [0, 0, 1, 0], 
                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, rotate)                        
        elif keycode == key.UP:
            # TODO: Move forward 
            # multiply current_transform * translation_transform
            x = 0
            y = -10
            z = 0
            translate = np.array([[1, 0, 0, x], 
                                  [0, 1, 0, y], 
                                  [0, 0, 1, z], 
                                  [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, translate)
        elif keycode == key.DOWN:
            # TODO: Move backwards
            x = 0
            y = 10
            z = 0
            translate = np.array([[1, 0, 0, x], 
                                  [0, 1, 0, y], 
                                  [0, 0, 1, z], 
                                  [0, 0, 0, 1]])
            # multiply current_transform * translation_transform
            self.transform = np.dot(self.transform, translate)
        elif keycode == key.H:
            # TODO: Reset model transformations
            # reset transformation matrix to identity matrix
            self.transform = np.array([[1, 0, 0, 0], 
                                       [0, 1, 0, 0], 
                                       [0, 0, 1, 0], 
                                       [0, 0, 0, 1]])
        elif keycode == key.B:
            #scale
            s = 2
            scale = np.array([[s, 0, 0, 0], 
                              [0, s, 0, 0],
                              [0, 0, s, 0], 
                              [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, scale)
        elif keycode == key.Y:
            x = 1
            z = 1
            shear = self.transform = np.array([[1, x, 0, 0], 
                                               [0, 1, 0, 0], 
                                               [0, z, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        elif keycode == key.X:
            y = 1
            z = 1
            shear = self.transform = np.array([[1, 0, 0, 0], 
                                               [y, 1, 0, 0], 
                                               [z, 0, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        elif keycode == key.Z:
            x = 1
            y = 1
            shear = self.transform = np.array([[1, 0, x, 0], 
                                               [0, 1, y, 0], 
                                               [0, 0, 1, 0], 
                                               [0, 0, 0, 1]])
            self.transform = np.dot(self.transform, shear)
        # Always redraw after keypress
        self.on_draw()
    
# Run the actual application
if __name__ == "__main__":
    window = Window()
    pyglet.app.run()