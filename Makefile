# Colored text
RED = \033[0;31m
NC = \033[0m # No Color
GREEN = \033[0;32m

# Helper function to print section titles
define log_section
	@printf "\n${GREEN}--> $(1)${NC}\n\n"
endef

## Create Conda environment from a particular location in the repo
create_conda_env:
	$(call log_section, Creating Conda environment)
	conda env create -f $(PWD)/environment.yml