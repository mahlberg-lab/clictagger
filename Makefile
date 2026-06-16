EGG_NAME=clictagger
SHELL=/bin/bash -o pipefail

all: compile test lint

bin/pip:
	# 3.13+ adds "--without-scm-ignore-files", without which we blat .gitignore
	if python3 -m venv --help | grep -q -- "--without-scm-ignore-files"; then python3 -m venv --without-scm-ignore-files . ; else python3 -m venv .; fi

lib/.requirements: dev-requirements.txt setup.py bin/pip
	# Install requirements
	./bin/pip install -r dev-requirements.txt
	touch lib/.requirements

compile: lib/.requirements

test: compile
	./bin/pytest $(EGG_NAME) tests

lint: lib/.requirements
	./bin/python3 setup.py sdist
	./bin/twine check dist/*
	./bin/black --diff --check $(EGG_NAME)/ tests/ conftest.py

lint-apply: lib/.requirements
	./bin/black $(EGG_NAME)/ tests/ conftest.py

coverage: compile
	./bin/coverage run ./bin/py.test $(EGG_NAME)/ tests/
	./bin/coverage html
	mkdir -p ../client/www/coverage
	ln -frs htmlcov ../client/www/coverage/server
	echo Visit http://$(WWW_SERVER_NAME)/coverage/server/index.html

notebook: bin/pip
	./bin/pip install notebook ipywidgets
	./bin/jupyter nbextension enable --py widgetsnbextension --sys-prefix
	./bin/jupyter notebook --ip='0.0.0.0'

serve-docs: bin/pip
	 make -C docs clean dirhtml SPHINXBUILD=../bin/sphinx-build
	 ./bin/python3 -m http.server -d docs/_build/dirhtml

release: test lint
	./bin/fullrelease

clean:
	rm -rf -- bin include lib lib64 share pyvenv.cfg

.PHONY: compile test lint lint-apply coverage notebook release clean
