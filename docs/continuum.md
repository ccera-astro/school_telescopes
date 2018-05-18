<title>Continuum Data Display</title>
# Continuum Data Display

This display shows the total detected power for the two input channels--**SKY** and **REF**. The total power displayed
is in arbitrary units as calculated by the [receiver *DSP* chain](/Documents/receiver-description.html).  That chain includes an *FFT* on both input channels,
and the total power is a scalar sum of each bin in the *FFT*, with the [frequency exclusions](/Documents/exclusions.html)
subtracted out. This allows for there to be in-band persistent *RFI* present at the input, but that *RFI* will not contribute
significantly to the final data products.

This display also shows the [*difference channel*](/Documents/differential.html), which is computed by subtracting
the **REF** channel from the **SKY**
channel. In some hardware scenarios, this provides a useful mechanism, similar to *Dicke Switching* to significantly
reduce contributions to output fluctuations from inherent system gain changes.   In such a setup, the two channels
use identical hardware *up front* (LNAs, LNBFs, etc).  The **SKY** channel observes the sky as seen by the antenna, while
the **REF** channel observes either a different section of *cold sky*, or a *reference termination* of some sort.  With
both channels containing identical hardware, in closely-related physical environments (temperature, etc), the changes
in gain due to environment will be very similar in both channels, and will be at least partially factored-out.

**Note** that for system configurations that don't meet the requirements for correct *differencing*, the *difference* channel
will not reflect meaningful data.  For example, in an [*interferometer*](/Documents/interferometer.html) system configuration,
the two antennae are typically located at some distance from one another, and are looking at the same patch of sky
In this case, any computed *difference* would not reflect sky objects, but shifts in operating conditions of one of the channels.

## Controls
### Continuum Data Scaling

This control is used to perform a simple scaling operation on the relevant data prior to display.  It has **no** effect
on the logged data, only on the data displayed via this webpage.  Exponential notation (e.g.: 1.0e3) is allowed.

### Offset

This control is used to apply an offset **after** the data have been scaled using the above 
scaling control.

### Display Min

This control sets the minimum value of the displayed data.
Exponential notation (e.g.: 1.0e3) is allowed.

### Display Max

This control sets the maximum value of the displayed data.
Exponential notation (e.g.: 1.0e3) is allowed.
