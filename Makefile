
start:translations
	SCRIPTS/crontab_run.py
stop stopsuivi stoptomuss restartsuivi:
	SCRIPTS/crontab_run.py $@

install:clean
	SCRIPTS/install
check:
	SCRIPTS/mirror_check

recompute_the_ue_list:
	# Recompute the UE list. Take into account students in TT
	./tomuss.py recompute_the_ue_list

clean:
	@echo 'CLEAN'
	@-find . \( -name '*~' \
                 -o -name '*.pyc' \
                 -o -name '*.bak' \
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
	etags $$(git ls-files -- '*.js' '*.py')

regtest:clean translations
	cd REGTEST_SERVER ; ./tests.py 2>/dev/null

regtest1:clean translations
	cd REGTEST_SERVER ; ./tests.py 1 2>/dev/null

V := $(shell python -c 'import tomuss_init ; from . import configuration;print configuration.version' 2>/dev/null)

release:translations
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
	@[ -x LOCAL/release ] && LOCAL/release

tar:
	@echo "Start cleanup"
	@$(MAKE) clean changelog
	@echo "Start copy"
	@rm -rf /tmp/TOMUSS-$(V)
	@mkdir /tmp/TOMUSS-$(V)
	@cp -a $$(pwd)/?* /tmp/TOMUSS-$(V)
	@echo "Remove what is not in GIT"
	@git ls-files -o --directory | (cd /tmp/TOMUSS-$(V) && xargs rm -r || true)
	@echo "Rename LOCAL.template to LOCAL"
	@mv /tmp/TOMUSS-$(V)/LOCAL.template /tmp/TOMUSS-$(V)/LOCAL
	@cd /tmp ; \
	tar -cvf - TOMUSS-$(V) \
	    | bzip2 -9 >~/public_html/TOMUSS/TOMUSS-$(V).tar.bz2 ;
	@echo "Start tempory files cleanup"
	@rm -rf /tmp/TOMUSS-$(V)
	@rm -f ~/public_html/TOMUSS/tomuss.tar.bz2
	@echo "Create link to last version"
	@ln -s TOMUSS-$(V).tar.bz2 ~/public_html/TOMUSS/tomuss.tar.bz2
	@ls -ls ~/public_html/TOMUSS/TOMUSS-$(V).tar.bz2
	@ls -ls ~/public_html/TOMUSS/tomuss.tar.bz2

changelog:
	@-if [ $$(which git) != '' ] ; \
	then \
	echo "Create changelog" ; \
	SCRIPTS/changelog >DOCUMENTATION/changelog ; \
	fi

translations:
	@for I in TRANSLATIONS/*/LC_MESSAGES \
                  LOCAL/LOCAL_TRANSLATIONS/*/LC_MESSAGES ; \
         do if [ -d "$$I" ] ; \
                 then \
                 echo $$I ; \
                 (cd $$I ; \
                  $(MAKE) --no-print-directory -f $$(echo $$I | sed -r 's/[^\/]+/../g')/Makefile tomuss.mo) ; \
                if [ $$? != 0 ] ; then exit 1 ; fi ; \
           fi ; \
         done
	SCRIPTS/create_backgrounds.py

%.mo:%.po
	msgfmt $*.po -o $*.mo

full-tar:
	@$(MAKE) clean 2>/dev/null >&2
	@tar -cf - \
		--exclude 'Trash' \
		--exclude 'LOGS' \
		--exclude 'DBregtest' \
		--exclude 'BACKUP_DBregtest' \
		--exclude '.git' \
		 .

untar:
	cd /tmp && bzcat ~/public_html/TOMUSS/TOMUSS-$(V).tar.bz2 | tar -xf -

tar-check:untar
	cd /tmp/TOMUSS-$(V) && $(MAKE) regtest1

push:
	git push ; git push --tags ; git fetch
	cd LOCAL ; git push ; git push --tags ; git fetch

untag:
	git tag -d $(V)
	cd LOCAL ; git tag -d $(V)

S=count() { git ls-files | grep -E "$$1" | xargs cat | wc -l ; echo '(' ; git ls-files | grep -E "$$1" | wc -l; echo 'files)';} ; search() { A=$$(count "$$1") ; cd LOCAL ; B=$$(count "$$1") ; echo $$A '   LOCAL:' $$B; } ; search

stat:
	@echo "Copyright and comment lines are counted"
	@echo "JavaScript lines : $$($(S) '\.js$$')"
	@echo "Python     lines : $$($(S) '\.py$$')"
	@echo "HTML       lines : $$($(S) '\.html$$')"
	@echo "CSS        lines : $$($(S) '\.css$$')"
	@echo "SVG        lines : $$($(S) '\.svg$$')"
	@echo "PO         lines : $$($(S) '\.po$$')"
	@echo "PO               : $$(grep -c msgid TRANSLATIONS/fr/LC_MESSAGES/tomuss.po) messages"
	@echo "Images           : " "$$(git ls-files | grep -E '\.(png|jpg|gif)$$' | wc -l)"


version:
	@echo $(V)

