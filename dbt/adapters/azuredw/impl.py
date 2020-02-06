from dbt.adapters.sql import SQLAdapter
from dbt.adapters.azuredw import AzureDWConnectionManager


class AzureDWAdapter(SQLAdapter):
    ConnectionManager = AzureDWConnectionManager

    @classmethod
    def date_function(cls):
        return 'get_date()'

    @classmethod
    def convert_text_type(cls, agate_table, col_idx):
        return 'varchar(8000)'
