import numpy as np
import numba
from numba import jit
import timeit

@jit(nopython=True)
def go_fast(a):
    trace=0.0
    for i in range (a.shape[0]):
        trace+=np.tanh(a[i,i])
    return a+trace

x=np.arange(100).reshape(10,10)
print(go_fast(x) )   

print(timeit.timeit( go_fast(x)))