"""Class for representing a job board's state."""
# Standard library dependencies
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, IO


class JobBoardModel():
    """Represents a job board response."""

    # Note: These are initialized partly to work around
    # a VS code linting/typing bug.
    # TODO: Find link to bug description
    responseText: str = ""
    lastRequested: Optional[datetime] = None
    interval: int = 60

    def __init__(self,
                 responseText: Optional[str] = None,
                 lastRequested: Optional[datetime] = None,
                 interval: Optional[int] = None) -> None:
        """Create a JobBoardModel to represent the current job board state."""
        self.lastRequested = lastRequested
        if responseText is not None:
            self.responseText = responseText
        if interval is not None:
            self.interval = interval

    def isReadyForRefresh(self) -> bool:
        """Determine if we are ready to pull jobs from the job board."""
        nextRequestTime: datetime = self.getNextRefreshTime()
        return datetime.now() >= nextRequestTime

    def getNextRefreshTime(self) -> datetime:
        """Return the next time we should request jobs from the job board."""
        if self.lastRequested is None or self.interval == 0:
            return datetime.now()
        delta: timedelta = timedelta(minutes=self.interval)
        nextRequestTime: datetime = self.lastRequested + delta
        return nextRequestTime

    def serialize(self, file: IO[str]) -> None:
        """Dump the JSON representation of this object to a file."""
        json.dump(self.__dict__, file, default=JobBoardModel.jsonDefault)

    @classmethod
    def deserialize(cls, file: IO[str]) -> 'JobBoardModel':
        """Read the JSON representation of a JobBoardModel into an object."""
        jobBoard: JobBoardModel = json.load(file, object_hook=cls.fromDict)
        return jobBoard

    @classmethod
    def fromDict(cls, dct: Dict[str, str]) -> 'JobBoardModel':
        """Create a JobBoardModel from a dict containing its properties."""
        lastRequested: Optional[datetime] = None
        interval: Optional[int] = None

        lastRequestedStr: Optional[str] = dct.get('lastRequested', None)
        if lastRequestedStr is not None:
            lastRequested = datetime.fromisoformat(lastRequestedStr)

        intervalStr: Optional[str] = dct.get('interval', None)
        if intervalStr is not None:
            interval = int(intervalStr)

        return cls(responseText=dct.get('responseText', ''),
                   lastRequested=lastRequested,
                   interval=interval)

    @staticmethod
    def jsonDefault(obj: object) -> str:
        """Use with json.dump to serialize classes with datetime properties."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Type {type(obj)} not serializable')
