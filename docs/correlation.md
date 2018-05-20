<title>Correlator Data Display</title>

<img  alt="CCERA" src="transparent-logo.png" width="100" height="25">

# Correlator Data Display

This display shows the single-lag *correlation* between the **SKY** and **REF** channels, as a scalar number.  This is
derived from the sum of the bins that result from multiplying the **SKY** FFT with the complex-conjugate of the
**REF** side FFT, minus any [*exclusions*](/Documents/exclusions.html).

The two traces are the *real* and *imaginary* (or *cos* and *sin*) components of the cross multiply.  The units
are arbitrary.

## Controls

### Correlation Data Scaling

This control sets a scaling value for the input data, prior to display.
Exponential notation (e.g.: 1.0e3) is allowed.

### Display Min

This control sets the minimum value displayed within the graph.
Exponential notation (e.g: 1.0e3) is allowed.

### Display Max

This control sets the maximum value displayed within the graph.
Exponental notation (e.g: 1.0e3) is allowed.


