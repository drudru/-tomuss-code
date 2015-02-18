# To debug JS :
#    node debug xxx.js
# And 'c' to continue

all:regtest_python tomuss_python.js tomuss_python_O.js regtest_js regtest_js_O stats

OBJS = filter.py average.py maximum.py nmbr.py cow.py diff_date.py weighted_percent.py product.py
OBJS_JS = preamble.py preamble_js.py $(OBJS)
OBJS_PYTHON = preamble.py preamble_python.py $(OBJS)
REGTEST = regtest.py *_regtest.py

PYJS = RapydScript/bin/rapydscript --prettify --bare


LOCAL=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then ls ../LOCAL/LOCAL_PYTHON_JS/*.py | grep -v regtest ; fi)
LOCAL_REGTEST=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then echo ../LOCAL/LOCAL_PYTHON_JS/*_regtest.py ; fi)

TRANSLATE = f() { \
if [ -f RapydScript/bin/rapydscript ] ; \
then \
echo "Python translation to JavaScript:" $(OBJS_JS) $$2 $$1 ; \
(  \
sed -e "s/$$1/'''/" $(OBJS_JS) $(LOCAL) $$2 | tee xxx.debug | \
$(PYJS) \
) >$@ ; \
else \
$(MAKE) warning ; \
fi ; } ; f

NODE = export NODE_MODULE_CONTEXTS=1 ; node

warning:
	@echo "==============================================================="
	@echo "RapydScript not installed: no Python to JavaScript translation"
	@echo "You are using the staticaly translated JS from the tarball"
	@echo "To install the translator, run:  cd PYTHON_JS ; make translator"
	@echo "You need to install node.js in order to make regression tests"
	@echo "==============================================================="

translator:
	@echo "Cloning translator repository, checkout a working version"
	if [ ! -d RapydScript ] ; \
	then \
        git clone git://github.com/atsepkov/RapydScript.git ; \
	cd RapydScript ; \
	git checkout d2897bc844bdc5c15c051eb4c9cb68ece982f2c0 ; \
	fi

tomuss_python.py:$(OBJS_PYTHON) $(LOCAL) Makefile
	@cat $(OBJS_PYTHON) $(LOCAL) >$@

tomuss_python.js:$(OBJS_JS) $(LOCAL) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#'

tomuss_python_O.js:$(OBJS_JS) $(LOCAL) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#'

tomuss_python_regtest.js:$(OBJS_JS) $(REGTEST) $(LOCAL) $(LOCAL_REGTEST) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#' "$(REGTEST) $(LOCAL_REGTEST)"

tomuss_python_regtest_O.js:$(OBJS_JS) $(REGTEST) $(LOCAL) $(LOCAL_REGTEST) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#' "$(REGTEST) $(LOCAL_REGTEST)"

regtest: translator regtest_python regtest_js regtest_js_O

regtest_python:
	@echo "Running regression tests in Python"
	@cat $(OBJS_PYTHON) $(LOCAL) $(REGTEST) $(LOCAL_REGTEST) >xxx.py;python xxx.py
	@echo

regtest_js:tomuss_python_regtest.js xxx_tomuss.js
	@echo "Running regression tests for JavaScript with 'node'"
	@cat xxx_tomuss.js tomuss_python_regtest.js >xxx.js
	@$(NODE) xxx.js
	@echo

regtest_js_O:tomuss_python_regtest_O.js xxx_tomuss.js
	@echo "Running regression tests for optimized JavaScript with 'node'"
	@cat xxx_tomuss.js tomuss_python_regtest_O.js >xxx.js
	@$(NODE) xxx.js
	@echo

stats:
	@wc $(OBJS_JS) tomuss_python*.js

clean:
	@echo "Do not delete tomuss_python_O.js, it may be not buildable"
	@-rm tomuss_python.js tomuss_python_regtest.js tomuss_python_regtest_O.js xxx*

xxx_tomuss.js:Makefile ../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js
	@echo 'window = { "location":""} ; ' >$@
	@echo 'navigator = { } ; ' >>$@
	@echo 'var today = "20140101" ;' >>$@
	@cat ../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js >>$@

difference.js:difference.py xxx_tomuss.js Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#' "regtest.py difference.py"
	@cat xxx_tomuss.js difference.js >xxx.js
	@$(NODE) xxx.js
	@echo

# Only for personnal testing

test:
	$(PYJS) test.py >xxx.js
	$(NODE) xxx.js

