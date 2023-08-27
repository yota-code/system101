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

	return ( Y(0) = num - den );

}

double iir_2_direct_form_I_wrapped(iir_2_C * self, double x0, WrappingMode_E mode) {

	double num = 0.0;
	double den = 0.0;

	PUSH(( mode == WrappingMode_180 ) ? ( MOD_180(x0) ) : ( MOD_360(x0) ));

	double d = X(0) - X(1);
	double w = 0.0;
	if (180.0 < fabs(d)) {
		w = copysign(360.0, d);
		for (int i=1 ; i<(FILTER_ORDER + 1); i++) {
			X(i) += w;
			Y(i) += w;
		}
	}

	for (int i=0 ; i<(FILTER_ORDER + 1) ; i++) {
		num += B(i) * X(i);
	}
	for (int i=1 ; i<3 ; i++) {
		den += A(i) * Y(i);
	}

	Y(0) = num - den;

	return (( mode == WrappingMode_180 ) ? ( MOD_180(Y(0)) ) : ( MOD_360(Y(0)) ));

}

#ifdef AUTOTEST

int main(int argc, char * argv[]) {

	iir_2_C u = {};

	iir_2_butterworth(& u, 45, 360, 170.0);

	for (int i=0 ; i<25 ; i++) {
		double x = (i < 5) ? (170.0) : (-170.0);
		//double y = iir_2_direct_form_I(&u, x);
		double y = iir_2_direct_form_I_wrapped(&u, x, WrappingMode_180);
		printf("%d\t%f\t%f\n", i, x, y);
	}

	iir_2_butterworth(& u, 45, 360, 10.0);

	for (int i=0 ; i<25 ; i++) {
		double x = (i < 5) ? (10.0) : (-10.0);
		//double y = iir_2_direct_form_I(&u, x);
		double y = iir_2_direct_form_I_wrapped(&u, x, WrappingMode_360);
		printf("%d\t%f\t%f\n", i, x, y);
	}

	iir_2_butterworth(& u, 45, 360, 10.0);

	for (int i=0 ; i<25 ; i++) {
		double x = (i < 5) ? (10.0) : (-10.0);
		//double y = iir_2_direct_form_I(&u, x);
		double y = iir_2_direct_form_I(&u, x);
		printf("%d\t%f\t%f\n", i, x, y);
	}

}

#endif