# Where is the Python to JS translator
export PYTHONJS = $(HOME)/PythonJS
# git clone https://github.com/PythonJS/PythonJS.git

# To recompile PythonJS :
#   cd tests ; ./server.py --regenerate-runtime

# To debug JS :
#    node debug xxx_rhino.js
# And 'c' to continue

all:regtest_python tomuss_python.js tomuss_python_O.js regtest_js regtest_js_O stats

OBJS = filter.py
REGTEST = filter_regtest.py
PYJS = PythonJS/pythonjs/translator.py --no-requirejs

TRANSLATE = f() { echo "Python translation to JavaScript:" $(OBJS) $$2 $$1 ; \
                  (  \
		  cat patch.js ; \
                  sed -e "s/__OR__/$$(cat xxx_or)/g" \
                      -e 's/$$1/"""/' $(OBJS) $$2 | tee xxx.debug | \
                  $(PYJS) \
                  ) >$@ ; } ; \
            f

xxx_or:../TRANSLATIONS/*/*/tomuss.po
	@python -c 'import tomuss_init ; from .. import utilities ; print utilities._("or")' >$@ 2>/dev/null
	@echo "The 'or' keyword in filters is '$$(cat xxx_or)'"
	@echo "Do not modify this once this keyword has been stored in tables"

$(PYJS):
	@echo "Cloning PythonJS repository, checkout a working version"
	@if [ ! -d PythonJS ]; \
	then git clone https://github.com/PythonJS/PythonJS.git ; \
        git checkout b4a588e213a29b88ca4e60e2c1fc31f91530d4c1 ; \
	fi

tomuss_python.js:xxx_or $(PYJS) $(OBJS) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#'

tomuss_python_O.js:xxx_or $(PYJS) $(OBJS) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#'

tomuss_python_regtest.js:xxx_or $(PYJS) $(OBJS) Makefile
	@$(TRANSLATE) '#WITHJAVASCRIPT#' $(REGTEST)

tomuss_python_regtest_O.js:xxx_or $(PYJS) $(OBJS) Makefile
	@$(TRANSLATE) '#WITHOUTJAVASCRIPT#' $(REGTEST)

regtest: regtest_python regtest_js regtest_js_O

regtest_python:
	@echo "Running regression tests in Python"
	@python ./filter.py

regtest_js:tomuss_python_regtest.js
	@echo "Running regression tests for JavaScript with 'node'"
	@node tomuss_python_regtest.js

regtest_js_O:tomuss_python_regtest_O.js
	@echo "Running regression tests for optimized JavaScript with 'node'"
	@node tomuss_python_regtest_O.js

stats:
	@wc $(OBJS) tomuss_python*.js

clean:
	-rm tomuss_python.js tomuss_python_O.js xxx*

# check TOMUSS database to search for problems

xxx_compatibility_check.js:compatibility.py
	./compatibility.py >$@

compatibility_check:regtest_js_O xxx_compatibility_check.js
	@echo "Check compatibility with existing filters in TOMUSS DB"
	@echo 'window = { location:""} ; ' >xxx.js
	@echo 'navigator = { } ; ' >>xxx.js
	@echo 'var today = "20140101" ;' >>xxx.js
	@cat ../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js tomuss_python_regtest_O.js xxx_compatibility_check.js >>xxx.js
	@A="$$(node xxx.js | grep BUG)" ; \
	if [ "" = "$$A" ] ; \
            then echo "$@ OK" ; \
            else echo "$@ **** FAILED ****" ; echo "$$A" ; exit 1 ; \
        fi

# Only for personnal testing

test:
	$(PYJS) test.py >xxx.js
	node xxx.js

