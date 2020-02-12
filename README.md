# dbt-azuresa

dbt-azuresa is a custom adapter for [dbt](https://github.com/fishtown-analytics/dbt) that adds support for Azure Synapse Analytics data warehouse. `pyodbc` is used as the connection driver as that is what is [suggested by Microsoft](https://docs.microsoft.com/en-us/sql/connect/python/python-driver-for-sql-server). The adapter supports both windows auth, and specified user accounts. The page for creating a custom dbt adapter can be found [here](https://docs.getdbt.com/docs/building-a-new-adapter).

dbt-azuresa is currently in a beta release.

The official `dbt` adapter test suite is used here for testing. The GitHub repo for these integration tests can be found [here](https://github.com/fishtown-analytics/dbt-integration-tests).

## Connecting to Azure Synapse Analytics data warehouse

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

- At this time dbt-azuresa supports only `table`, `view` and `incremental` materializations (no `ephemeral`)
- Only top-level (model) CTEs are supported, ie CTEs in macros are not supported (this is a sqlserver thing)
