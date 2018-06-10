update:
	git fetch upstream
	git checkout master
	git merge upstream/master

requirements: requirements.txt
	. venv/bin/activate; pip install -r $< > /dev/null

console: requirements
	. venv/bin/activate; python console.py ${ARGS}
