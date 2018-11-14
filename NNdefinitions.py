import numpy as np
import keras as ks
import tensorflow as tf


"""
Preliminary step 
import numpy as np
np.random.seed(4)

. define some random example data
m=5  # number of training examples is 5
n=3  # number of neurons is 3
Z = np.random.rand(n,m)  # Make some random data for Z
Y = np.random.rand(n,m)  # Make some random data for Y

2. Calculate the softmax activation 
T = np.exp(Z)  # e to the power of Z
T_tot = np.sum(T,axis=0)  # Get the total of T
AL = np.divide(T,T_tot)  # Normalize with the total of T


3. Calculate the cost 
elementwise_product = np.multiply(Y,np.log(AL)) # Multiply each element of Y with the log of each element of AL
print("\nThe elementwise product of AL, Y is: \n",elementwise_product)  # For each training sample and neuron we have a product
elementwise_product_sum = -np.sum(elementwise_product,axis=0)  # The loss is the sum over each training sample
print("\nThe loss for each training example is: \n",elementwise_product_sum)  # We have a loss now for each sample
cost = (1/m) * np.sum(elementwise_product_sum)  # The cost is the sum of all the losses
print("\nThe cost J is: \n",cost)

"""



def initialize_weights(layers_dimensions):
    # wejscie tablica z wymiarami poszczegolnych warstw sieci
    # wyjscie parametry sieci
    
    parameters = {}
    
    np.random.seed(3)
    
    for layer in range(1, len(layers_dimensions)):
        print(layer)
        parameters["W" + str(layer)] = np.random.randn(layers_dimensions[layer], layers_dimensions[layer-1])*np.sqrt(1/layers_dimensions[layer-1])
        parameters["b" + str(layer)] = np.zeros((layers_dimensions[layer], 1))
        
        """
        parameters["V_db" + str(layer)] = np.zeros((layers_dimensions[layer], 1))
        parameters["V_dW" + str(layer)] = np.zeros((layers_dimensions[layer], layers_dimensions[layer-1]))
        parameters["S_db" + str(layer)] = np.zeros((layers_dimensions[layer], 1))
        parameters["S_dW" + str(layer)] = np.zeros((layers_dimensions[layer], layers_dimensions[layer-1]))
        parameters["V_db_norm" + str(layer)] = np.zeros((layers_dimensions[layer], 1))
        parameters["V_dW_norm" + str(layer)] = np.zeros((layers_dimensions[layer], layers_dimensions[layer-1]))
        parameters["S_db_norm" + str(layer)] = np.zeros((layers_dimensions[layer], 1))
        parameters["S_dW_norm" + str(layer)] = np.zeros((layers_dimensions[layer], layers_dimensions[layer-1]))
        """
    
    return parameters

#---------------------------------------forward_part----------------------------------------

def forward_linear(A_prev, W, b):
    # wyjscie : Z, cache z A_prev, W , b
    
    Z = np.dot(W, A_prev) + b
    
    cache = (A_prev, W, b)
    
    return Z, cache

def forward_activation(A_prev, W, b, activation_function):
    
    if activation_function== "relu":
        #print("relu")
        Z, linear_cache = forward_linear(A_prev, W, b)
        A = np.maximum(0, Z)
    
    if activation_function == "sigmoid":
        #print("sigmoid")
        Z, linear_cache = forward_linear(A_prev, W, b)
        A = np.divide(1, 1 + np.exp(-Z))
    if activation_function == "softmax":
        #print("softmax")
        Z, linear_cache = forward_linear(A_prev, W, b)
        print("Z.shape = " + str(Z.shape))
        
        T = np.exp(Z)  # e to the power of Z
        T_tot = np.sum(T,axis=0)  # Get the total of T
        print("T_tot.shape = " + str(T_tot.shape))
        print("   T_tot = " + str(T_tot))
        A = np.divide(T,T_tot)  # Normalize with the total of T
        
    
    cache = Z
    
    caches = (cache, linear_cache)
    
    return A, caches

def compute_cost(A_last, Y):
    
    #cost = -1/m*(Y*np.log(A) + (1-Y)*np.log(1-A))
    A_last = np.log(A_last)
    mult = np.multiply(Y, A_last)
    elementwise_product_sum = -np.sum(mult,axis=0)
    cost = (1/Y.shape[1]) * np.sum(elementwise_product_sum)
    return cost


def complete_forward(X, parameters):
    
    LEN = len(parameters) // 2
    A_prev = X
    
    caches = []
    
    for l in range(1, LEN):
        A_prev, cache= forward_activation(A_prev, parameters["W" + str(l)], parameters["b" + str(l)], "relu")
        caches.append(cache)
        
    A_last, cache = forward_activation(A_prev, parameters["W" + str(LEN)], parameters["b" + str(LEN)], "softmax")
    caches.append(cache)
    
    return A_last, caches

#---------------------------------------backward_part----------------------------------------

def relu_backward(dA, activation_cache):
    
    Z = activation_cache
    dZ = np.array(dA, copy=True) # just converting dz to a correct object.
    dZ[Z <= 0] = 0
    assert (dZ.shape == Z.shape)
    return dZ

def sigmoid_backward(dA, activation_cache):
    
    Z = activation_cache
    s = 1/(1 + np.exp(-Z))
    dZ =dA* s*(1-s)
            
    return dZ

def softmax_backward(dA, activation_cache):
    
    Z = activation_cache
    s = 1/(1+np.exp(-Z))
    A=(np.exp(Z).T / np.sum(np.exp(Z),axis=1)).T
    dZ = dA * s * (1-s)
    dZ = A * (1+dA)
    dZ = np.array(dA, copy=True)
    assert (dZ.shape == Z.shape)
    return dZ

def linear_backward(dZ, cache):
      
    (A_prev, W, b) = cache
    m = A_prev.shape[1]
    dW = 1/m*np.dot(dZ, A_prev.T)
    db = 1/m*np.sum(dZ, axis = 1, keepdims = True)
    dA_prev = np.dot(W.T, dZ)
    assert (dA_prev.shape == A_prev.shape)
    assert (dW.shape == W.shape)
    assert (db.shape == b.shape)
    
    return dA_prev, dW, db

def activation_backward(dA, activation_cache, linear_cache, activation_function):
    
    if activation_function == "relu":
        dZ = relu_backward(dA, activation_cache)
    
    if activation_function == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)
    
    if activation_function == "softmax":
        dZ = softmax_backward(dA, activation_cache)
    
    return dZ

def layer_backward(dA, cache, activation_function):
    
    (activation_cache, linear_cache) = cache
    
    dZ = activation_backward(dA, activation_cache, linear_cache, activation_function)
    A_prev, dW, db = linear_backward(dZ, linear_cache)
    
    return A_prev, dW, db

def backward_propagation(A_last, Y, caches):
    
    #dA = -(np.divide(Y, A_last) - np.divide((1-Y), (1-A_last)))
    dA = -np.divide(Y, A_last)
    
    changes = {}
    
    LEN = len(caches)
    
    current_cache = caches[LEN-1]
    
    changes["dA" + str(LEN-1)], changes["dW" + str(LEN)], changes["db" + str(LEN)] = layer_backward(dA, current_cache, "softmax")
    dA_prev = changes["dA" + str(LEN-1)]
    
    
    for l in reversed(range(LEN-1)):
        current_cache = caches[l]
        changes["dA" + str(l)], changes["dW" + str(l+1)], changes["db" + str(l+1)] = layer_backward(dA_prev, current_cache, "relu")
        dA_prev = changes["dA" + str(l)]
        
    return changes

def update_parameters(gradients, parameters, learning_rate, epoch):
    
    LEN = len(parameters) // 2
    
    learning_rate = np.power(0.97, epoch)*learning_rate
    
    for l in range(LEN):
        parameters["W" + str(l+1)] = parameters["W" + str(l+1)] - learning_rate*gradients["dW" + str(l+1)] 
        parameters["b" + str(l+1)] = parameters["b" + str(l+1)] - learning_rate*gradients["db" + str(l+1)]
    
    return parameters

def update_parametersADAM(gradients, parameters, learning_rate, epoch, Beta_1, Beta_2):  # czemu psuje zobaczyc
    
    LEN = len(parameters) // 2
    Epsilon = 0.00000001
    
    learning_rate = np.power(0.97, epoch)*learning_rate
    
    for l in range(LEN):
        parameters["V_db" + str(l+1)] = Beta_1*parameters["V_db" + str(l+1)] + (1-Beta_1)*gradients["db" + str(l+1)]
        parameters["V_dW" + str(l+1)] = Beta_1*parameters["V_dW" + str(l+1)] + (1-Beta_1)*gradients["dW" + str(l+1)]
        parameters["S_db" + str(l+1)] = Beta_2*parameters["S_db" + str(l+1)] + (1-Beta_2)*np.power(gradients["db" + str(l+1)],2)
        parameters["S_dW" + str(l+1)] = Beta_2*parameters["S_dW" + str(l+1)] + (1-Beta_2)*np.power(gradients["dW" + str(l+1)],2)
        
        parameters["V_db_norm" + str(l+1)] = np.divide(parameters["V_db_norm" + str(l+1)], 1 - np.power(Beta_1, epoch))
        parameters["V_dW_norm" + str(l+1)] = np.divide(parameters["V_dW_norm" + str(l+1)], 1 - np.power(Beta_1, epoch))
        parameters["S_db_norm" + str(l+1)] = np.divide(parameters["S_db_norm" + str(l+1)], 1 - np.power(Beta_2, epoch))
        parameters["S_dW_norm" + str(l+1)] = np.divide(parameters["S_dW_norm" + str(l+1)], 1 - np.power(Beta_2, epoch))
        
        parameters["W" + str(l+1)] = parameters["W" + str(l+1)] - learning_rate*parameters["V_dW_norm" + str(l+1)]/np.sqrt(parameters["S_dW_norm" + str(l+1)]+Epsilon)
        parameters["b" + str(l+1)] = parameters["b" + str(l+1)] - learning_rate*parameters["V_db_norm" + str(l+1)]/np.sqrt(parameters["S_db_norm" + str(l+1)]+Epsilon)
    
    return parameters
