ptrprobe
========

Simple Python script to probe and record bed level compensation (for Marlin / PrintrBot - Metal)

### Purpose
Probe the bed level at a set of locations and append the results to a file.  You can use these results to evaluate the flatness of your bed, the stability of the bed level probing or the impact of the temperature. 
Beware: the measurements may be impacted by the proximity of other metalic parts, the temperature of the probe iself, or any other factor I do not know, so take the results with a grain of salt.

### Limitations
This script has currenlty no command line or configuration options. You must edit it to suits your needs.  You may also need to setup a proper environment.  

This was tested on a PrintrBot Simple Metal using Marlin firmware only. The probe MUST have been properly calibrated first, you do not want it to enter in collision with the bed.

Feel free to fork and enhance or contribute.

### Usage
The following steps works in my environment, adapt as needed.
* I copy the script in the root directory of octopi on a Raspberry PI (see https://github.com/guysoft/OctoPi) 
* I Execute the script via ``/home/pi/oprint/bin/python probe.py`` in the octopi home directory. 
* The results are appended in the csv file ``probes.csv`` (see an example in this repository).
My results show that the impact of the temperature is negligible (unlike what I thoung after a couple of non systematic tests).

