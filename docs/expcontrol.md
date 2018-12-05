<title>Experiment Controls</title>

<img  alt="ORION" src="../orion_logo.png" width="100" height="25">
<hr>

# Experiment Control Page
The experiment control page allows you to configure and start/stop/save 
experiment profiles in an intuitive and concise way.

# Experiment Definition

This is the first section of the page that allows you to define an
experiment profile, and save that profile for later, or immediate
execution.

<hr>

## Sample Rate/Type/Frequency

* **Sample rate**
    This "radio button" area allows you to select from a number of
    hardware-appropriate sample-rates.  Select a rate that is useful for
    your experiment.  The actual useful observing bandwidth will be somewhat-less
    than the sample-rate, due to filter roll-off, etc.

* **Experiment type**
    This area allows you to select the type of experiment to run. There are a
    few different experiment types, and as the software matures, new experiment
    types will be added.  Select an appropriate experiment type:

    * *Combo Radiometer* -- an FX-based two-channel correlator with differential support
    * *Fast Combo Radiometer* -- as above, but with the FX architecture, and thus faster
    * *D1 Spectometer* -- a special 3-channel spectrometer mode for searching/monitoring the
Deuterium spectral line.


* **Spectral logging**
    This checkbox controls whether spectral components will be logged in data-files
    or not.  It is ofen the case that spectral information conveys nothing of
    long-term interest, so this option is provided to save storage space.

* **Tuner center frequency**
    This control allows you to enter the center frequency for the tuner(s) in
    the radio(s).  Standard engineering notation is accepted here.

<hr>

## Experiment name and other information

* **Experiment name**
    Enter a name you wish to assign to your experiment.  It is best to
    use only alpha-numerics.

* **Remote logging share**
    This entry is optional, and allows you to log data to a CIFS share. Use the
    standard CIFS share format *//hostname/sharename*.

* **Remote logging username**
    Enter your username associated with the above share.

* **Remote logging password**
    Enter the password associated with the above share.

* **Declination target**
    Enter the desired "target" declination for the observation

* **Local longitude**
    Enter the local longitude of the observatory
    
* **Local latitude**
    Enter the local latitude of the observatory
    
* **Baseline distance**
    For interferometer observations, enter the E-W baseline distance, in
    meters. This is used to calculate a high-pass filter for the correlator
    output.

* **Integration time**
    Choose a suitable integration time, in seconds. You can either use the
    convenient up/down controls, or enter a number directly.

* **Frequency exclusions**
    This section allows you to enter a list of excluded frequencies when using
    the *Combo Radiometer* experiment type.  These frequencies will be excluded
    prior to other calculations being performed on the data. The data are entered as
    a **comma-separated list** of *frequency:bandwidth*, with both components in *Hz*.
    Use of engineering notation is supported.
    
* **Save profile**
    This checkbox allows you to specify that the profile be saved under its
    *Experiment Name* prior to execution.
    
* **Save to system startup**
    This checkbox allows you to ask the system to re-start this experiment if
    and when the system reboots.

* **Experiment notes**
    This area allows you to enter experiment specific notes, which will be saved
    in a "notes" file along with real-time data.

* **Start**
    This button causes the system to begin execution of your experiment, based on
    the entered profile parameters.

<hr>

# Experiment and profile management

## Stop experiment

This subsection allows you to stop the currently executing experiment, and view
any error-log information associated with the experiment.

* **Stop**
    This control stops the currently executing (if any) experiment.

## Restart saved experiment profile

This subsection allows you to re-start a named experiment, based on its saved
profile name. A list of existing saved profiles is provided.

* **Restart**
    The control causes the named experiment to be re-started, including stopping
    any existing experiment that may currently be executing.
    
<hr>
<hr>
<img  alt="CCERA" src="../transparent-logo.png" width="150" height="35">
