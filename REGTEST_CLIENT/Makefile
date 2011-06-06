# Launch the regression tests once.
tests:
	@which fvwm
	@which cnee || which xnee
	@which Xvfb || which Xnest
	@echo "Use 'forever' goal to run tests until an error"
	@./test.py

# Launch the regression tests until an error is detected
forever:
	@echo 'Display status after test end'
	@echo 'Tests logs are in "xxx" file.'
	@echo "Start test : $$(date)"
	@I=1 ; \
        while ./test.py 2>&1 ; \
            do echo "$$I tests done $$(date)" ; \
            I=$$(expr $$I + 1) ; \
        done | tee xxx | grep --line-buffered -e 'Start testing' \
                                              -e 'The log file' 
	@echo "ERROR: regression tests failed"

clean:
	rm *~ *.pyc Trash/*
