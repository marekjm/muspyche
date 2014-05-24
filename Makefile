PYTHON_VERSION=3.4
PYTHON_SITEPKGS_LOCAL=~/.local/lib/python${PYTHON_VERSION}/site-packages
BINDIR=~/.local/bin

.PHONY: tests tests-specs tests-contextstack

clean:
	@rm -rv muspyche/__pycache__/


install: install-bin


install-lib:
	@cp -Rv ./muspyche ${PYTHON_SITEPKGS_LOCAL}


install-bin-only:
	@cp -v ./muspyche/cli.py ${BINDIR}/muspyche
	chmod 755 ${BINDIR}/muspyche


install-bin: install-lib install-bin-only


tests:
	python3 tests/contextstack.py
	./run_atoms_tests.sh
	python3 tests/specs.py


tests-specs:
	python3 tests/specs.py --failfast


tests-contextstack:
	python3 tests/contextstack.py --failfast --verbose
