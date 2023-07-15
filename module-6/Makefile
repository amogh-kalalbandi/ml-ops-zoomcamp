 quality_checks:
	black .
	pylint --recursive=y .

tests: quality_checks
	pytest tests/

integration_test: tests
	bash run.sh

build: integration_test
	echo run
