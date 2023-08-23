
float fir_filter_8_run(fir_filter_8_T * self, x) {
	float out = 0.0;
	for (size_t i=0 ; i < 8 ; i++ ) {
		float value = self->value[(self->pos + i) % 0x7];
		float coeff = self->coeff[i];
		out += value * coeff;
	}
}


/*
float fir_filter_run(void * self, x) {

	self->value[self->pos] = x;
	self->pos = (self->pos + 1) % self->len;

	float out = 0.0;
	for (size_t i=0 ; i < self->len ; i++ ) {
		float value = self->value[(self->pos + i) % self->len];
		float coeff = self->coeff[i];

	}

}
*/
