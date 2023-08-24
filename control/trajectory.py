#!/usr/bin/env python3

import math
import sys

import numpy as np
import matplotlib.pyplot as plt

class Filter2sat :
	def __init__(self, omega0, epsilon, sat_1, sat_2, period=0.02) :
		self.period = period
		
		self.omega0 = omega0
		self.epsilon = epsilon
		
		# Here saturation is symetric, but it could be implemented to use different values for upper and lower bounds
		self.sat_1 = sat_1
		self.sat_2 = sat_2
				
		self.y0_lst = [0.0,]
		self.y1_lst = [0.0,]
		self.y2_lst = [0.0,]
		
		self.x0_lst = list()
		
		self.n = 0
		self.t_lst = list()
		
	def bound(self, x, lower, upper) :
		return max(lower, min(x, upper))
		
	def run(self, x0) :
		
		# first we compute y2, the second order derivative of the output
		# from the previous values of y0 and y1
		y2 = (x0 - self.y0_lst[-1] - (2 * self.epsilon * self.y1_lst[-1] / self.omega0)) * self.omega0**2
		
		# we apply the sat 2 limitation
		y2 = self.bound(y2, -self.sat_2, self.sat_2)
				
		# y1 is the integration of y2
		y1 = self.y1_lst[-1] + self.period * (self.y2_lst[-1] + y2) / 2
		
		# we apply the sat 1 limitation
		y1 = self.bound(y1, -self.sat_1, self.sat_1)
		
		# y0, the output of the filter is the integration of y1
		y0 = self.y0_lst[-1] + self.period * (self.y1_lst[-1] + y1) / 2
		
		# DEBUG BEGIN
		self.x0_lst.append(x0)
		
		self.y2_lst.append(y2)
		self.y1_lst.append(y1)
		self.y0_lst.append(y0)
		
		self.t_lst.append(self.n * self.period)
		self.n += 1
		# DEBUG END
		
		return y0

def find_ffwd_coef(omega0, epsilon, sat_1, sat_2, modulo) :

	d_lst = list()
	y1_lst = list()
	for d in np.linspace(0.0, 50.0, 50) :
		u = Filter2sat(omega0, epsilon, sat_1, sat_2)
		for i in range(2000) :
			if i % modulo == 0 :
				y0_last = u.y0_lst[-1]

			u.run(y0_last + d)

		if u.y1_lst[-1] < sat_1 * 0.9 :
			d_lst.append(d)
			y1_lst.append(u.y1_lst[-1])

		# plt.figure()
		# plt.subplot(3, 1, 1)
		# plt.plot(u.t_lst, u.y0_lst[1:], label=f"d={d}")
		# plt.plot(u.t_lst, u.x0_lst)
		# plt.legend()
		# plt.subplot(3, 1, 2)
		# plt.plot(u.t_lst, u.y1_lst[1:])
		# plt.subplot(3, 1, 3)
		# plt.plot(u.t_lst, u.y2_lst[1:])
		# plt.show()

	slope = d_lst[-1] / y1_lst[-1]
	print(f"ffwd :: delta = {slope} * vz")

	# plt.figure()
	# plt.title("delta = f(vz)")
	# plt.plot(y1_lst, d_lst)
	# plt.xlabel("vz")
	# plt.ylabel("delta")
	# plt.annotate(f"slope = {slope:.5g}", (1 + y1_lst[-1] / 2, -1 + d_lst[-1] / 2))
	# plt.show()

	return slope

def find_fbck_coef(omega0, epsilon, sat_1, sat_2, modulo, lvl_tgt) :
	ffwd = find_ffwd_coef(omega0, epsilon, sat_1, sat_2, modulo)

	gain1 = 1.0
	gain2 = 0.0

	u = Filter2sat(omega0, epsilon, sat_1, sat_2)

	vz_tgt_lst = list()
	vz_cur_lst = list()
	delta_lst = list()
	vz_delta_lst = list()
	lvl_delta_lst = list()
	
	for i in range(6) :
		u.run(0.0)

	for i in range(4000) :
		if i % modulo == 0 :
			lvl_cur = u.y0_lst[-1]
			vz_cur = u.y1_lst[-1]

			lvl_delta = lvl_tgt - lvl_cur
			lvl_delta_lst.append(lvl_delta)

			vz_tgt = max(-8.0, min(math.copysign(math.sqrt(abs(lvl_delta) * 2.0 * 0.5), lvl_delta), 8.0))
			vz_tgt = max(-8.0, min(lvl_delta * 0.4, 8.0))

			vz_tgt_lst.append(vz_tgt)
			vz_cur_lst.append(vz_cur)

			vz_delta = vz_tgt - vz_cur
			vz_delta_lst.append(vz_delta)
			delta = vz_tgt * ffwd + vz_delta * gain1 + vz_delta * vz_delta * gain2

			delta_lst.append(delta)

		u.run(lvl_cur + delta)

	plt.figure()
	plt.subplot(3, 2, 1)
	plt.plot(u.t_lst, u.y0_lst[1:], label="y0")
	plt.plot(u.t_lst, u.x0_lst, label="x0")
	plt.legend()
	plt.subplot(3, 2, 3)
	plt.plot(u.t_lst, u.y1_lst[1:])
	plt.subplot(3, 2, 5)
	plt.plot(u.t_lst, u.y2_lst[1:])
	plt.subplot(3, 2, 2)
	plt.plot(lvl_delta_lst, label="lvl_delta")
	plt.legend()
	plt.subplot(3, 2, 4)
	plt.plot(vz_tgt_lst, label="vz_tgt")
	plt.plot(vz_delta_lst, label="vz_delta")
	plt.legend()
	plt.subplot(3,2,6)
	plt.plot(delta_lst, label="delta_cmd")
	plt.legend()

	plt.show()

def plot_demo(omega0, epsilon, sat_1, sat_2, period=0.02) :
	x = [0.0,] * 4 + [200.0,] * 2000
	u = Filter2sat(omega0, epsilon, 8.0, 2.0)
	v = Filter2sat(omega0, epsilon, math.inf, math.inf)

	y_sat = [u.run(i) for i in x]
	y_flt = [v.run(i) for i in x]

	plt.figure()
	plt.subplot(3, 1, 1)
	plt.plot(v.t_lst, v.y0_lst[1:], label="classic")
	plt.plot(v.t_lst, u.y0_lst[1:], label="limited")
	plt.plot(v.t_lst, v.x0_lst)
	plt.legend()
	plt.subplot(3, 1, 2)
	plt.plot(v.t_lst, v.y1_lst[1:])
	plt.plot(v.t_lst, u.y1_lst[1:])
	plt.subplot(3, 1, 3)
	plt.plot(v.t_lst, v.y2_lst[1:])
	plt.plot(v.t_lst, u.y2_lst[1:])
	plt.show()

if __name__ == '__main__' :

	omega0 = 0.5
	epsilon = 0.9
	sat_1 = 8.0
	sat_2 = 2.0

	# find_ffwd_coef(omega0, epsilon, sat_1, sat_2, 1)
	find_fbck_coef(omega0, epsilon, sat_1, sat_2, 1, 200.0)

	sys.exit(0)

	plot_demo(omega0, epsilon, sat_1, sat_2, period=0.02)
