default: help

.PHONY: test
test:  ## Run full test suite ⏳
	tox

.PHONY: check
check:  ## Run static code checks over codebase
	pre-commit run --all

.PHONY: build
build:  ## Build distribution packages
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: build  ## Upload distribution packages to PyPI
	twine upload dist/*

.PHONY: help
help:  ## Display this help message
	@grep -E '^[a-zA-Z_%.-]+:.*?## .*$$' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36mmake %-10s\033[0m %s\n", $$1, $$2}'
