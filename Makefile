update:
	git fetch upstream
	git checkout master
	git merge upstream/master

run:
	. venv/bin/activate;	python run.py

devel:
	. venv/bin/activate; PROVISION=force python run.py
