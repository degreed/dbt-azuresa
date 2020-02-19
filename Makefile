docker-build:
	@echo "Building the container..."
	@docker build . -t dbt-azuresa:testing

dbt-shell: docker-build
	@echo "Spinning up a shell..."
	@docker run --env-file ./env.list -it dbt-azuresa:testing /bin/bash

run-tests: docker-build
	@echo "Running the suite of dbt adapter tests..."
	@docker run --env-file ./env.list dbt-azuresa:testing /bin/bash -c "cd dbt-integration-tests/ && /bin/bash -eo pipefail bin/run-with-profile default"
