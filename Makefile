
start:
	SCRIPTS/crontab_run.py
stop stopsuivi stoptomuss:
	SCRIPTS/crontab_run.py $@

install:clean
	SCRIPTS/install
check:
	SCRIPTS/mirror_check

clean:
	@echo 'CLEAN'
	@-find . \( -name '*~' \
                 -o -name '*.pyc' \
                 -o -name '*.mo' \
		 -o -name '*flymake*' \
                 -o -name 'xxx[!_]*' \) \
                 -exec rm {} \; 2>/dev/null
	@rm -rf DBregtest BACKUP_DBregtest
	@for I in */. ;\
          do [ -f $$I/Makefile ] && ( cd $$I ; \
                                      echo "CLEAN $$I" ; \
                                      $(MAKE) -s clean ) ; \
         done || true

tags:
	etags $$(find . \( -name '*.js' -o -name '*.py' \) -print)

regtest:
	cd REGTEST_SERVER ; ./tests.py

regtest1:
	cd REGTEST_SERVER ; ./tests.py 1

V := $(shell python -c 'import configuration;print configuration.version' 2>/dev/null)

release:
	@echo "Check if we are in the 'stable' branch"
	@git branch | grep -F '* stable' >/dev/null
	@cd LOCAL ; git branch | grep -F '* stable' >/dev/null
	@echo "This release will be tagged $(V)"
	@echo "Running regression tests (about a minute)"
	@cd REGTEST_SERVER ; ./tests.py 1 >/dev/null 2>&1
	@echo "Regression tests are fine."
	@echo "Tagging GIT"
	@git tag $(V)
	@cd LOCAL ; git tag $(V)
	@echo "Documentation update"
	@cd DOCUMENTATION ; $(MAKE)
	@$(MAKE) -s tar

tar:
	$(MAKE) clean changelog
	rm -rf /tmp/TOMUSS-$(V)
	cp -a $$(pwd)/ /tmp/TOMUSS-$(V)
	rm -rf /tmp/TOMUSS-$(V)/LOCAL
	rm -rf /tmp/TOMUSS-$(V)/BACKUP_DBtest
	rm -rf /tmp/TOMUSS-$(V)/DBtest
	rm -rf /tmp/TOMUSS-$(V)/BACKUP_DB
	rm -rf /tmp/TOMUSS-$(V)/DB
	ls /tmp/TOMUSS-$(V)
	mv /tmp/TOMUSS-$(V)/LOCAL.template /tmp/TOMUSS-$(V)/LOCAL
	cd /tmp ; \
	tar -cvf - \
		--exclude 'Trash' \
		--exclude TOMUSS-$(V)/'LOGS' \
		--exclude TOMUSS-$(V)/'TMP' \
		--exclude '.git' \
		--exclude 'services-ucbl.html' \
		--exclude 'xxx*' \
		TOMUSS-$(V) \
	    | bzip2 -9 >~/public_html/TOMUSS/TOMUSS-$(V).tar.bz2 ; \
	rm -rf TOMUSS-$(V)
	rm -f ~/public_html/TOMUSS/tomuss.tar.bz2
	ln -s TOMUSS-$(V).tar.bz2 ~/public_html/TOMUSS/tomuss.tar.bz2

changelog:
	-if [ -x git ] ; then SCRIPTS/changelog >DOCUMENTATION/changelog ; fi

translations:
	@for I in TRANSLATIONS/*/LC_MESSAGES LOCAL/TRANSLATIONS/*/LC_MESSAGES ; do echo $$I ; (cd $$I ; $(MAKE) --no-print-directory -f $$(echo $$I | sed -r 's/[^\/]+/../g')/Makefile tomuss.mo) ; done

%.mo:%.po
	msgfmt $*.po -o $*.mo

full-tar:
	@$(MAKE) clean 2>/dev/null >&2
	@tar -cf - \
		--exclude 'Trash' \
		--exclude 'LOGS' \
		--exclude 'DBtest' \
		--exclude 'BACKUP_DBtest' \
		--exclude 'DBregtest' \
		--exclude 'BACKUP_DBregtest' \
		--exclude '.git' \
		 .

untar:
	cd /tmp ; bzcat ~/public_html/TOMUSS/TOMUSS-$(V).tar.bz2 | tar -xf -

tar-check:untar
	cd TOMUSS-$(V) ; $(MAKE) regtest1


S=count() { git ls-files | grep -E "$$1" | xargs cat | wc -l ; echo '(' ; git ls-files | grep -E "$$1" | wc -l; echo 'files)';} ; search() { A=$$(count "$$1") ; cd LOCAL ; B=$$(count "$$1") ; echo $$A '   LOCAL:' $$B; } ; search

stat:
	@echo "Copyright and comment lines are counted"
	@echo "JavaScript lines : " "$$($(S) '\.js$$')"
	@echo "Python     lines : " "$$($(S) '\.py$$')"
	@echo "HTML       lines : " "$$($(S) '\.html$$')"
	@echo "CSS        lines : " "$$($(S) '\.css$$')"
	@echo "SVG        lines : " "$$($(S) '\.svg$$')"
	@echo "Images           : " "$$(git ls-files | grep -E '\.(png|jpg|gif)$$' | wc -l)"
