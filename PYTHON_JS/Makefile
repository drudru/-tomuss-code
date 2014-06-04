# Where is the Python to JS translator
export PYTHONJS = $(HOME)/PythonJS

# To recompile PythonJS :
#   (cd PythonJS/pythonjs ; ./pythonjs.py --runtime)

# To debug JS :
#    node debug xxx_rhino.js
# And 'c' to continue

all:regtest_python tomuss_python.js tomuss_python_O.js regtest_js regtest_js_O stats

OBJS = preamble.py filter.py average.py
REGTEST = filter_regtest.py average_regtest.py
PYJS = PythonJS/pythonjs/translator.py --no-wrapper

TRANSLATE = f() { echo "Python translation to JavaScript:" $(OBJS) $$2 $$1 ; \
                  (  \
		  cat patch.js ; \
                  sed -e "s/__OR__/$$(cat xxx_or)/g" \
                      -e "s/$$1/'''/" $(OBJS) $$2 | tee xxx.debug | \
                  $(PYJS) \
                  ) >$@ ; } ; \
            f

NODE = export NODE_MODULE_CONTEXTS=1 ; node

xxx_or:../TRANSLATIONS/*/*/tomuss.po PythonJS
	@python -c 'import tomuss_init ; from .. import utilities ; print utilities._("or")' >$@ 2>/dev/null
	@echo "The 'or' keyword in filters is '$$(cat xxx_or)'"
	@echo "Do not modify this once this keyword has been stored in tables"

PythonJS:
	@echo "Cloning PythonJS repository, checkout a working version"
        git clone https://github.com/PythonJS/PythonJS.git
	cd PythonJS ; git checkout b1f7bf044c48eb296bf919dea99eb0e251a35e8a

update:
	cd PythonJS ; git pull https://github.com/PythonJS/PythonJS.git

tomuss_python.js:xxx_or $(OBJS) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#'

tomuss_python_O.js:xxx_or $(OBJS) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#'

tomuss_python_regtest.js:xxx_or $(OBJS) $(REGTEST) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#' "$(REGTEST)"

tomuss_python_regtest_O.js:xxx_or $(OBJS) $(REGTEST) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#' "$(REGTEST)"

regtest: PythonJS regtest_python regtest_js regtest_js_O

regtest_python:
	@echo "Running regression tests in Python"
	@cat $(OBJS) $(REGTEST) >xxx.py ; python xxx.py
	@echo

regtest_js:tomuss_python_regtest.js xxx_tomuss.js
	@echo "Running regression tests for JavaScript with 'node'"
	@$(NODE) tomuss_python_regtest.js
	@echo

regtest_js_O:tomuss_python_regtest_O.js
	@echo "Running regression tests for optimized JavaScript with 'node'"
	@cat xxx_tomuss.js tomuss_python_regtest_O.js >xxx.js
	@$(NODE) xxx.js
	@echo

stats:
	@wc $(OBJS) tomuss_python*.js

clean:
	-rm tomuss_python.js tomuss_python_O.js xxx*

xxx_tomuss.js:Makefile
	@echo 'window = { location:""} ; ' >$@
	@echo 'navigator = { } ; ' >>$@
	@echo 'var today = "20140101" ;' >>$@
	@cat ../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js >>$@

# check TOMUSS database to search for problems

xxx_compatibility_check.js:compatibility.py
	./compatibility.py >$@

compatibility_check:regtest_js_O xxx_compatibility_check.js xxx_tomuss.js
	@echo "Check compatibility with existing filters in TOMUSS DB"
	@cat xxx_tomuss tomuss_python_regtest_O.js xxx_compatibility_check.js >>xxx.js
	@A="$$($(NODE) xxx.js | grep BUG)" ; \
	if [ "" = "$$A" ] ; \
            then echo "$@ OK" ; \
            else echo "$@ **** FAILED ****" ; echo "$$A" ; exit 1 ; \
        fi

# Only for personnal testing

test:
	$(PYJS) test.py >xxx.js
	$(NODE) xxx.js

