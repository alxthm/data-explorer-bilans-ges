.PHONY: clean data lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROFILE = default
PROJECT_NAME = benchmark-footprints
PYTHON_INTERPRETER = python3

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
# For now:
# * requirements.txt is used as the base source of requirements (could be moved to a pyproject.toml...)
# * requirements.lock.txt is generated from it (we could use pip-tools for this...),
#   and used for both local venv and remote docker image

freeze_requirements:
	$(PYTHON_INTERPRETER) -m venv .venv_for_lock
	. .venv_for_lock/bin/activate && \
		$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel && \
		$(PYTHON_INTERPRETER) -m pip install -r requirements.txt && \
		$(PYTHON_INTERPRETER) -m pip freeze > requirements.lock.txt && \
	rm -rf .venv_for_lock

install_requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.lock.txt
	$(PYTHON_INTERPRETER) -m pip install -e .

## Make Dataset
# For now:
# * non-heavy data is simply checked out to git (in the data/raw/light/ folder)
# * heavier data (>10Mb) should be put inside the data/raw/heavy folder (not checked out to git)
#   and compressed into individual .gz files (checked out to git for now since it's still small)
# * processed data is not checked out to git
compress_data:
	gzip -k -r data/raw/heavy/

data/raw/heavy/data_uncompressed:
	gzip -k -r -d data/raw/heavy/
	touch data/raw/heavy/data_uncompressed

data: data/raw/heavy/data_uncompressed
	$(PYTHON_INTERPRETER) src/data/make_dataset.py

## Delete all compiled Python files
clean-python:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Delete untracked data files (uncompressed data, processed data, ...)
clean-data:
	git clean -xdf data/

## Lint using ruff
lint:
	ruff format

serve:
	panel serve \
		--address "0.0.0.0" --port 7860 \
		--allow-websocket-origin "*" \
		--global-loading-spinner \
		--reuse-sessions \
		--num-procs 2 \
		./src/pages/benchmark.py ./src/pages/profiles.py ./src/pages/about.py \
		--index ./src/pages/benchmark.py

# ## Set up python interpreter environment
# create_environment:
# ifeq (True,$(HAS_CONDA))
# 		@echo ">>> Detected conda, creating conda environment."
# ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
# 	conda create --name $(PROJECT_NAME) python=3
# else
# 	conda create --name $(PROJECT_NAME) python=2.7
# endif
# 		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
# else
# 	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
# 	@echo ">>> Installing virtualenvwrapper if not already installed.\nMake sure the following lines are in shell startup file\n\
# 	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
# 	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
# 	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
# endif

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
