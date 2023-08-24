from scipy.signal import butter, freqz, freqs
import matplotlib.pyplot as plt
from math import pi
import numpy as np

f_s = 360    # Sample frequency in Hz
f_c = 45     # Cut-off frequency in Hz
order = 2    # Order of the butterworth filter

omega_c = 2 * pi * f_c       # Cut-off angular frequency
omega_c_d = omega_c / f_s    # Normalized cut-off frequency (digital)

# Design the digital Butterworth filter
b_d, a_d = butter(order, omega_c_d / pi)    
print('Digital Coefficients')
print("b =", b_d)                         # Print the coefficients
print("a =", a_d)

w, H_d = freqz(b_d, a_d, 4096)            # Calculate the frequency response
w *= f_s / (2 * pi)                       # Convert from rad/sample to Hz

# Design the analog Butterworth filter
b_a, a_a = butter(order, f_c, analog=True)
print('Analog Coefficients')
print("b =", b_a)                         # Print the coefficients
print("a =", a_a)

w, H_a = freqs(b_a, a_a, w)               # Calculate the frequency response

# Plot the amplitude response
plt.subplot(2, 1, 1)            
plt.suptitle('Bode Plot')
H_d_dB = 20 * np.log10(abs(H_d))          # Convert modulus of H to dB
H_a_dB = 20 * np.log10(abs(H_a))
plt.plot(w, H_d_dB, color='blue', label='Digital')
plt.plot(w, H_a_dB, color='green', label='Analog')
plt.legend()
plt.ylabel('Magnitude [dB]')
plt.xlim(0, f_s / 2)
plt.ylim(-80, 6)
plt.axvline(f_c, color='red')
plt.axhline(-3, linewidth=0.8, color='black', linestyle=':')

# Plot the phase response
plt.subplot(2, 1, 2)
phi_d = np.angle(H_d)                     # Argument of H
phi_a = np.angle(H_a)
phi_d = np.unwrap(phi_d) * 180 / pi       # Remove discontinuities
phi_a = np.unwrap(phi_a) * 180 / pi       # and convert to degrees
plt.plot(w, phi_d, color='blue')
plt.plot(w, phi_a, color='green')  
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [°]')
plt.xlim(0, f_s / 2)
plt.ylim(-360, 0)
plt.yticks([-360, -270, -180, -90, 0])
plt.axvline(f_c, color='red')

plt.show()
