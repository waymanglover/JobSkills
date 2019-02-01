# Standard library dependencies
import datetime as dt
import xml.etree.ElementTree as ElementTree
from typing import Dict, List, Optional

Element = ElementTree.Element
datetime = dt.datetime


class JobModel():
    title: str = ""
    description: str = ""
    published: Optional[datetime] = None
    link: str = ""

    def handleChildElement(self, tag: str, text: str) -> None:
        if tag == 'title':
            self.title = text
        elif tag == 'description':
            self.description = text
        elif tag == 'pubDate':
            self.published = JobModel.parsePubDate(text)
        elif tag == 'link':
            self.link = text

    def toDict(self) -> Dict[str, str]:
        publishedStr: str = ''
        if self.published is not None:
            publishedStr = self.published.isoformat(sep=' ',
                                                    timespec='seconds')
        return {'link': self.link,
                'title': self.title,
                'description': self.description,
                'published': publishedStr}

    @classmethod
    def parsePubDate(cls, text: str) -> datetime:
        var: datetime = datetime.strptime(text, '%a, %d %b %Y %H:%M:%S %z')
        return var

    @classmethod
    def fromRssItem(cls, rssItem: Element) -> 'JobModel':
        # empty job model
        jobModel = cls()

        # Iterate through child elements of item
        for child in rssItem:
            if child.text is not None:
                jobModel.handleChildElement(child.tag, child.text)

        # append news dictionary to news items list
        return jobModel

    @classmethod
    def fromRssResponse(cls, rssResponse: Element) -> List['JobModel']:
        jobModels: List[JobModel] = []

        # Iterate items in RSS feed
        for item in rssResponse.findall('./channel/item'):
            jobModel: JobModel = JobModel.fromRssItem(item)
            jobModels.append(jobModel)

        return jobModels
