FROM python:3.7-slim-stretch

# Install general dependencies
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    g++ \
    gcc \
    git \
    gnupg2 \
    libssl1.1 \
    unixodbc-dev \
    vim
RUN pip install -U pip

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
WORKDIR /dbt_development
RUN cp ./plugins/dbt-azuredw/profiles.yml ~/.dbt/profiles.yml

# Install the adapter
RUN python ./plugins/dbt-azuredw/setup.py install

# Set up testing dependencies
RUN git clone https://github.com/fishtown-analytics/dbt-integration-tests.git
RUN pip install -r dbt-integration-tests/requirements.txt
