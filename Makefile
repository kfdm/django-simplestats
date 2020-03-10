APP_BIN := .venv/bin/quickstats
PIP_BIN := .venv/bin/pip

.PHONY:	test build migrate run shell clean
.DEFAULT: test

test: ${APP_BIN}
	${APP_BIN} test -v 2

$(PIP_BIN):
	python3 -m venv .venv

${APP_BIN}: $(PIP_BIN)
	${PIP_BIN} install -r docker/requirements.txt
	${PIP_BIN} install -e .[dev,standalone]

build:
	docker-compose build
migrate: ${APP_BIN}
	${APP_BIN} migrate
run: migrate
	${APP_BIN} runserver
shell: migrate
	${APP_BIN} shell
clean:
	rm -rf .venv
