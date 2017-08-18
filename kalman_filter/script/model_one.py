#!/usr/bin/env python3

import math
import random
import sys

import numpy as np
import matplotlib.pyplot as plt

class RndGauss() :
	def __init__(self, default_mu=0.0, default_sigma=1.0) :
		self.default_mu = default_mu
		self.default_sigma = default_sigma

		self.mu_param = dict()
		self.sigma_param = dict()
		self.rndgauss = dict()

	def get(self, key, mu=None, sigma=None) :
		if key not in self.rndgauss or len(self.rndgauss) <= 0 :
			if key not in self.mu_param :
				if mu is None :
					mu = self.default_mu
				self.mu_param[key] = mu
			if key not in self.sigma_param :
				if sigma is None :
					sigma = self.default_sigma
				self.sigma_param[key] = sigma
			self.rndgauss = [
				random.gauss(self.mu_param[key], self.sigma_param[key])
				for i in range(1024)
			]
		return self.rndgauss.pop(0)

RN = RndGauss()

class Rover() :
	delta_t = 0.01
	def __init__(self) :
		"""
		describe the current state of the rover
		state = [
			[ position ],
			[ speed ]
		]
		"""
		self.state = np.matrix([[0.0], [0.0]])
		"""
		describe the transformation from current state to next state
		system = [
			[ 1, T ],
			[ 0, 1 ]
		]
		"""
		self.application = np.matrix([[1.0, self.delta_t], [0.0, 1.0]])
		"""
		describe the contribution of the command to the system
		command = [
			[ 0 ],
			[ 1 ]
		]
		"""
		self.command = np.matrix([[0.0], [1.0]])

		"""
		Transform the state vector into the observed vector.
		The observed vector is made of : position, speed of each wheel
		observation = [
			[ 1, 0 ],
			[ 0, 1 ],
			[ 0, 1 ],
		]

		"""
		self.observation = np.matrix([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])

		"""
		The sensor noise is also a component of the system
		"""
		self.sensor_noise = np.matrix([[1.0, 0.0, 0.0], [0.0, 0.1, 0.0], [0.0, 0.0, 0.1]])

		self.state_history = list()

		self.input_clean = list()
		self.input_noisy = list()

		self.observed_clean = list()
		self.observed_noisy = list()

	def prepare_input(self, throttle) :
		return np.matrix([[throttle,]], dtype=np.double)

	def run(self, throttle) :
		print(throttle)
		input_vec = self.prepare_input(throttle)

		self.input_clean.append(input_vec.tolist())

		# add some imperfections on the real system:
		input_vec[0,0] = self.prepare_input(
		 	0.5 * input_vec[0,0] + RN.get('throttle', sigma=0.5),
		)

		self.input_noisy.append(input_vec.tolist())

		self.state_history.append(self.state)

		self.state = self.application @ self.state + self.command @ input_vec

		observed = self.observation @ self.state

		self.observed_clean.append(observed.tolist())

		# add some imperfections to the real sensors
		# observed[0,0] = round(observed[0,0] + RN.get('pos', sigma=2.0))
		observed[0,0] = observed[0,0] + RN.get('pos', sigma=15.0)
		observed[1,0] = observed[1,0] + RN.get('spd1', sigma=5.0)
		observed[2,0] = observed[2,0] + RN.get('spd2', sigma=5.0)

		self.observed_noisy.append(observed.tolist())

		return input_vec, observed, self.sensor_noise

class KalmanFilter() :
	delta_t = 0.01
	def __init__(self, model) :
		self.model = model

		self.state = np.matrix([[0.0], [0.0]])

		# system, command and observation matrices should match the Rover's matrices
		#self.application = np.matrix([[1.0, self.delta_t], [0.0, 1.0]])
		#self.command = np.matrix([[0.0], [1.0]])
		#self.observation = np.matrix([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])

		"""
		the result of the filter could be seen as a gaussian blob where:
		 * the state represents the estimated mean values
		 * the covariance represents the standard deviations and the amount
		of uncertainty
		"""
		self.covariance = np.matrix([[0.0, 0.0], [0.0, 0.0]])

		self.state_history = list()
		self.covariance_history = list()
		self.input_history = list()
		self.observed_history = list()


	def run(self, input_vec, sensor_m, sensor_s) :
		self.input_history.append(input_vec.tolist())
		self.observed_history.append(sensor_m.tolist())

		self.predict(input_vec)
		self.update(sensor_m, sensor_s)
		#print("{0} {1} -> {2}".format(sensor_m[1,0], sensor_m[2,0], self.state[1,0]))

		self.state_history.append(self.state)
		self.covariance_history.append(self.covariance)

	def predict(self, input_vec) :
		m = self.model

		self.state = m.application @ self.state + m.command @ input_vec

		q = np.matrix([
			[0.0, 0.0],
			[0.0, 0.0]
		])

		self.covariance = m.application @ self.covariance @ m.application.T + q

	def update(self, sensor_m, sensor_s) :
		m = self.model

		"""
		reduced kalman gain
		"""
		K = self.covariance @ m.observation.T @ (
			m.observation @ self.covariance @ m.observation.T + sensor_s
		).I

		self.state = self.state + K @ (sensor_m - m.observation @ self.state)
		self.covariance = self.covariance - K @ m.observation @ self.covariance

if __name__ == '__main__' :


	random.seed(0)

	u = Rover()
	k = KalmanFilter(u)

	m = [1,] * 80 + [0,] * 120 + [-2] * 40
	for throttle in m :
		input_vec, sensor_m, sensor_s = u.run(throttle) # real observed values
		k.run(input_vec, sensor_m, sensor_s) # estimated observed values

	# plt.plot(np.array(u.input_clean)[:,0,0])
	# plt.plot(np.array(u.input_noisy)[:,0,0], '+')
	# plt.show()
	#
	# plt.plot(np.array(u.observed_clean)[:,0,0])
	# plt.plot(np.array(u.observed_noisy)[:,0,0], '+')
	# plt.plot(np.array(u.observed_clean)[:,1,0])
	# plt.plot(np.array(u.observed_noisy)[:,1,0], '+')
	# plt.plot(np.array(u.observed_clean)[:,2,0])
	# plt.plot(np.array(u.observed_noisy)[:,2,0], '+')
	# plt.show()
	#
	# plt.plot(np.array(u.state_history)[:,0,0])
	# plt.plot(np.array(u.state_history)[:,1,0])
	# plt.plot(np.array(k.state_history)[:,0,0], '+-')
	# plt.plot(np.array(k.state_history)[:,1,0], '+-')
	# plt.show()

	plt.subplot(2,1,1)
	plt.plot(np.array(k.observed_history)[:,0,0])
	plt.plot(np.array(u.state_history)[:,0,0], 'o-')
	plt.plot(np.array(k.state_history)[:,0,0], '+-')
	plt.subplot(2,1,2)
	plt.plot(np.array(k.observed_history)[:,1,0])
	plt.plot(np.array(k.observed_history)[:,2,0])
	plt.plot(np.array(u.state_history)[:,1,0], 'o-')
	plt.plot(np.array(k.state_history)[:,1,0], '+-')
	plt.show()

	sys.exit(0)
