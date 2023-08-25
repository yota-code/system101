#!/usr/bin/env python3

import math

import numpy as np
import matplotlib.pyplot as plt

import scipy.signal

from cc_pathlib import Path

import digilter.iir
import digilter.butterworth

data = Path("merio.tsv").load()

t_arr = np.array([float(line[0]) for line in data[1:]])
pan_arr = np.array([float(line[1]) for line in data[1:]])
tilt_arr = np.array([float(line[2]) for line in data[1:]])

# d = t_arr[1:]-t_arr[:-1]
# plt.axhline(0.012, color="g")
# plt.axhline(0.008, color="g")
# plt.plot(d)
# plt.axhline(0.01, color="r")
# plt.axhline(np.mean(d), color="r", linestyle='--')
# plt.grid()

b_lst, a_lst = digilter.butterworth.Butterworth_LowPass_BLT(2, 3, 100)

print(b_lst)
print(a_lst)

x_arr = np.round(t_arr * 100.0) / 100.0

u = digilter.iir.Filter_IIR_direct_form_I(b_lst, a_lst, x_ini=pan_arr[0], y_ini=pan_arr[0])
u_arr = [u.run(x) for x in pan_arr]

v = digilter.iir.Filter_IIR_direct_form_I(b_lst, a_lst, x_ini=tilt_arr[0], y_ini=tilt_arr[0])
v_arr = [v.run(x) for x in tilt_arr]

print(x_arr)

plt.figure()
plt.subplot(2,1,1)
plt.plot(t_arr, pan_arr)
plt.plot(x_arr, u_arr)
plt.grid()

plt.subplot(2,1,2)
plt.plot(t_arr, tilt_arr)
plt.plot(x_arr, v_arr)
plt.grid()

plt.show()