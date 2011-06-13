CFLAGS = -O3

# Launch the regression tests once.
tests:check
	@echo "Use 'forever' goal to run tests without stopping"
	@./test.py

# Launch the regression tests until an error is detected
forever:check
	@echo 'Display status on test termination'
	@echo 'Tests logs are in "xxx.forever" file.'
	@echo 'Results of the last test are in /tmp/XXX/xxx.html'
	@echo 'Results of the current test are in /tmp/XXX/xxx.html.new'
	@echo 'The bad snapshots (and image diffs) are in /tmp/XXX/'
	@echo "Start test : $$(date)"
	@I=1 ; \
        while ./test.py 2>&1 ; \
            do echo "= $$I tests done $$(date)" ; \
            I=$$(expr $$I + 1) ; \
        done | tee xxx.forever | grep --line-buffered -e '^= '
	@echo "ERROR: regression tests failed"

dumper:dumper.c
	$(CC) $(CFLAGS) dumper.c $$(pkg-config --libs x11) -o $@

clean:
	rm *~ *.pyc Trash/*

EXECUTABLE = which >/dev/null

check:dumper
	@$(EXECUTABLE) fvwm
	@$(EXECUTABLE) cnee || $(EXECUTABLE) xnee
	@$(EXECUTABLE) Xnest || $(EXECUTABLE) Xvfb
	@$(EXECUTABLE) epiphany || echo "'epiphany' browser is missing"
	@$(EXECUTABLE) chromium-browser || echo "'chromium' browser is missing"
	@$(EXECUTABLE) opera || echo "'opera' browser is missing"
	@$(EXECUTABLE) firefox || echo "'firefox' browser is missing"

