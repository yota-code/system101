#include <inttypes.h>

#ifndef M_PI
	#define M_PI ((double)(0x3.243f6a8885a308dp0))
#endif

#define FILTER_ORDER (2)

typedef struct {
	double b[FILTER_ORDER + 1];
	double a[FILTER_ORDER + 1];
	double x[FILTER_ORDER + 1];
	double y[FILTER_ORDER + 1];
	uint8_t p;
} iir_2_C;

#define X(i) (self->x[(self->p + (i)) % (FILTER_ORDER + 1)])
#define Y(i) (self->y[(self->p + (i)) % (FILTER_ORDER + 1)])

#define A(i) (self->a[(i)])
#define B(i) (self->b[(i)])

#define PUSH(x0) { \
	self->p = (self->p + FILTER_ORDER) % (FILTER_ORDER + 1); \
	X(0) = (x0); \
}

#define MOD_360(x) (fmod((fmod(x, 360.0) + 360.0), 360.0))
#define MOD_180(x) ( 180.0 <= MOD_360(x) ) ? ( MOD_360(x) - 360.0 ) : ( MOD_360(x) )

typedef enum {
	WrappingMode_360=0,
	WrappingMode_180=1
} WrappingMode_E;

void iir_2_butterworth(iir_2_C * self, double fc, double fs, double ini_value) ;
double iir_2_direct_form_I(iir_2_C * self, double x0) ;
double iir_2_direct_form_I_wrapped(iir_2_C * self, double x0, WrappingMode_E mode) ;
