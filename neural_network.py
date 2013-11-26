'''
Created on Nov 20, 2013

@author: Alex Lalejini
netid: aml386
'''
import random
import math
import numpy as np
import matplotlib.pyplot as plt



class NeuralNetwork():
    #NOTE: FOR THIS PARTICULAR APPLICATION: INPUT LAYER MUST BE 2, OUTPUT LAYER MUST BE 4
    def __init__(self):
        net_description = [2, 10000, 4]
        ##################################
        #----------NETWORK INITIALIZATION----------
        #each element in net_descrip describes the # of neurons at that layer
        #the first element is always the input layer and the last element is always the output layer
        self.net_descrip = net_description
        #used to store weights
        self.weights = {}
        self.biases = []
        #used to store value for each neuron
        self.values = []
        #used to store error gradient for each neuron
        self.error_gradients = []
        #Initialize weights in network based on net_descrip
        for L in xrange(1, len(self.net_descrip)):
            for P in xrange(0, self.net_descrip[L - 1]):
                for N in xrange(0, self.net_descrip[L]):
                    weight_name = "W" + str(L) + "-" + str(P) + "-" + str(N)
                    self.weights[weight_name] = self.gen_weight()
        #Initialize array used to store y values and error gradient values
        for L in xrange(0, len(self.net_descrip)):
            self.values.append([])
            self.biases.append([])
            self.error_gradients.append([])
            for N in xrange(0, self.net_descrip[L]):
                self.values[L].append(0)
                self.biases[L].append(2 * self.gen_weight() - 1)
                self.error_gradients[L].append(0)
    
    #in the form [x, y, z, r, g, b]           
    def train(self, training_set = [], epochs_to_train = 0, learning_rate = 0):
        #----------TRAINING----------
        epochs = 0    
        while True:
            # ----- TRAIN -----
            #for each vertex in list of training vertices
            for ex in xrange(0, len(training_set)):        
                #Load Input
                x = float(training_set[ex][0])
                y = float(training_set[ex][1])
                self.values[0][0] = x
                self.values[0][1] = y
                #Load correct output
                z = float(training_set[ex][2])
                r = float(training_set[ex][3])
                g = float(training_set[ex][4])
                b = float(training_set[ex][5])
                correct_output = [z, r, g, b]
                #---Forward Pass---
                # - Update hidden layer and output layer values
                for L in xrange(1, len(self.net_descrip)):
                    for N in xrange(0, self.net_descrip[L]):
                        #for each input (value of previous layer)
                        Y_N = 0
                        for I in xrange(0, self.net_descrip[L - 1]):
                            weight_name = "W" + str(L) + "-" + str(I) + "-" + str(N)
                            Y_N += self.values[L - 1][I] * self.weights[weight_name]
                        Y_N = self.sigmoid(Y_N - self.biases[L][N])
                        self.values[L][N] = Y_N
                # - Calculate Error in output values
                errors = []
                for o in xrange(0, len(correct_output)):
                    error = correct_output[o] - self.values[-1][o]
                    errors.append(error)
                #---Backpropagation---
                # - calculate error gradients for output layer
                for Y in xrange(0, len(self.values[-1])):
                    Y_N = self.values[-1][Y]
                    err_grad = Y_N * (1 - Y_N) * errors[Y]
                    self.error_gradients[-1][Y] = err_grad
                    self.biases[-1][Y] += self.learning_rate * (-1) * err_grad
                # - calculate error gradients for hidden layers POTENTIAL POINT OF FAILURE
                for L in xrange(len(self.net_descrip) - 2, 0, -1):
                    for N in xrange(0, self.net_descrip[L]):
                        D_N = 0
                        for I in xrange(0, self.net_descrip[L + 1]):
                            weight_name = "W" + str(L + 1) + "-" + str(N) + "-" + str(I)
                            D_N += self.error_gradients[L + 1][I] * self.weights[weight_name]
                        D_N *= self.values[L][N] * (1 - self.values[L][N])
                        self.error_gradients[L][N] = D_N
                        self.biases[L][N] += learning_rate * (-1) * D_N
                # - calculate weight corrections
                for W in self.weights:
                    weight = W.replace("W", "")
                    weight = weight.split("-")
                    L = int(weight[0])
                    P = int(weight[1])
                    N = int(weight[2])
                    Y_P = self.values[L - 1][P]
                    D_N = self.error_gradients[L][N]
                    DW_PN = learning_rate * Y_P * D_N
                    self.weights[W] += DW_PN
                    
            epochs += 1
            if (epochs >= epochs_to_train):
                break
          
        print("====================================")
        print("Epochs Trained: " + str(epochs))
        print("Weights: " + str(self.weights))
        print("Biases: " + str(self.biases))
        print("====================================")
    
    #calculates [z, r, g, b] based on given x, y   
    def calculate(self, x, y):
        #Load Input
        self.values[0][0] = x
        self.values[0][1] = y    
        #---Forward Pass---
        # - Update hidden layer and output layer values
        for L in xrange(1, len(self.net_descrip)):
            for N in xrange(0, self.net_descrip[L]):
                #for each input (value of previous layer)
                Y_N = 0
                for I in xrange(0, self.net_descrip[L - 1]):
                    weight_name = "W" + str(L) + "-" + str(I) + "-" + str(N)
                    Y_N += self.values[L - 1][I] * self.weights[weight_name]
                Y_N = self.sigmoid(Y_N - self.biases[L][N])
                self.values[L][N] = self.correct(Y_N)
        print("=====================")
        print("Input: " + str([x,y]))
        print("Output: " + str(self.values[-1]))
        output = self.values[-1]
        return output
    
        
    def gen_weight(self):
        return random.random()
    
    def sigmoid(self, v):
        return (1.0)/float(1.0 + math.pow(math.e, -1.0 * v))
    
    def correct(self, y):
        if (y >= 0.8):
            return 1.0
        elif (y <= 0.2):
            return 0.0
        else:
            return y
