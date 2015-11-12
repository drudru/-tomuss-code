# To debug JS :
#    node debug xxx.js
# And 'c' to continue

all:regtest_python tomuss_python.js regtest_js stats

OBJS = filter.py average.py maximum.py nmbr.py cow.py diff_date.py weighted_percent.py product.py places.py
OBJS_JS = preamble.py preamble_js.py $(OBJS)
OBJS_PYTHON = preamble.py preamble_python.py $(OBJS)
REGTEST = regtest.py *_regtest.py
JS=../FILES/lib.js ../FILES/utilities.js ../COLUMN_TYPES/text.js deprecated.js

LOCAL=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then ls ../LOCAL/LOCAL_PYTHON_JS/*.py | grep -v regtest ; fi)
LOCAL_REGTEST=$(shell if [ -d ../LOCAL/LOCAL_PYTHON_JS ] ; then echo ../LOCAL/LOCAL_PYTHON_JS/*_regtest.py ; fi)

translator:
	@echo "Cloning translator repository, checkout a working version"
	if [ ! -d RapydScript ] ; \
	then \
        git clone git://github.com/atsepkov/RapydScript.git ; \
	cd RapydScript ; \
	git checkout e2c8b247a5b1a1024a8e7adae188b7bb78a77ede ; \
	fi

tomuss_python.py:$(OBJS_PYTHON) $(LOCAL) Makefile
	@cat $(OBJS_PYTHON) $(LOCAL) >$@

tomuss_python.js:$(OBJS_JS) $(LOCAL) Makefile
	@./python_to_js "$(OBJS_JS) $(LOCAL)" $@

tomuss_python_regtest.js:$(OBJS_JS) $(REGTEST) $(LOCAL) $(LOCAL_REGTEST) Makefile
	@./python_to_js "$(OBJS_JS) $(LOCAL) $(REGTEST) $(LOCAL_REGTEST)" $@

regtest: translator regtest_python regtest_js

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
	./python_to_js test.py xxx.js
	./my_nodejs xxx.js

