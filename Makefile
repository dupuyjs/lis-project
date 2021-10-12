SHELL=/bin/bash

MODULES = ./nlp


clean:
	@find . -name '__pycache__' -exec rm -fr {} +
	@find . -name '.pytest_cache' -exec rm -fr {} +
	@find . -name '.coverage' -exec rm -f {} +
	@find . -name 'coverage.xml' -exec rm -f {} +
	@find . -name 'pytest-results.xml' -exec rm -f {} +
	@find . -name 'build' ! -path '*/node_modules/*' -exec rm -fr {} +
	@find . -name 'dist' ! -path '*/node_modules/*' -exec rm -fr {} +
	@find . -name '*.egg-info' -exec rm -Rf {} +
	@find . -name 'tests-report.md' -exec rm -Rf {} +

	# Run all the python sub-projects
	@$(foreach c,$(MODULES), $(MAKE) -C $(c) $@ || exit ;)
	@rm -f tests-report.md

install-deps:
	@$(foreach c,$(MODULES), $(MAKE) -C $(c) $@ ;)