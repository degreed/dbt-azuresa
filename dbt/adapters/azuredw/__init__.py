from dbt.adapters.azuredw.connections import AzureDWConnectionManager
from dbt.adapters.azuredw.connections import AzureDWCredentials
from dbt.adapters.azuredw.impl import AzureDWAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import azuredw


Plugin = AdapterPlugin(
    adapter=AzureDWAdapter,
    credentials=AzureDWCredentials,
    include_path=azuredw.PACKAGE_PATH)
