tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

venv:
	virtualenv $@

requirements: venv requirements.txt
	. venv/bin/activate; pip install --upgrade -r requirements.txt > /dev/null

upgrade: requirements
	. venv/bin/activate; pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

dist: requirements
	. venv/bin/activate; python setup.py sdist bdist_wheel

publish-test: dist
	. venv/bin/activate; twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish: dist
	. venv/bin/activate; twine upload dist/*

test: requirements
	. venv/bin/activate; tox

coverage: test
	. venv/bin/activate; coverage report; coverage html

docs: requirements
	. venv/bin/activate; cd docs; make html
	open docs/_build/html/index.html

demo-cloud:
	. venv/bin/activate; gunicorn demo.cloud.web:server

demo-master: demo/master/server.key demo/master/server.crt
	. venv/bin/activate; gunicorn --bind 127.0.0.1:8001 --certfile=demo/master/server.crt --keyfile=demo/master/server.key demo.master:server

demo/master/server.key:
	openssl genrsa -des3 -out $@ 1024
	cp $@ $@.org
	openssl rsa -in $@.org -out $@
	rm $@.org

demo/master/server.crt: demo/master/server.key
	openssl req -new -key $< -out server.csr
	openssl x509 -req -days 365 -in server.csr -signkey $< -out $@
	rm server.csr

demo-client:
	. venv/bin/activate; python -m demo.client

.PHONY: dist docs
