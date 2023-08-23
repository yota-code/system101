#ifndef INCLUDE_fir_filter_H
#define INCLUDE_fir_filter_H

typedef struct {
	size_t pos;
	float value[length];
	float coeff[length];
} fir_filter_8_T;

#define fir_filter_define_(length) typedef struct { \\
	size_t pos; \\
	size_t len; \\
	float value[length]; \\
	float coeff[length]; \\
} fir_filter_ ## length ## _T

#define fir_filter_declare_(length, name) \\
	fir_filter_ ## length ## _T name = { 0 }; \\
	name.len = length;

#endif
