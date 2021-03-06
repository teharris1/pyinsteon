all:

.PHONY:	dist update
dist:
	rm -f dist/*.whl dist/*.tar.gz
	python setup.py sdist

release:
	twine upload dist/*.tar.gz

test:
    twine upload --repository testpypi dist/*.tar.gz
