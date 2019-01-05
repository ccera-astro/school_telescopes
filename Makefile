PYTARGETS=radiometer.py d1_spectral_logger.py
DOCTARGETS=docs/index.html docs/dformat.html docs/continuum.html docs/correlation.html \
docs/exclusions.html docs/spectral.html docs/receiver.html docs/expcontrol.html
LHTML=password.html expcontrol.html index.html real-time.html syscontrol.html
JSONS=experiments.json default.json
LPY=astro_web.py moveto.py radiometer_helper.py d1_spectral_helper.py runexp.py
IMGS=orion_logo.png radiometer.grc.png transparent-logo.png docs/dsp_diagram.png
JSCRIPTS=jquery.flot.axislabels.js  jquery.flot.js  jquery.flot.tooltip.js  jquery.js
SHSCRIPTS=rc.local

%.html: %.md
	pandoc -o $@ $<

%.py: %.grc
	-grcc -d . $<


all: $(PYTARGETS) $(DOCTARGETS)

clean:
	rm -f docs/*.html
	rm -f $(PYTARGETS)

docs: $(DOCTARGETS)

apps: $(PYTARGETS)


tarfile: all
	tar cvzf orion.tar.gz $(PYTARGETS) $(DOCTARGETS) $(LHTML) $(JSONS) $(LPY) $(IMGS) $(JSCRIPTS) $(SHSCRIPTS) Makefile

install: all
	mkdir -p Documents
	cp $(DOCTARGETS) Documents
	cp runexp.py runexp
	chmod 755 runexp runexp.py

sysinstall:
	cp rc.local /etc
	chmod 755 /etc/rc.local
