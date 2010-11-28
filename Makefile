
start:
	SCRIPTS/crontab_run.py
stop:
	SCRIPTS/crontab_run.py stop

install:clean diff
	SCRIPTS/install
check:
	SCRIPTS/mirror_check


stat:
	@echo "JavaScript lines : " "$$(cat FILES/*.js COLUMNS_TYPE/*.js | wc -l)"
	@echo "Python     lines : " "$$(cat [!x]*.py REGTEST*/*.py TEMPLATES/*.py PLUGINS/*.py COLUMN_TYPES/*.py LOCAL/[!x]*.py | wc -l)"
	@echo "HTML       lines : " "$$(cat FILES/*.html | wc -l)"
	@echo "CSS        lines : " "$$(cat FILES/*.css | wc -l)"
	@echo "Images           : " "$$(ls FILES/*.png FILES/*.gif FILES/*.ico | wc -l)"
	@echo "SVG              : " "$$(ls FILES/*.svg | wc -l)"

clean:
	@echo 'CLEAN'
	@-find . \( -name '*~' \
                 -o -name '*.pyc' \
                 -o -name 'xxx[!_]*' \) \
                 -exec rm {} \; 2>/dev/null
	@rm -rf DBregtest BACKUP_DBregtest || true
	@-for I in */. ;\
          do [ -f $$I/Makefile ] && ( cd $$I ; \
                                      echo "CLEAN $$I" ; \
                                      $(MAKE) -s clean ) ; \
         done

tags:
	etags *.py */*.py */*.js


# display difference between development sources and production sources.
diff:
	-@find . -type f \
	     ! \( -name '*.pyc' -o -name  '*~' -o -name 'xxx*' -o \
		-name 'all_ues.js' -o \
		-name 'sauvegarde' -o \
	        -path '*/LOGS/*' -o \
		-path '*/TICKETS/*' -o \
		-path '*/BACKUP_DB*/*' -o \
		-path '*/DB*/*' -o \
		-path '*/TMP/*' -o \
		-path '*/LOCAL/DATA/*' -o \
		-path '*/Trash/*' \) | while read I ; do \
	diff -u "/disc/saisienotes/SERVEUR_NOTES/$$I" "$$I" ; done
	@echo 'Tapez "return" pour continuer ou ^C pour arréter.'
	@read A


regtest:
	cd REGTEST_SERVER ; ./tests.py

tar:
	V=$$(python -c 'import configuration;print configuration.version') ; \
	$(MAKE) clean ; rm -rf /tmp/TOMUSS-$$V ; \
	cp -a $$(pwd) /tmp/TOMUSS-$$V ; \
	rm -r /tmp/TOMUSS-$$V/LOCAL ; \
	rm -r /tmp/TOMUSS-$$V/BACKUP_DBtest ; \
	rm -r /tmp/TOMUSS-$$V/DBtest ; \
	rm -r /tmp/TOMUSS-$$V/BACKUP_DB ; \
	rm -r /tmp/TOMUSS-$$V/DB ; \
	mv /tmp/TOMUSS-$$V/LOCAL.template /tmp/TOMUSS-$$V/LOCAL ; \
	cd /tmp ; \
	tar -cvf - \
		--exclude 'Trash' \
		--exclude 'LOGS/*' \
		--exclude 'LOGS/TICKETS/*' \
		--exclude 'TMP/*' \
		--exclude 'services-ucbl.html' \
		--exclude 'TEMPLATES/licence_dist.py' \
		--exclude 'TEMPLATES/master_sib.py' \
		--exclude 'TEMPLATES/m1.py' \
		--exclude 'TEMPLATES/rch.py' \
		--exclude 'TEMPLATES/cci.py' \
		--exclude 'TEMPLATES/pro.py' \
		--exclude 'FILES/premier_cours.py' \
		--exclude 'all_ues.js' \
		--exclude 'all_ues.js.gz' \
		--exclude 'xxx*' \
		TOMUSS-$$V \
	    | bzip2 -9 >~/public_html/TOMUSS/TOMUSS-$$V.tar.bz2 ; \
	rm -r TOMUSS-$$V ; \
	rm -f ~/public_html/TOMUSS/tomuss.tar.bz2 ; \
	ln -s TOMUSS-$$V.tar.bz2 ~/public_html/TOMUSS/tomuss.tar.bz2

full-tar:
	@$(MAKE) clean 2>/dev/null >&2
	@tar -cf - \
		--exclude 'Trash' \
		--exclude 'LOGS/*' \
		--exclude 'LOGS/TICKETS/*' \
		--exclude 'DBtest' \
		--exclude 'BACKUP_DBtest' \
		--exclude 'DBregtest' \
		--exclude 'BACKUP_DBregtest' \
		 .


tar-check:
	V=$$(python -c 'import configuration;print configuration.version') ; \
	cd /tmp ; \
	bzcat ~/public_html/TOMUSS/TOMUSS-$$V.tar.bz2 | \
	tar -xf - ; \
	cd TOMUSS-$$V ; \
	make regtest

