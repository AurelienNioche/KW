import numpy as np
cimport numpy as cnp

cpdef cnp.ndarray softmax(cnp.ndarray x, float temp):

    return np.exp(x / temp) / np.sum(np.exp(x / temp))