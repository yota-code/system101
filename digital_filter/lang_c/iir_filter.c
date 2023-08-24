


double iir_dtcr_run(iir_dtcr_C * self, double x) {
	double y = 0.0;
	/* first operation */
	self->line[self->pos] = x * self->num[self->len] - y * self.den[self->len];
	/* intermediate operations */
	for (size_t i=self->len ; i > 0 ; i--) {
		size_t j = (i + self->pos) % self->len;
		self->line[i] = 
			  x * self->num[i]
			- y * self.den[i]
			+ self->line[(self->pos + 1) % self->len];
	}
	/* final operation */
	y = x * self.num[0] + self->line[self->pos];
	
}

int main(int argc, char * argv[]) {

	iir_dtcr__declare__(3, test,
		{0.0088, 0.0263, 0.0263, 0.0088},
		{1.0, -2.2343, 1.8758, -0.5713}
	);

	
}