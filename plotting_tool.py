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
import mini_geometry #@UnresolvedImport



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
        
        #Used to store c style arrays of color and vertex data
        self.vertexData = None
        self.parseData('data/tommy.data')
        print(self.vertexData)
        
        ####################################################################################
        #----------TO BE CHANGED----------
        #store initial screen values
        self.screenWidth = 600
        self.screenHeight = 600
        w = self.screenWidth
        h = self.screenHeight
        x_max = 500.0
        x_min = -500.0
        y_max = 500.0
        y_min = -500.0
        z_max = 500.0 #near
        z_min = -500.0 #far
        #Same as viewer location (p_0)
        e_x = 0
        e_y = 0
        e_z = 200
        #should be transpose of xyz -> mini uvw
        #rotate by 90 degrees about x axis (want car to face z direction)
        xtheta = -270
        xtheta = math.radians(xtheta)
        x_rot = np.array([[1, 0, 0, 0], 
                         [0, math.cos(xtheta), -math.sin(xtheta), 0], 
                         [0, math.sin(xtheta), math.sin(xtheta), 0], 
                         [0, 0, 0, 1]])
        ztheta = 180
        ztheta = math.radians(ztheta)
        z_rot = np.array([[math.cos(ztheta), -math.sin(ztheta), 0, 0], 
                         [math.sin(ztheta), math.cos(ztheta), 0, 0], 
                         [0, 0, 1, 0], 
                         [0, 0, 0, 1]])
        miniLocal_worldTransform = np.dot(z_rot, x_rot)
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
        t = np.dot(trans_eyeTransform, miniLocal_worldTransform)
        self.modelViewTransform = np.dot(world_cameraTransform, t)
        
        self.p_ortho = np.array([[2/(x_max - x_min), 0, 0, -(x_max + x_min)/(x_max - x_min)], 
                                 [0, 2/(y_max - y_min), 0, -(y_max + y_min)/(y_max - y_min)],
                                 [0, 0, -2/(z_min - z_max), -(z_min + z_max)/(z_min - z_max)], 
                                 [0, 0, 0, 1]])
        
        self.p_perspective = np.array([[(2 * z_max)/(x_max - x_min), 0,                          -(x_max + x_min)/(x_max - x_min), 0],
                                       [0,                          (2 * z_max)/(y_max - y_min), -(y_max + y_min)/(y_max - y_min), 0],
                                       [0,                          0,                           -(z_min + z_max)/(z_min - z_max), -(2 * z_min * z_max)/(z_min - z_max)],
                                       [0,                          0,                           -1,                               0]])
        
        self.transform = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        ####################################################################################
           
        # Initialize GL state: Enable depth testing
        glClearColor(1, 1, 1, 1)
        glEnable(GL_DEPTH_TEST)

        # Initialize OpenGL data         
        self.createBuffers() #TODO: EDIT
        self.createShaders() #TODO: EDIT
        
        
    #Parses given data file, loads data into self.vertexData as c style array
    #Assumes file structure: X,Y,Z,R,G,B\n
    def parseData(self, data_file):
        #stores vertices read in from file (vertices and color interweaved)
        vertices = []
        with open(data_file, 'r') as f:
            for line in f:
                vertex = str(line).replace('\n', '').split(',')
                vertices.append(vertex)
        vertices = np.array(vertices).flatten()
        #save vertex data in c style array in instance variable
        self.vertexData = (GLfloat * vertices.size)()
        for i in xrange(0, vertices.size):
            self.vertexData[i] = float(vertices[i])

    
    ##################################################################
    # Buffer management
    
    def createBuffers(self):
        # TODO: Create, load, and bind your vertex & index buffers. Also
        # setup any vertex attributes. Note that the geometry stores 8
        # values per vertex (position x,y,z; normal x,y,z; texcoord u,v)
        # as floats in that order. You only need vertices for this assignment.
        # Your positions must be stored in vertex attribute 0.
        
        #holds the arrayID of our vertex array given by openGL
        self.arrayID = GLuint()
        #n = 1 (we want 1 vertex array object)
        glGenVertexArrays(1, byref(self.arrayID))
        glBindVertexArray(self.arrayID)
        
        #grab flat array of mini vertex data (of the form mentioned above)
        data = (GLfloat * len(self._mini.vertexdata))(*self._mini.vertexdata)
            
        self.bufferID = GLuint()
        glGenBuffers(1, byref(self.bufferID))
        #inits the buffer as a vertex buffer
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferID)
        #load data into buffer.  
        glBufferData(GL_ARRAY_BUFFER, sizeof(data), data, GL_STATIC_DRAW)
        
        #Associate the buffer data with the vertex array.  Ignore all the unused stuff
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(GLfloat * 8), 0)
        
        #turn on the arrays for OpenGL
        glEnableVertexAttribArray(0)
        
        #Create index buffers
        self.indexBufferID = GLuint()
        glGenBuffers(1, byref(self.indexBufferID))
        #grab the mini's indices
        miniIndices = (GLshort * len(self._mini.indices))(*self._mini.indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBufferID)
        #Again, dynamic?
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(miniIndices), miniIndices, GL_STATIC_DRAW)       
        #I guess the above code works...
        
    def destroyBuffers(self):
        # TODO: Clean up your vertex & index buffers
        #Make the vertex attribute arrays inactive
        glDisableVertexAttribArray(0)
        
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
        with open('a3.vert') as vertexFile:
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
        with open('a3.frag') as fragFile:
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
        
        
        # Link and enable the program
        glLinkProgram(self.programID)
        glUseProgram(self.programID)
        
        # TODO: Get and set the uniform variable values as needed
        # Store their locations as member variables for later
        self.partColorLoc = glGetUniformLocation(self.programID, "inColor")
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

        # TODO: Update any projection matrix/info you need
        self.screenWidth = width
        self.screenHeight = height
        
        # Always redraw
        self.on_draw()

    # Draw the window
    def on_draw(self):
        # Handles glClear calls
        self.clear()
        # TODO: Render your geometry. Update any uniforms (e.g., colors,
        # matrices) you may need.
        w = self.screenWidth
        h = self.screenHeight
        aspect = float(w)/h
        #apply local modelViewTransform to local transforms
        mvpMatrix = np.dot(self.modelViewTransform, self.transform)
        #apply ortho perspective matrix to model view matrix
        mvpMatrix = np.dot(self.p_ortho, mvpMatrix)
        #mvpMatrix = np.dot(self.p_perspective, mvpMatrix)
        
        #print(mvpMatrix)
        mvpMatrix = mvpMatrix.transpose()
        mvpTransform = (GLfloat * 16)()
        #Janky way to build our matrix
        for i in xrange(0, 16):
            mvpTransform[i] = mvpMatrix.flatten()[i]
           
        mini = self._mini 
        for part in mini.parts:
            start, end = mini.group(part)
            offset = sizeof(GLushort) * mini.indicesPerFace * start
            count = mini.indicesPerFace * (end - start)
            #pass color information in as uniform variable
#            glUniform3f(self.partColorLoc, *(colormap[part]))
            glUniformMatrix4fv(self.mvpTransformLoc, 1, GL_FALSE, *([mvpTransform]))
            glDrawElements(GL_TRIANGLES, count, GL_UNSIGNED_SHORT, offset)


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
            pass
            
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
            pass
                        
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
        # Add other keycodes as needed
        #print(self.transform)
        # Always redraw after keypress
        self.on_draw()
    
# Run the actual application
if __name__ == "__main__":
    window = Window()
    pyglet.app.run()