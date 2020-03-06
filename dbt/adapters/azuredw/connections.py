from contextlib import contextmanager

import pyodbc
import time

import dbt.compat
import dbt.exceptions
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager

from dbt.logger import GLOBAL_LOGGER as logger

AZUREDW_CREDENTIALS_CONTRACT = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "driver": {"type": "string",},
        "host": {"type": "string",},
        "database": {"type": "string",},
        "schema": {"type": "string",},
        "UID": {"type": "string",},
        "PWD": {"type": "string",},
        "authentication": {
            "type": "string",
            "enum": [
                "ActiveDirectoryIntegrated",
                "ActiveDirectoryMSI",
                "ActiveDirectoryPassword",
                "SqlPassword",
                "TrustedConnection",
            ],
        },
    },
    "required": ["driver", "host", "database", "schema", "authentication"],
}


class AzureDWCredentials(Credentials):
    SCHEMA = AZUREDW_CREDENTIALS_CONTRACT
    ALIASES = {
        "user": "UID",
        "username": "UID",
        "pass": "PWD",
        "password": "PWD",
        "server": "host",
    }

    @property
    def type(self):
        return "azuredw"

    def _connection_keys(self):
        # return an iterator of keys to pretty-print in 'dbt debug'
        # raise NotImplementedError
        return (
            "server",
            "database",
            "schema",
            "UID",
            "authentication",
        )


class AzureDWConnectionManager(SQLConnectionManager):
    TYPE = "azuredw"

    @contextmanager
    def exception_handler(self, sql):
        try:
            yield

        except pyodbc.DatabaseError as e:
            logger.debug("Database error: {}".format(str(e)))

            try:
                # attempt to release the connection
                self.release()
            except pyodbc.Error:
                logger.debug("Failed to release connection!")
                pass

            raise dbt.exceptions.DatabaseException(dbt.compat.to_string(e).strip())

        except Exception as e:
            logger.debug("Error running SQL: %s", sql)
            logger.debug("Rolling back transaction.")
            self.release()
            if isinstance(e, dbt.exceptions.RuntimeException):
                # during a sql query, an internal to dbt exception was raised.
                # this sounds a lot like a signal handler and probably has
                # useful information, so raise it without modification.
                raise

            raise dbt.exceptions.RuntimeException(e)

    def add_query(self, sql, auto_begin=True, bindings=None, abridge_sql_log=False):

        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()

        logger.debug('Using {} connection "{}".'.format(self.TYPE, connection.name))

        with self.exception_handler(sql):
            if abridge_sql_log:
                logger.debug("On %s: %s....", connection.name, sql[0:512])
            else:
                logger.debug("On %s: %s", connection.name, sql)
            pre = time.time()

            cursor = connection.handle.cursor()

            # pyodbc does not handle a None type binding!
            if bindings is None:
                cursor.execute(sql)
            else:
                logger.debug(f"bindings set as {bindings}")
                cursor.execute(sql, bindings)

            logger.debug(
                "SQL status: %s in %0.2f seconds",
                self.get_status(cursor),
                (time.time() - pre),
            )

            return connection, cursor

    @classmethod
    def open(cls, connection):

        if connection.state == "open":
            logger.debug("Connection is already open, skipping open.")
            return connection

        credentials = connection.credentials

        MASKED_PWD = (
            credentials.PWD[0] + ("*" * len(credentials.PWD))[:-2] + credentials.PWD[-1]
        )
        try:
            con_str = []
            con_str.append(f"DRIVER={{{credentials.driver}}}")
            con_str.append(f"SERVER={credentials.host}")
            con_str.append(f"Database={credentials.database}")

            if credentials.authentication == "TrustedConnection":
                con_str.append("trusted_connection=yes")
            else:
                con_str.append(f"AUTHENTICATION={credentials.authentication}")
                con_str.append(f"UID={credentials.UID}")
                con_str.append(f"PWD={credentials.PWD}")

            con_str_concat = ";".join(con_str)
            con_str[-1] = f"PWD={MASKED_PWD}"
            con_str_masked = ";".join(con_str)

            logger.debug(f"Using connection string: {con_str_masked}")
            del con_str

            handle = pyodbc.connect(con_str_concat, autocommit=True)

            connection.state = "open"
            connection.handle = handle
            logger.debug(f"Connected to db: {credentials.database}")

        except pyodbc.Error as e:
            logger.debug(f"Could not connect to db: {e}")

            connection.handle = None
            connection.state = "fail"

            raise dbt.exceptions.FailedToConnectException(str(e))

        return connection

    def cancel(self, connection):
        connection.handle.close()
        pass

    @classmethod
    def get_credentials(cls, credentials):
        return credentials

    @classmethod
    def get_status(cls, cursor):
        # return cursor.statusmessage
        return "OK"

    def execute(self, sql, auto_begin=False, fetch=False):
        _, cursor = self.add_query(sql, auto_begin)
        status = self.get_status(cursor)
        if fetch:
            table = self.get_result_from_cursor(cursor)
        else:
            table = dbt.clients.agate_helper.empty_table()
        return status, table

    def add_begin_query(self):
        pass
        # return self.add_query('BEGIN TRANSACTION', auto_begin=False)

    def add_commit_query(self):
        pass
        # return self.add_query('COMMIT', auto_begin=False)

    @classmethod
    def get_result_from_cursor(cls, cursor):
        data = []
        column_names = []

        if cursor.description is not None:
            column_names = [col[0] for col in cursor.description]
            ## azure likes to give us empty string column names for scalar queries
            for i, col in enumerate(column_names):
                if col == "":
                    column_names[i] = f"Column{i+1}"
                    logger.debug(
                        f"substituted empty column name in position {i} with `Column{i+1}`"
                    )
            rows = cursor.fetchall()
            data = cls.process_results(column_names, rows)
        try:
            return dbt.clients.agate_helper.table_from_data(data, column_names)
        except Exception as e:
            logger.debug(f"failure with rows: {rows}")
            logger.debug(f"Failure with data: {data}")
            logger.debug(f"Failure with column_names: {column_names}")
            raise e

    @classmethod
    def process_results(cls, column_names, rows):
        return [dict(zip(column_names, row)) for row in rows]
