# Launch the regression tests once.
tests:check
	@echo "Use 'forever' goal to run tests until an error"
	@./test.py

# Launch the regression tests until an error is detected
forever:check
	@echo 'Display status on test termination'
	@echo 'Tests logs are in "xxx.forever" file.'
	@echo 'Results of the last test are in /tmp/XXX/xxx.html'
	@echo 'Results of the current test are in /tmp/XXX/xxx.html.new'
	@echo 'The bad snapshots are in /tmp/XXX/999.png'
	@echo "Start test : $$(date)"
	@I=1 ; \
        while ./test.py 2>&1 ; \
            do echo "$$I tests done $$(date)" ; \
            I=$$(expr $$I + 1) ; \
        done | tee xxx.forever | grep --line-buffered -e '^= '
	@echo "ERROR: regression tests failed"

clean:
	rm *~ *.pyc Trash/*

EXECUTABLE = which >/dev/null

check:
	@$(EXECUTABLE) fvwm
	@$(EXECUTABLE) cnee || $(EXECUTABLE) xnee
	@$(EXECUTABLE) Xvfb || $(EXECUTABLE) Xnest
