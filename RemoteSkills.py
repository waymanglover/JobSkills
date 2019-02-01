# Standard library dependencies
import datetime
import json
import xml.etree.ElementTree as ElementTree
from typing import List

# External dependencies
import requests

# Internal dependencies
from DatabaseHelper import DatabaseHelper
from JobBoardModel import JobBoardModel
from JobModel import JobModel

Response = requests.Response
Element = ElementTree.Element

# Constants
# TODO: Move to config/arg/both
JOB_BOARD_URL: str = (
    'https://weworkremotely.com/categories/remote-programming-jobs.rss'
    )


def main() -> None:
    response: JobBoardModel = getLatestResponse()
    if not response.isReadyForRefresh():
        print('Not ready for refresh.')
        return None
    # TODO: HTTP error handling. Assuming success for now.
    httpResponse: Response = requests.get(JOB_BOARD_URL)
    print(f"Got response: {httpResponse.text}")
    # TODO: Update interval from response?
    response = JobBoardModel(responseText=httpResponse.text,
                             lastRequested=datetime.datetime.now())
    writeToCache(response)
    rssResponse: Element = ElementTree.fromstring(response.responseText)
    jobModels: List[JobModel] = JobModel.fromRssResponse(rssResponse)

    with DatabaseHelper() as dbHelper:
        print('Opened DB')
        dbHelper.insert(jobModels)


def writeToCache(response: JobBoardModel) -> None:
    with open('cache', 'w') as cache:
        json.dump(response.__dict__, cache, default=jsonDefault)


def getLatestResponse() -> JobBoardModel:
    try:
        with open('cache', 'r') as cache:
            response: JobBoardModel = json.load(
                cache,
                object_hook=JobBoardModel.fromDict)
        return response
    except FileNotFoundError:
        # No response has been cached yet. Return an empty response.
        return JobBoardModel()


def jsonDefault(obj: object) -> str:
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} not serializable')


if __name__ == '__main__':
    main()
