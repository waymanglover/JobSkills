"""Class to provide helper methods for SQLite database access."""

# Standard library dependencies
import sqlite3
from types import TracebackType
from typing import Dict, List, Optional, Type, Any

# Internal dependencies
from JobModel import JobModel

Connection = sqlite3.Connection
Cursor = sqlite3.Cursor

# Constants
# TODO: Move to config/arg/both
DATABASE_FILENAME: str = 'skills.db'
CREATE_JOBS_TABLE: str = '''
    CREATE TABLE IF NOT EXISTS jobs
    (
        id INTEGER PRIMARY KEY,
        link TEXT,
        title TEXT,
        description TEXT,
        published TEXT,
        UNIQUE(link)
    )
    '''
INSERT_JOBS: str = '''
    INSERT OR IGNORE INTO jobs (link, title, description, published) VALUES
    (:link, :title, :description, :published)
    '''


class DatabaseHelper():
    """Helper class for accessing SQLite job/skills database."""

    # TODO: Connection has helper methods (ex: con.executemany) that would
    # save us the effort of holding on to a cursor. Not sure if that would
    # perform better/worse than caching our own cursor. I'd assume worse?
    # If we did switch to that, we could use the connection as the context
    # manager instead of manually committing. See:
    # https://docs.python.org/2/library/sqlite3.html#using-the-connection-as-a-context-manager
    connection: Optional[Connection] = None
    cursor: Optional[Cursor] = None

    def __enter__(self) -> 'DatabaseHelper':
        """Create database connection when used in a with block."""
        self.connect()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[Exception],
                 exc_tb: Optional[TracebackType]) -> bool:
        """Close database connection at the end of a with block."""
        self.close()
        return False

    def connect(self) -> None:
        """
        Create a database connection and save off the cursor.

        Also creates the required tables in the database, if they do not exist.
        """
        self.connection = sqlite3.connect(DATABASE_FILENAME)
        self.cursor = self.connection.cursor()
        self.createTables()

    def close(self) -> None:
        """Close any open database cursors and connections."""
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.commit()
            self.connection.close()
            self.connection = None

    def commit(self) -> None:
        """Commit the current transaction to the database."""
        assert(self.connection is not None)
        self.connection.commit()

    def createTables(self) -> None:
        """Create required tables in the database, if they don't exist."""
        assert(self.cursor is not None)
        self.cursor.execute(CREATE_JOBS_TABLE)
        self.commit()

    # Not sure why, but mypy can't determine the type of
    # self.cursor.rowcount. Believe it should be int,
    # but we have to annotate it as Any.
    def insert(self, jobModels: List[JobModel]) -> Any:
        """Insert all provided JobModels into the jobs table."""
        assert(self.cursor is not None)
        jobModelDicts: List[Dict[str, str]] = [jobModel.toDict()
                                               for jobModel in jobModels]
        self.cursor.executemany(INSERT_JOBS, jobModelDicts)
        self.commit()
        return self.cursor.rowcount
