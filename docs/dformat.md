<title>Data Formats</title>

<img  alt="ORION" src="../orion_logo.png" width="100" height="25">
<hr>

# Data Logging Formats

Data of various kinds are logged in .csv files, with fields separated by ",".  This makes it
convenient for certain programs, like common spreadsheet programs, to process the data as
columns.

Scalar data (individual channels, cross-power, and differential power) are logged every 5 seconds,
while vector data (spectral estimtes, etc), are logged every 45 seconds.

# Data log locations

Data are logged onto the local "disk" (usually a USB stick or SSD), and the system takes care of mounting
the device onto the */home/astronomer/data* directory.  Optionally, the experiment may be configured to
include logging to a SAMBA share, which always appears at */home/astronomer/rdata*.

Each file is named:

*EXPNAME*-**YYYYMMDD**-tp.csv

For notional "scalar" data, and:

*EXPNAME*-**YYYYMMDD**-spec.csv

Where *EXPNAME* is the name of the experiment assigned, when it was created.

# Scalar (-tp) data file

The scalar data file contains scalar values like the total power for each channel, etc.  It is organized into columns:

* UTC-HOUR
* UTC-MINUTE
* UTC-SECOND
* LMST-HOUR
* LMST-MINUTE
* LMIST-SECOND
* FREQUENCY-IN-MHZ
* DECLINATION
* SKY-REF
* SKY
* REF
* SKY*REF (COS)
* SKY*REF (SIN)

# Vector (FFT) data file

The vector data file format contains vector values from FFT data, it is organized into columns:

* UTC-HOUR
* UTC-MINUTE
* UTC-SECOND
* LMST-HOUR
* LMST-MINUTE
* LMIST-SECOND
* FREQUENCY-IN-MHZ
* DECLINATION
* BANDWIDTH-IN-MHZ
* 1024 dB-VALUES...

<hr>
<hr>
<img  alt="CCERA" src="../transparent-logo.png" width="150" height="35">
