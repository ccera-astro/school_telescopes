<title>Intro: Integrated Radio Telscope Receiver System</title>

<img  alt="ORION" src="../orion_logo.png" width="100" height="25">
<hr>

# Introduction

The **ORION** radio astronomy observing platform represents state-of-the-art technology
in *Software Defined Radio* systems for the amateur and similar
small-scale radio astronomy projects.

# Receiver Subsystem

The receiver subsystem currently supports the following list of SDR hardware
configurations:

* A single LimeSDR-USB
* A single LimeSDR-Mini
* A single RTLSDR
* Two RTLSDR
* A Single USRP B210
* A Single USRP1 with TVRX2 card
* A single USRP B205mini
* Two USRP B205minis

The DSP flows supported currently include:

* [**Combo Radiometer**](receiver.html) providing two-channel *total-power, differential, correlation and spectral* data products with
   an advanced spectral mask. There is also a *fast* version of this combo radiometer, which supports a purely-scalar correlator
   architecture, and can thereby support higher sample rates.

In the future there will be support for:

* A pulsar mode


# Real time display

The **ORION** platform provides semi-real-time display of various data products via the data display page.
The page is broken into 3 sections:

* [*Continuum*](continuum.html)
* [*Correlation*](correlation.html)
* [*Spectral*](spectral.html)

# Data logging

Experiment data products are [*logged*](dformat.html) at useful time intervals, and saved both locally, and optionally to a
SAMBA/CIFs share, which is defined at experiment creation time.




<hr>
<hr>
<img  alt="CCERA" src="../transparent-logo.png" width="150" height="35">
