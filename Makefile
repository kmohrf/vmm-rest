.PHONY: run
.ONESHELL:
run: .vmm
	export FLASK_DEBUG=1
	export PYTHONPATH="$$PYTHONPATH:.vmm:."
	python3 vmmrest/app.py || pipenv sync && pipenv run python vmmrest/app.py

.vmm:
	hg clone https://bitbucket.org/pvo/vmm -r v0.7.x .vmm
