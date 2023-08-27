#!/usr/bin/env python3

import math

import numpy as np
import matplotlib.pyplot as plt

import scipy.signal

from cc_pathlib import Path

import digilter.iir
import digilter.butterworth

fc, fs = 45, 360

b_lst, a_lst = digilter.butterworth.Butterworth_LowPass_BLT(2, fc, fs)

print(scipy.signal.butter(2, 2 * fc / fs))

x_arr = np.array([10.0,] * 5 + [-10.0,] * 20)

u = digilter.iir.Filter_IIR_direct_form_I(b_lst, a_lst, x_ini=10.0, y_ini=10.0)
y_arr = [u.run_wrapped_360(x) for x in x_arr]

plt.figure()
plt.plot(x_arr)
plt.plot(y_arr)
plt.grid()
plt.show()