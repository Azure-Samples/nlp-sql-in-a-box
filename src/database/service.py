import logging

import pyodbc, struct
from azure.identity import DefaultAzureCredential
from faker import Faker

from .utils import table_exists, create_table, insert_record


logger = logging.getLogger(__name__)

scope = 'https://database.windows.net/.default'


# If you have issues connecting, make sure you have the correct driver installed
# ODBC Driver for SQL Server - https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
connection_string_template = 'DRIVER={driver};SERVER=tcp:{server_name}.database.windows.net,1433;DATABASE={database_name}'
driver = 'ODBC Driver 18 for SQL Server'


class Database:
    def __init__(self, server_name: str, database_name: str, credential: DefaultAzureCredential) -> None:
        token = credential.get_token(scope).token

        self.conn = get_connection(server_name=server_name, database_name=database_name, token=token)

    def setup(self) -> None:
        """
        Set up the database by creating the table and inserting fake records.
        """
        logger.debug("Setting up the database.")
        # Create a cursor object to execute SQL queries
        cursor = self.conn.cursor()

        if table_exists(cursor):
            # skip if table already exists
            return

        logger.debug("Creating table.")
        create_table(cursor)

        # Create Faker object
        fake = Faker()

        logger.debug("Generating and inserting records.")
        # Generate and insert 1,000 fake records
        for i in range(1000):
            insert_record(cursor, i, fake)

        # Commit the changes and close the connection
        self.conn.commit()

        logger.debug("Database setup completed.")

    def query(self, query: str) -> [pyodbc.Row]:
        """
        Query the database with the given SQL query.
        """
        cursor = self.conn.cursor()
        try:
            logger.debug("Querying database with: {}.".format(query))
            cursor.execute(query)
            result = cursor.fetchall()
            logger.debug("Successfully queried database: {}.".format(result))
        except Exception as ex:
            logger.error("Error querying database: {}.".format(ex))
            return "No Result Found"
        finally:
            cursor.close()

        return result


def get_connection(server_name: str, database_name: str, token: str) -> pyodbc.Connection:
    # see https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-python-quickstart
    token_bytes = token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    SQL_COPT_SS_ACCESS_TOKEN = 1256  # This connection option is defined by microsoft in msodbcsql.h

    connection_string = connection_string_template.format(driver=driver, server_name=server_name, database_name=database_name)
    return pyodbc.connect(connection_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
