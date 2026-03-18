.PHONY: check install dev test stop gateway

check:
	@echo "Checking prerequisites..."
	@python3 --version
	@uv --version

install:
	cd backend && make install

dev:
	cd backend && make dev

test:
	cd backend && make test

gateway:
	cd backend && make gateway

stop:
	@echo "Stopping services..."
