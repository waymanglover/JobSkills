# Standard library dependencies
import datetime as dt
import re
import xml.etree.ElementTree as ElementTree
from typing import Dict, List, Optional

Element = ElementTree.Element
datetime = dt.datetime

# Constants
PUB_DATE_FORMAT: str = '%a, %d %b %Y %H:%M:%S %z'
REGEX_REMOVE_HTML_TAGS = re.compile(r'<.*?>')
REGEX_REMOVE_EXTRA_WHITESPACE = re.compile(r'\s{2,}')


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
    def fromRssItem(cls, rssItem: Element) -> 'JobModel':
        jobModel = cls()

        for child in rssItem:
            if child.text is not None:
                jobModel.handleChildElement(tag=child.tag, text=child.text)

        return jobModel

    @staticmethod
    def fromRssResponse(rssResponse: Element) -> List['JobModel']:
        jobModels: List[JobModel] = []

        for item in rssResponse.findall('./channel/item'):
            jobModel: JobModel = JobModel.fromRssItem(item)
            jobModels.append(jobModel)

        return jobModels

    @staticmethod
    def parseDescription(description: str) -> str:
        output: str = ''
        # This is a bit of a hack. It removes metadata (logo, HQ location,
        # company/application URLs) from the description. This would only be
        # correct for WeWorkRemotely and would break if they change the format.
        # Everything else so far should be generic enough to work for any job
        # board RSS feed.
        descriptionAsList: List[str] = description.split('\n')[7:-3]
        output = output.join(descriptionAsList)
        output = REGEX_REMOVE_HTML_TAGS.sub(string=output, repl=' ')
        output = REGEX_REMOVE_EXTRA_WHITESPACE.sub(string=output, repl=' ')
        return output.strip()

    @staticmethod
    def parsePubDate(pubDate: str) -> datetime:
        var: datetime = datetime.strptime(pubDate, PUB_DATE_FORMAT)
        return var
