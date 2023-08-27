#!/usr/bin/env python3

import math

class Filter_IIR() :
		
	def __init__(self, num, den, x_ini=0.0, y_ini=0.0) :
		assert(len(num) == len(den))
		self.order = len(num) - 1
		assert(0 < self.order)
		
		self.x = [x_ini,] * (self.order + 1)
		self.y = [y_ini,] * (self.order + 1)
		
		self.b = num[:self.order + 1]
		self.a = den[:self.order + 1]

		print("num =", self.b)
		print("den =", self.a)

class Filter_IIR_direct_form_I(Filter_IIR) :

	def unwrap_360(self, x0, x1) :
		d = x0 - x1
		w = math.copysign(360.0, d) if abs(d) > 180.0 else 0.0
		return w
		
	def run(self, x0) :		
		self.x = [x0,] + self.x[:-1]
		self.y = [0.0,] + self.y[:-1]

		B = sum((b * x) for b, x in zip(self.b, self.x))
		A = sum((a * y) for a, y in zip(self.a[1:], self.y[1:]))
		y0 = B - A

		self.y[0] = y0

		return self.y[0]
	
	def run_wrapped_360(self, x0) :
		x0 = x0 % 360.0

		# for previous elements, an unwrap is applied first
		w = self.unwrap_360(x0, self.x[0])

		self.x = [x0,] + [w + x for x in self.x[:-1]]
		self.y = [0.0,] + [w + y for y in self.y[:-1]]

				
		B = sum((b * x) for b, x in zip(self.b, self.x))
		A = sum((a * y) for a, y in zip(self.a[1:], self.y[1:]))
		y0 = B - A
				
		self.y[0] = y0
		
		print(self.x, self.y)
		
		return self.y[0] % 360.0



