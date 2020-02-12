docker-build:
	@echo "Building the container..."
	@docker build . -t dbt-azuresa:testing

dbt-shell: docker-build
	@echo "Spinning up a shell..."
	@docker run -it dbt-azuresa:testing /bin/bash