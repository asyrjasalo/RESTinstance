SHELL := /bin/bash

# get OS X to have `pip install --user` target in $PATH
PATH := ${HOME}/.local/bin:${PATH}

# virtualenvs(' paths) handled by make rules
VENV_DEV_PATH := .venv/dev
VENV_RELEASE_PATH := .venv/release

# evaluate lazily: package name when installing from PyPIs
PACKAGE_NAME = RESTinstance
MODULE_NAME = REST

# evaluate lazily: check version before building and after installation
VERSION_TO_BUILD = python setup.py --version
VERSION_INSTALLED = python -c "import ${MODULE_NAME}; print(${MODULE_NAME}.__version__)"


.DEFAULT_GOAL := all_dev

.PHONY: all_dev
all_dev: test install atest ## (DEFAULT / make): test, install, atest

.PHONY: all_github
all_github: black test build install atest ## All branches/PRs: black, test, build, install, atest

.PHONY: all_prepypi
all_prepypi: build publish_pre install_pre atest ## Prerelease to TestPyPI: build, publish_pre, install_pre, atest

.PHONE: all_pypi
all_pypi: build publish_prod install_prod atest ## Final release to PyPI: build, publish_prod, install_prod, atest

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+[0-9]*:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: _venv_dev
_venv_dev:
	pipx --version >/dev/null || pip install --user pipx
	test -d "${VENV_DEV_PATH}" || pipx run virtualenv "${VENV_DEV_PATH}"
	. "${VENV_DEV_PATH}/bin/activate" && \
	pip install --quiet -r requirements-dev.txt

.PHONY: _venv_release
_venv_release:
	pipx --version >/dev/null || pip install --user pipx
	pipx run virtualenv --clear "${VENV_RELEASE_PATH}"
	. "${VENV_RELEASE_PATH}/bin/activate" && \
	pip install --upgrade pip setuptools wheel

.PHONY: pur
pur: _venv_dev ## Update requirements-dev's deps that have versions defined
	pipx run pur -r requirements-dev.txt --no-recursive

.PHONY: black
black: _venv_dev ## Reformat ("blacken") all Python source code in-place
	pipx run black .

.PHONY: flake8
flake8: _venv_dev ## Run flake8 for detecting flaws via static code analysis
	pipx run flake8

.PHONY: prospector
prospector: _venv_dev ## Runs static analysis using dodgy, mypy, pyroma and vulture
	. "${VENV_DEV_PATH}/bin/activate" && \
	prospector --tool dodgy --tool mypy --tool pyroma --tool vulture src

.PHONY: testenv
testenv: testenv_rm ## Start new testenv in docker if available, otherwise local
	docker -v >/dev/null && \
	(docker run -d --name "${PACKAGE_NAME}_mountebank" -ti -p 2525:2525 -p 8273:8273 -v $(CURDIR)/testapi:/testapi:ro andyrbell/mountebank mb --allowInjection --configfile /testapi/apis.ejs) || \
	(nohup npx mountebank --localOnly  --allowInjection --configfile testapi/apis.ejs > results/testenv_npx_mountebank.log &)

.PHONY: testenv_rm
testenv_rm: ## Stop and remove the running docker testenv if any
	docker -v >/dev/null && docker rm --force "${PACKAGE_NAME}_mountebank" || true

.PHONY: docs
docs: ## Regenerate (library) documentation in this source tree
	. "${VENV_DEV_PATH}/bin/activate" && \
	python -m robot.libdoc ${MODULE_NAME} docs/index.html

.PHONY: atest
atest: testenv ## Run Robot atests for the currently installed package
	python -m robot.run --outputdir results --xunit xunit.xml atest

.PHONY: test
test: _venv_dev ## Run unit tests, upgrades .venv/dev with requirements(-dev)
	. "${VENV_DEV_PATH}/bin/activate" && pytest

.PHONY: retest
retest: ## Run only failed unit tests if any, otherwise all
	. "${VENV_DEV_PATH}/bin/activate" && \
	pytest --last-failed --last-failed-no-failures all

.PHONY: build
build: _venv_release ## Build source and wheel dists, recreates .venv/release
	. "${VENV_RELEASE_PATH}/bin/activate" && pip install .
	#####################################
	### Version check before building ###
	. "${VENV_RELEASE_PATH}/bin/activate" && ${VERSION_TO_BUILD} && \
	python setup.py clean --all bdist_wheel sdist

.PHONY: install
install: ## (Re)install package as --editable from this source tree
	pip install --no-cache-dir --editable .
	######################################
	### Version check after installing ###
	${VERSION_INSTALLED}

.PHONY: install_pre
install_pre: uninstall ## (Re)install the latest test.pypi.org (pre-)release
	pip install --no-cache-dir --pre \
		--index-url https://test.pypi.org/simple/ \
		--extra-index-url https://pypi.org/simple ${PACKAGE_NAME}

.PHONY: install_prod
install_prod: ## Install/upgrade to the latest final release in PyPI
	pip install --no-cache-dir --upgrade ${PACKAGE_NAME}

.PHONY: uninstall
uninstall: ## Uninstall the Python package, regardless of its origin
	pip uninstall --yes ${PACKAGE_NAME} || true

.PHONY: publish_pre
publish_pre: ## Publish dists to test.pypi.org - for pre, e.g. aX, bX, rcX
	pipx run twine check dist/* && \
	pipx run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: publish_prod
publish_prod: ## Publish dists to live PyPI - for final only, e.g. 1.0.1
	pipx run twine check dist/* && pipx run twine upload dist/*

.PHONY: clean
clean: uninstall ## Pip uninstall, rm .venv/s, build, dist, eggs, .caches
	rm -rf dist build */*.egg-info */__pycache__ */**/__pycache__
	rm -rf .pytest_cache .mypy_cache
	rm -rf pip-wheel-metadata
	rm -rf "${VENV_DEV_PATH}" "${VENV_RELEASE_PATH}"
	rm -rf results
	rm -f log.html output.xml report.html *.demo.json
	rm -f mb.log mb1.log mb.pid
