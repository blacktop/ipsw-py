.PHONY: all
all: docs

.PHONY: clean
clean:
	find -name "__pycache__" | xargs rm -rf

.PHONY: build-docs
build-docs:
	docker build -t docker-sdk-python-docs -f Dockerfile-docs $(uid_args) .

.PHONY: docs
docs: build-docs
	docker run --rm -t -v `pwd`:/src docker-sdk-python-docs sphinx-build docs docs/_build
