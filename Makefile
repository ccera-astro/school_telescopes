PYTARGETS=radiometer.py d1_spectral_logger.py
DOCTARGETS=docs/index.html docs/dformat.html docs/continuum.html docs/correlation.html \
docs/exclusions.html docs/spectral.html docs/receiver.html
LHTML=password.html expcontrol.html index.html real-time.html syscontrol.html
JSONS=experiments.json
LPY=astro_web.py moveto.py radiometer_helper.py d1_spectral_helper.py
IMGS=orion_logo.png radiometer.grc.png transparent-logo.png docs/dsp_diagram.png
JSCRIPTS=jquery.flot.axislabels.js  jquery.flot.js  jquery.flot.tooltip.js  jquery.js

%.html: %.md
	pandoc -o $@ $<

%.py: %.grc
	-grcc -d . $<

all: $(PYTARGETS) $(DOCTARGETS)

tarfile: all
	tar cvzf orion.tar.gz $(PYTARGETS) $(DOCTARGETS) $(LHTML) $(JSONS) $(LPY) $(IMGS) $(JSCRIPTS)
