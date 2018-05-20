<title>Frequency Exclusions Control</title>

<img  alt="CCERA" src="transparent-logo.png" width="100" height="25">

# Frequency Exclusions Control

This control is used to define a number of *zones of exclusion* when processing raw FFT
data from the [*receiver DSP chain*](/Documents/receiver.html).

These zones are typically the locations of RFI or other artifacts in the spectral data 
that the observer wishes to remove when generating derived data products.

The input format is *center frequency* **:** *bandwidth*.  Both of these are in *Hz*,
and exponential notation is encouraged (e.g. 600e6:10e3). There may be any number of
these *exclusions* defined, and they don't have to appear in frequency order. They
should be separated by a single **,** character.

This provides a very useful mechanism for observing over bandwidths that would otherwise
be prone to interference, by isolating zones of persistent *RFI* and discarding them.

This means that *Continuum* and *Correlation* calculations and derivations can be produced
without the perturbing influence of *RFI* artifacts.

