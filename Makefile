all: clean uninstall sdist install

clean:
	rm -r dist || true

sdist:
	python3 setup.py sdist

install:
	pipx install dist/spex*.tar.gz

uninstall:
	pipx uninstall spex || true
