.PHONY: default isvirtualenv

default:
	clear
	@echo "Usage:"
	@echo ""
	@echo "    make devserver       Starts the development server."
	@echo "    make format          Formats source files."
	@echo ""
	@echo ""

isvirtualenv:
	@if [ -z "$(VIRTUAL_ENV)" ]; \
		then echo "ERROR: Not in a virtualenv." 1>&2; exit 1; fi

devserver: isvirtualenv
	poetry run uvicorn --reload  --log-level info leonify:application

format:
	poetry run isort .
	autoflake \
		--in-place \
		--recursive \
		--remove-all-unused-imports \
		--remove-unused-variables \
		.
	poetry run black .
