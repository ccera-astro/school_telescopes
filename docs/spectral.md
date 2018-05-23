<title>Spectral Data Display</title>

<img  alt="ORION" src="../orion_logo.png" width="100" height="25">
<hr>

# Spectral Data Display

This display shows the FFT-derived spectrum for both input channels. The units are in dB, relative to full-scale
for the receiver hardware in use, and are **not calibrated to any particular physical unit**.

The X-axis for this display can be either the receiver frequency, in MHz, or doppler velocity,
in km/sec, relative to the notional center-frequency.  No attempt is made to apply various
*standards of rest*, which is best left as an exercise in post-processing of the recorded data.

**Note** that this display shows the *raw* FFT spectrum of the input *prior* to
application of any [*frequency exclusions*](/Documents/exclusions.html).

## Controls
### Apply Baseline Subtraction

This control is used to subtract-out the instrumental response from the displayed spectral profile.
It is typically the case that the passband response for a receiver isn't completely "flat", and it may
also include unwanted RFI responses.  Enabling this control causes the display mechansim to
record a *baseline* and from that point forward subtract this baseline from the live data.

### Show Doppler

This control causes the X-axis to be displayed in km/sec, relative to the notional band-center.
No adjustments are made for any particular *standard of rest*.

### Peak Hold

This control causes an extra graph-line to be added which records peak responses from either the
**SKY** or **REF** data channels.

### Display Min

This control sets the minimum value displayed within the graph.
Exponential notation (e.g: 1.0e3) is allowed.

### Display Max

This control sets the maximum value displayed within the graph.
Exponental notation (e.g: 1.0e3) is allowed.
<hr>
<hr>
<img  alt="CCERA" src="../transparent-logo.png" width="150" height="35">
