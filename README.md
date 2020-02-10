# dbt-azuresa

dbt-azuresa is a custom adapter for [dbt](https://github.com/fishtown-analytics/dbt) that adds support for Azure SQL Data Warehouse.. pyodbc is used as the connection driver as that is what is [suggested by Microsoft](https://docs.microsoft.com/en-us/sql/connect/python/python-driver-for-sql-server). The adapter supports both windows auth, and specified user accounts.

dbt-azuresa is currently in a beta release.

## Connecting to Azure SQL Data Warehouse

## building your `profiles.yml`

Use the profiles.yml file included as a guide, updating with your creds. You can find all the creds you need under _Home > dbname (account/dbname) - Connection strings_ in Azure, along with the username and password for authentication.

## Getting Started

1. Run this to keep your profiles.yml from tracking:

```git
git update-index --skip-worktree profiles.yml
```

2. Update profiles.yml with your actual Azure Data Warehouse creds.

3. Build the docker image. From the repo root:

```docker
docker build . -t dbt-azure-dw
```

4. Run a bash shell in the container:

```docker
docker run -v $(PWD):/dbt_development/plugins -it dbt-azure-dw /bin/bash
```

you can then jump into `jaffle_shop (mssql)` and work on making it run against your ADW!  

### Sample profiles.yml

```yaml

default:
  target: dev
  outputs:
    dev:
      type: azuredw
      driver: 'ODBC Driver 17 for SQL Server'
      host: account.database.windows.net
      database: dbt_test
      schema: foo
      username: dbt_user
      password: super_secret_dbt_password
      authentication: ActiveDirectoryPassword
```

## Known Issues

- At this time dbt-azuredw supports only `table`, `view` and `incremental` materializations (no `ephemeral`)
- Only top-level (model) CTEs are supported, ie CTEs in macros are not supported (this is a sqlserver thing)

## Jaffle Shop

Fishtown Analytic's [jaffle shop](https://github.com/fishtown-analytics/jaffle_shop) package is currently unsupported by this adapter. At the time of this writing, jaffle shop uses the `using()` join, and `group by [ordinal]` notation which is not supported in T-SQL. An alternative version has been forked by the author of dbt-mssql [here](https://github.com/jacobm001/jaffle_shop_mssql).
