APP_BIN := .venv/bin/purplebot-discord
PIP_BIN := .venv/bin/pip


.PHONY:	run build check clean
.DEFAULT: run

run: ${APP_BIN}
	${APP_BIN} test -v 2

$(PIP_BIN):
	python3 -m venv .venv

${APP_BIN}: $(PIP_BIN)
	${PIP_BIN} install -e .

clean:
	rm -rf .venv dist
