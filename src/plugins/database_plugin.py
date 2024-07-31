import logging
from typing import Annotated, List

import pyodbc
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from src.database.service import Database


logger = logging.getLogger(__name__)


class DatabasePlugin:
    """DatabasePlugin provides a set of functions to access the database."""

    def __init__(self, db: Database) -> None:
        self.db = db

    @kernel_function(name="query", description="Query the database.")
    def query(self, query: Annotated[str, "The SQL query"]) -> Annotated[List[pyodbc.Row], "The rows returned"]:
        logger.info("Running database plugin with query: {}".format(query))
        return self.db.query(query)
