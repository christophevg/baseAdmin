tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

venv:
	virtualenv $@

requirements: venv requirements.txt
	. venv/bin/activate; pip install --upgrade -r requirements.txt > /dev/null

dist: requirements
	. venv/bin/activate; python setup.py sdist bdist_wheel

dist-test: dist
	rm -rf $@
	mkdir $@
	cd $@; cp -r ../demo .; virtualenv venv;	. venv/bin/activate; pip install ../dist/baseadmin-1.0.0.tar.gz gunicorn; gunicorn demo.backend:server

publish-test: dist
	. venv/bin/activate; twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish: dist
	. venv/bin/activate; twine upload dist/*

test:
	tox

coverage: test requirements
	. venv/bin/activate; coverage report

docs: requirements
	. venv/bin/activate; cd docs; make html
	open docs/_build/html/index.html

backend: requirements
	. venv/bin/activate; gunicorn demo.backend:server

client: requirements
	. venv/bin/activate; PYTHON_PATH=. python -m demo.client

clean:
	@rm -rf dist dist-test *.egg-info build docs/_build .coverage .tox *.pkl

.PHONY: dist docs backend client dist-test
