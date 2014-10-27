# Where is the Python to JS translator
export PYTHONJS = $(HOME)/PythonJS

# To recompile PythonJS :
#   (cd PythonJS/pythonjs ; ./pythonjs.py --runtime)

# To debug JS :
#    node debug xxx_rhino.js
# And 'c' to continue

all:regtest_python tomuss_python.js tomuss_python_O.js regtest_js regtest_js_O stats

OBJS = preamble.py filter.py average.py maximum.py nmbr.py cow.py diff_date.py weighted_percent.py
REGTEST = regtest.py filter_regtest.py average_regtest.py maximum_regtest.py nmbr_regtest.py diff_date_regtest.py weighted_percent_regtest.py
PYJS = PythonJS/pythonjs/translator.py --no-wrapper

LOCAL=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then ls ../LOCAL/LOCAL_PYTHON_JS/*.py | grep -v regtest ; fi)
LOCAL_REGTEST=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then echo ../LOCAL/LOCAL_PYTHON_JS/*_regtest.py ; fi)

TRANSLATE = f() { \
if [ -f PythonJS/pythonjs/translator.py ] ; \
then \
echo "Python translation to JavaScript:" $(OBJS) $$2 $$1 ; \
(  \
sed -e "s/$$1/'''/" $(OBJS) $(LOCAL) $$2 | tee xxx.debug | \
$(PYJS) \
) >$@ ; \
else \
$(MAKE) warning ; \
fi ; } ; f

NODE = export NODE_MODULE_CONTEXTS=1 ; node

warning:
	@echo "==============================================================="
	@echo "PythonJS not installed: no Python to JavaScript translation"
	@echo "You are using the staticaly translated JS from the tarball"
	@echo "To install the translator, run:  cd PYTHON_JS ; make PythonJS"
	@echo "You need to install node.js in order to make regression tests"
	@echo "==============================================================="

PythonJS:
	@echo "Cloning PythonJS repository, checkout a working version"
        git clone https://github.com/PythonJS/PythonJS.git
	cd PythonJS ; git checkout b1f7bf044c48eb296bf919dea99eb0e251a35e8a

update:
	cd PythonJS ; git pull https://github.com/PythonJS/PythonJS.git

tomuss_python.py:$(OBJS)
	@cat $(OBJS) >$@

tomuss_python.js:$(OBJS) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#'

tomuss_python_O.js:$(OBJS) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#'

tomuss_python_regtest.js:$(OBJS) $(REGTEST) $(LOCAL_REGTEST) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#' "$(REGTEST) $(LOCAL_REGTEST)"

tomuss_python_regtest_O.js:$(OBJS) $(REGTEST) $(LOCAL_REGTEST) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#' "$(REGTEST) $(LOCAL_REGTEST)"

regtest: PythonJS regtest_python regtest_js regtest_js_O

regtest_python:
	@echo "Running regression tests in Python"
	@cat $(OBJS) $(LOCAL) $(REGTEST) $(LOCAL_REGTEST) >xxx.py;python xxx.py
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
	@wc $(OBJS) tomuss_python*.js

clean:
	# Do not delete tomuss_python_O.js, it may be not buildable
	-rm tomuss_python.js tomuss_python_regtest.js tomuss_python_regtest_O.js xxx*

xxx_tomuss.js:Makefile ../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js
	@echo 'window = { location:""} ; ' >$@
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

