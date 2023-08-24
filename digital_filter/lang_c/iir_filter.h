#ifndef INCLUDE_irr_filter_H
#define INCLUDE_irr_filter_H

typedef struct {
	size_t length;
	double * num;
	double * den;
	double * line;
	size_t pos;
	double input;
	double output;
} iir_dtcr_C;

#define iir_dtcr__declare__(len, name, num, den) \
	double iir_ ## name ## _num[len + 1] = num; \
	double iir_ ## name ## _den[len + 1] = den; \
	double iir_ ## name ## _line[len + 1] = {0}; \
	\
	iir_dtcr_C iir_ ## _filter = { len, \
		iir_ ## name ## _num, iir_ ## name ## _den, iir_ ## name ## _line, \
		0, 0.0, 0.0 \
	};

	
double iir_dtcr_run(iir_dtcr_C * self, double x) ;	
	
#endif