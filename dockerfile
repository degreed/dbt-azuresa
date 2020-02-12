FROM python:3.7-slim-stretch

# Install general dependencies
RUN apt-get update && \
    apt-get install && \
    apt-transport-https \
    ca-certificates \
    curl \
    g++ \
    gcc \
    git \
    gnupg2 \
    libssl1.1 \
    unixodbc-dev \
    vim -y

# Install Sql Server driver dependencies
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install msodbcsql17=17.3.1.1-1 -y 
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

# Set up the directories
RUN mkdir ~/.dbt
RUN mkdir /dbt_development
RUN mkdir /dbt_development/plugins
COPY . /dbt_development/plugins/dbt-azuredw
RUN cp ./plugins/dbt-azuredw/profiles.yml ~/.dbt/profiles.yml

# Set up testing dependencies
RUN git clone https://github.com/fishtown-analytics/dbt-integration-tests.git

WORKDIR /dbt_development
