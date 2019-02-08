# Standard library dependencies
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, IO


class JobBoardModel():
    """Represents a job board response"""
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
        self.lastRequested = lastRequested
        if responseText is not None:
            self.responseText = responseText
        if interval is not None:
            self.interval = interval

    def isReadyForRefresh(self) -> bool:
        nextRequestTime: datetime = self.getNextRefreshTime()
        return datetime.now() >= nextRequestTime

    def getNextRefreshTime(self) -> datetime:
        if self.lastRequested is None or self.interval == 0:
            return datetime.now()
        delta: timedelta = timedelta(minutes=self.interval)
        nextRequestTime: datetime = self.lastRequested + delta
        return nextRequestTime

    def serialize(self, file: IO[str]) -> None:
        json.dump(self.__dict__, file, default=JobBoardModel.jsonDefault)

    @classmethod
    def deserialize(cls, file: IO[str]) -> 'JobBoardModel':
        jobBoard: JobBoardModel = json.load(file, object_hook=cls.fromDict)
        return jobBoard

    @classmethod
    def fromDict(cls, dct: Dict[str, str]) -> 'JobBoardModel':
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
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Type {type(obj)} not serializable')
