#include <tgmath.h>
#include <string.h>

#ifdef AUTOTEST
#include <stdio.h>
#endif

#include "iir_filter_2.h"

void iir_2_butterworth(iir_2_C * self, double fc, double fs, double ini_value) {

	memset(self, 0, sizeof(iir_2_C));

	if (ini_value != 0.0) {
		for (int i=0 ; i<3 ; i++) {
			self->x[i] = ini_value;
			self->y[i] = ini_value;
		}
	}

	double g = 1 / tan(M_PI * fc / fs);

	double a0 = g*g + sqrt(2)*g + 1;

	A(0) = 1.0;
	A(1) = (2 - 2*g*g) / a0;
	A(2) = (g*g - sqrt(2)*g + 1) / a0;

	B(0) = 1 / a0;
	B(1) = 2 / a0;
	B(2) = 1 / a0;

}

double iir_2_direct_form_I(iir_2_C * self, double x0) {

	double num = 0.0;
	double den = 0.0;

	PUSH(x0);

	for (int i=0 ; i<(FILTER_ORDER + 1) ; i++) {
		num += B(i) * X(i);
	}
	for (int i=1 ; i<3 ; i++) {
		den += A(i) * Y(i);
	}

	return (Y(0) = num - den);

}

#ifdef AUTOTEST

int main(int argc, char * argv[]) {

	iir_2_C u = {};

	iir_2_butterworth(& u, 45, 360, 0.0);

	for (int i=0 ; i<25 ; i++) {
		double x = (i < 5) ? (0.0) : (1.0);
		double y = iir_2_direct_form_I(&u, x);
		printf("%f\t%f\n", x, y);
	}

}

#endif