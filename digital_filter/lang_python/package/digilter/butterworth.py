#!/usr/bin/env python3

import math

import sympy

def Butterworth_polynom(n:int, s) :
    assert(0 < n)
    u = [
        (s**2 - 2*s*sympy.cos(sympy.pi*(2*k+n-1)/(2*n)) + 1) for k in range(1, n // 2 + 1)
    ]
    if n % 2 != 0 : # polynom is odd
        u.append(s + 1)
    return sympy.prod(u)

def Butterworth_LowPass_analog(n:int) :
	s = sympy.symbols('s')
	return 1 / Butterworth_polynom(n, s).expand().collect(s)

def Butterworth_LowPass_BLT(n:int, fc=None, fs=None) : # bilinear transformation
	g, z = sympy.symbols('gamma z')
	analog = Butterworth_LowPass_analog(n)
	discrete = analog.subs({'s': g * (z-1) / (z+1)}).expand().collect(z).simplify()
	num, den = discrete.as_numer_denom()

	b_lst = sympy.Poly(num.expand().simplify().collect(z), z).all_coeffs()
	a_lst = sympy.Poly(den.expand().simplify().collect(z), z).all_coeffs()

	if fc is not None and fs is not None :
		g_val = 1 / math.tan(math.pi * fc / fs)
		a0 = float(a_lst[0].subs({'gamma': g_val}))
		b_lst = [(float(b.subs({'gamma': g_val})) / a0) for b in b_lst]
		a_lst = [(float(a.subs({'gamma': g_val})) / a0) for a in a_lst]
		
	return b_lst, a_lst 

if __name__ == '__main__' :
	import scipy.signal

	import numpy as np
	import matplotlib.pyplot as plt

	import iir

	n, fc, fs = 2, 10, 300

	b_lst, a_lst = Butterworth_LowPass_BLT(n, fc, fs)
	print(b_lst)
	print(a_lst)

	b_check, a_check = scipy.signal.butter(n, 2 * fc / fs)
	print(b_check)
	print(a_check)

	for n, (x, y) in enumerate(zip(b_lst, b_check)) :
		s = "\x1b[32mOK\x1b[0m" if abs(x - y) < 1e-6 else f"KO reference = {y:12.6g}"
		print(f"b{n} = {x:12.6g} ({s})")
	print()
	for n, (x, y) in enumerate(zip(a_lst, a_check)) :
		s = "\x1b[32mOK\x1b[0m" if abs(x - y) < 1e-6 else f"KO reference = {y:12.6g}"
		print(f"a{n} = {x:12.6g} ({s})")

	x_arr = np.array([0.0,]*5 + [1.0]*50 + [359.0]*50)
	y_arr = scipy.signal.lfilter(b_lst, a_lst, x_arr)

	u = iir.Filter_IIR_direct_form_I(b_lst, a_lst)
	u_arr = [u.run(x) for x in x_arr]
	v = iir.Filter_IIR_direct_form_I(b_lst, a_lst)
	v_arr = [v.run_wrapped_360(x) for x in x_arr]

	print(y_arr)
	print(v_arr)

	plt.plot(x_arr)
	# plt.plot(y_arr)
	plt.plot(u_arr)
	plt.plot(v_arr, '--')
	plt.grid()
	plt.show()

	sys.exit(0)

	w, H_d = scipy.signal.freqz(b_lst, a_lst, 4096)
	w *= fs / (2 * math.pi)

	# Design the analog Butterworth filter
	b_analog, a_analog = scipy.signal.butter(n, fc, analog=True)
	print('\nAnalog Coefficients')
	print("b =", b_analog)
	print("a =", a_analog)

	w, H_a = scipy.signal.freqs(b_analog, a_analog, w)

	# Plot the amplitude response
	plt.figure()

	plt.subplot(2, 1, 1)            
	plt.suptitle('Bode Plot')
	H_d_dB = 20 * np.log10(abs(H_d))          # Convert modulus of H to dB
	H_a_dB = 20 * np.log10(abs(H_a))
	plt.semilogx(w, H_d_dB, color='blue', label='Digital')
	plt.semilogx(w, H_a_dB, color='green', label='Analog')
	plt.legend()
	plt.ylabel('Magnitude [dB]')
	plt.xlim(fc / 2, fs / (2 + 1e-2))
	plt.ylim(-80, 6)
	plt.axvline(fc, color='red')
	plt.axhline(-3, linewidth=0.8, color='black', linestyle=':')
	plt.grid()

	plt.subplot(2, 1, 2)
	phi_d = np.angle(H_d)                     # Argument of H
	phi_a = np.angle(H_a)
	phi_d = np.degrees(np.unwrap(phi_d))       # Remove discontinuities
	phi_a = np.degrees(np.unwrap(phi_a))       # and convert to degrees
	plt.semilogx(w, phi_d, color='blue')
	plt.semilogx(w, phi_a, color='green')  
	plt.xlabel('Frequency [Hz]')
	plt.ylabel('Phase [°]')
	plt.xlim(fc / 2, fs / (2 + 1e-2))
	# plt.ylim(-360, 0)
	# plt.yticks([-360, -270, -180, -90, 0])
	plt.axvline(fc, color='red')
	plt.grid()

	plt.show()