# Standard library dependencies
import datetime
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
CACHE_FILENAME = 'cache'


def main() -> None:
    try:
        with open(CACHE_FILENAME, 'r') as cache:
            jobBoard: JobBoardModel = JobBoardModel.deserialize(cache)
    except FileNotFoundError:
        # Can't find cache. Assume no requests have been done yet.
        jobBoard = JobBoardModel()

    if not jobBoard.isReadyForRefresh():
        print('Not ready for refresh.')
        return None

    httpResponse: Response = requests.get(JOB_BOARD_URL)
    httpResponse.raise_for_status()

    print(f"Got response: {httpResponse.text}")
    # TODO: Update interval from response
    # RSS supplies a refresh interval (in minutes) for clients.
    # I don't expect it'll change often, so it's hard-coded for now.
    jobBoard = JobBoardModel(responseText=httpResponse.text,
                             lastRequested=datetime.datetime.now())

    with open(CACHE_FILENAME, 'w') as cache:
        jobBoard.serialize(cache)

    rssResponse: Element = ElementTree.fromstring(jobBoard.responseText)
    jobModels: List[JobModel] = JobModel.fromRssResponse(rssResponse)

    with DatabaseHelper() as dbHelper:
        print('Opened DB')
        dbHelper.insert(jobModels)


if __name__ == '__main__':
    main()
