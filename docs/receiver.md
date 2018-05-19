<title>Receiver DSP Flow</title>

# Receiver DSP Flow

## Overview
The receiver for the *Combo Radiometer* application starts by taking a 1024-bin FFT for each
receiver channel, using a Blackmann-Harris window.

Once this is done, other products are derived from the two FFT outputs, including:

* Power estimates for each channel (via conversion to Mag**2)
* The cross-product of the two FFTs, using complex-conjugate multiplication
* A synthetic *difference* channel, from the power estimates
* Spectral profile for both input channels

Note that all the derived products are integrated over a time period
specified by the experiment profile in use.

These products are all [*logged*](/Documents/logging.html) into archival
files in a .csv format, as well as *current data* files in a .json format.
The *current data* files are used to feed the real-time displays via a
web browser.

## Notes

These operations are performed whether the attached hardware receiver(s)
are appropriate for the configuration or not.  In a hardware configuration
where there is only a single-channel receiver, the 2nd, **REF** channel
simply contains zeros, which implies that the *difference* and
*correlation* outputs will not contain meaningful data.

In a configuration where there are two non-mutually-coherent receivers,
the *difference* output will contain meaningful data, but the
*correlation* output will not.
