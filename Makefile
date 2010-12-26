
start:
	SCRIPTS/crontab_run.py
stop stopsuivi stoptomuss:
	SCRIPTS/crontab_run.py $@

install:clean
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
	@rm -rf DBregtest BACKUP_DBregtest
	@for I in */. ;\
          do [ -f $$I/Makefile ] && ( cd $$I ; \
                                      echo "CLEAN $$I" ; \
                                      $(MAKE) -s clean ) ; \
         done || true

tags:
	etags *.py */*.py */*.js

regtest:
	cd REGTEST_SERVER ; ./tests.py

tar:
	V=$$(python -c 'import configuration;print configuration.version') ; \
	$(MAKE) clean ; rm -rf /tmp/TOMUSS-$$V ; \
	cp -a $$(pwd) /tmp/TOMUSS-$$V ; \
	rm -rf /tmp/TOMUSS-$$V/LOCAL ; \
	rm -rf /tmp/TOMUSS-$$V/BACKUP_DBtest ; \
	rm -rf /tmp/TOMUSS-$$V/DBtest ; \
	rm -rf /tmp/TOMUSS-$$V/BACKUP_DB ; \
	rm -rf /tmp/TOMUSS-$$V/DB ; \
	mv /tmp/TOMUSS-$$V/LOCAL.template /tmp/TOMUSS-$$V/LOCAL ; \
	cd /tmp ; \
	tar -cvf - \
		--exclude 'Trash' \
		--exclude 'LOGS' \
		--exclude 'TMP' \
		--exclude '.git' \
		--exclude 'services-ucbl.html' \
		--exclude 'xxx*' \
		TOMUSS-$$V \
	    | bzip2 -9 >~/public_html/TOMUSS/TOMUSS-$$V.tar.bz2 ; \
	rm -rf TOMUSS-$$V ; \
	rm -f ~/public_html/TOMUSS/tomuss.tar.bz2 ; \
	ln -s TOMUSS-$$V.tar.bz2 ~/public_html/TOMUSS/tomuss.tar.bz2

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

tar-check:
	V=$$(python -c 'import configuration;print configuration.version') ; \
	cd /tmp ; \
	bzcat ~/public_html/TOMUSS/TOMUSS-$$V.tar.bz2 | \
	tar -xf - ; \
	cd TOMUSS-$$V ; \
	make regtest

