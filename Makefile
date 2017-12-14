update:
	git fetch upstream
	git checkout master
	git merge upstream/master

requirements: requirements.txt
	. venv/bin/activate; pip install -r $< > /dev/null

run: requirements
	. venv/bin/activate; python run.py

devel: requirements
	. venv/bin/activate; PROVISION=force python run.py

console: requirements
	. venv/bin/activate; python console.py
