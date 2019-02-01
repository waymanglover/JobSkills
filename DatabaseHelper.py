# Standard library dependencies
import sqlite3
from types import TracebackType
from typing import Dict, List, Optional, Type

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
    """Helper class for accessing SQLite job/skills database"""
    connection: Optional[Connection] = None
    cursor: Optional[Cursor] = None

    def __enter__(self) -> 'DatabaseHelper':
        self.connect()
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[Exception],
                 exc_tb: Optional[TracebackType]) -> bool:
        self.close()
        return False

    def connect(self) -> None:
        self.connection = sqlite3.connect(DATABASE_FILENAME)
        self.cursor = self.connection.cursor()
        self.createTables()

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.commit()
            self.connection.close()
            self.connection = None

    def commit(self) -> None:
        assert(self.connection is not None)
        self.connection.commit()

    def createTables(self) -> None:
        assert(self.cursor is not None)
        self.cursor.execute(CREATE_JOBS_TABLE)
        self.commit()

    def insert(self, jobModels: List[JobModel]) -> None:
        assert(self.cursor is not None)
        print(f'Attempting insert of {len(jobModels)} jobs.')
        jobModelDicts: List[Dict[str, str]] = [jobModel.toDict()
                                               for jobModel in jobModels]
        self.cursor.executemany(INSERT_JOBS, jobModelDicts)
        self.commit()
