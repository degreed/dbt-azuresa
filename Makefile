docker-build:
	@echo "Building the container..."
	@docker build . -t dbt-azuresa:testing

dbt-shell: docker-build
	@echo "Spinning up a shell..."
	@docker run -it dbt-azuresa:testing /bin/bash

run-tests: docker-build
	@echo "Running the suite of dbt adapter tests..."
	@docker run dbt-azuresa:testing /dbt_development/dbt-integration-tests/bin/run-with-profile test