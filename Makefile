env/done: env/bin/pip
	env/bin/pip install pytest -e .
	touch env/done

env/bin/pip:
	python -m venv --system-site-packages env

test: env/done
	env/bin/py.test -vv tests

.PHONY: test
