# To debug JS :
#    node debug xxx.js
# And 'c' to continue

all:regtest_python tomuss_python.js regtest_js stats tomuss_python.py

OBJS = filter.py average.py maximum.py nmbr.py cow.py diff_date.py weighted_percent.py product.py places.py if_else.py
OBJS_JS = preamble.py preamble_js.py $(OBJS)
OBJS_PYTHON = preamble.py preamble_python.py $(OBJS)
REGTEST = regtest.py *_regtest.py
JS=../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js

LOCAL=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then ls ../LOCAL/LOCAL_PYTHON_JS/*.py | grep -v regtest ; fi)
LOCAL_REGTEST=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then echo ../LOCAL/LOCAL_PYTHON_JS/*_regtest.py ; fi)

RAPYDSCRIPT_COMMIT=0483fac4745bca9c531d29963f2daca5e3330e7c
translator:
	@if [ ! -d RapydScript ] ; \
	then \
		echo "Cloning Python->JS translator repository." ; \
		git clone https://github.com/atsepkov/RapydScript.git ; \
		cd RapydScript ; \
		git checkout $(RAPYDSCRIPT_COMMIT) ; \
	fi
	@cd RapydScript ; \
	if [ $$(git rev-parse HEAD) != $(RAPYDSCRIPT_COMMIT) ] ; \
	then \
		echo "Updating Python->JS translator." ; \
		$(MAKE) clean ; \
		git fetch ; \
		git checkout $(RAPYDSCRIPT_COMMIT) ; \
	fi

tomuss_python.py:$(OBJS_PYTHON) $(LOCAL) Makefile
	@cat $(OBJS_PYTHON) $(LOCAL) >$@

tomuss_python.js:translator $(OBJS_JS) $(LOCAL) Makefile
	@./python_to_js "$(OBJS_JS) $(LOCAL)" $@

tomuss_python_regtest.js:translator $(OBJS_JS) $(REGTEST) $(LOCAL) $(LOCAL_REGTEST) Makefile
	@./python_to_js "$(OBJS_JS) $(LOCAL) $(REGTEST) $(LOCAL_REGTEST)" $@

regtest: regtest_python regtest_js

regtest_python:
	@echo "Running regression tests in Python"
	@cat $(OBJS_PYTHON) $(LOCAL) $(REGTEST) $(LOCAL_REGTEST) >xxx.py;python3 xxx.py
	@echo

regtest_js:tomuss_python_regtest.js xxx_tomuss.js
	@echo "Running regression tests for JavaScript with 'node'"
	@cat xxx_tomuss.js tomuss_python_regtest.js >xxx.js
	@./my_nodejs xxx.js
	@echo

stats:
	@wc $(OBJS_JS) tomuss_python*.js

clean:
	@echo "$@"
	@-rm tomuss_python_regtest.js xxx*

fullclean:clean
	@echo "$@"
	@-rm tomuss_python.js

xxx_tomuss.js:Makefile $(JS)
	@echo 'window = { "location":""} ; ' >$@
	@echo 'navigator = { } ; ' >>$@
	@echo 'var today = "20140101" ;' >>$@
	@cat $(JS) >>$@

difference.js:difference.py xxx_tomuss.js Makefile
	@./python_to_js "regtest.py difference.py" difference.js
	@cat xxx_tomuss.js difference.js >xxx.js
	@./my_nodejs xxx.js
	@echo

used_filters:
	find ../DB/Y[!0]* -name '*.py' -print0 | \
	xargs -0 grep -e 'filter' -e 'cell_writable' | \
	sed -e "s/.*['"\""],['"\""]//" -e "s/..$$//" | \
	awk '{T[$$0]++;} END { for(i in T) print T[i], i ; }' | \
	sort -n

# Only for personnal testing

test:
	./python_to_js " preamble_js.py filter.py test.py" xxx.js
	@echo 'window = { "location":""} ; navigator = { } ;' >xxx2.js
	@cat xxx.js >>xxx2.js
	./my_nodejs xxx2.js

