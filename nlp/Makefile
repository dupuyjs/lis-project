SHELL=/bin/bash

clean:
	@rm -Rf build/
	@rm -Rf dist/
	@rm -Rf __pycache__/
	@rm -Rf tests/__pycache__/
	@rm -Rf src/datashop/__pycache__/
	@rm -Rf src/__pycache__/
	@rm -Rf src/aad.egg-info

run-local:
	@PYTHONPATH=./src uvicorn main:app --reload --host localhost --port 9000

install-deps:
	pip install -r requirements.txt
