EGG_NAME=clictagger
SHELL=/bin/bash -o pipefail

all: compile test lint

bin/pip:
	python3 -m venv .

lib/.requirements: requirements.txt setup.py bin/pip
	# Install requirements
	./bin/pip install -r requirements.txt
	touch lib/.requirements

compile: lib/.requirements

test: compile
	./bin/pytest $(EGG_NAME) tests

lint: lib/.requirements
	./bin/black $(EGG_NAME)/ tests/

coverage: compile
	./bin/coverage run ./bin/py.test $(EGG_NAME)/ tests/
	./bin/coverage html
	mkdir -p ../client/www/coverage
	ln -frs htmlcov ../client/www/coverage/server
	echo Visit http://$(WWW_SERVER_NAME)/coverage/server/index.html

.PHONY: compile test lint coverage
