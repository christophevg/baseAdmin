update:
	git fetch upstream
	git checkout master
	git merge upstream/master

requirements: requirements.txt
	. venv/bin/activate; pip install -r $< > /dev/null

console: requirements
	. venv/bin/activate; python console.py ${ARGS}

client: requirements
	. venv/bin/activate; PYTHONPATH=. python -m client ${ARGS}

demo-service: requirements
	. venv/bin/activate; PYTHONPATH=. python client/services/demo.py ${ARGS}

system-service: requirements
	. venv/bin/activate; PYTHONPATH=. python client/services/system.py ${ARGS}
