import datetime
import os
import re
from collections import OrderedDict
from typing import Optional
from urllib.parse import urljoin

from collections import Counter

import nltk
import numpy as np
import requests
from celery import Celery, current_task
from celery.signals import worker_process_init
from requests.adapters import HTTPAdapter
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    RetryError,
    Timeout,
)
from urllib3.util.retry import Retry

LOOP = 3
request_error_codes = (
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
    Timeout,
    ConnectionError,
    RetryError,
)
EXCEPTION_MESSAGE = "Not able to access the API; \
    please give the access token if not already given to circumvent the rate limit issue, recheck the organization name, or try again later."
NO_DATA_MESSAGE = "No data available."

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)
celery.conf.worker_proc_alive_timeout = 10


def dialogue_act_features(post):
    features = {}
    for word in nltk.word_tokenize(post):
        features["contains({})".format(word.lower())] = True
    return features


classifier = None


@worker_process_init.connect()
def setup(**kwargs):
    nltk.download("nps_chat")
    nltk.download("punkt")
    posts = nltk.corpus.nps_chat.xml_posts()[:10000]

    featuresets = [
        (dialogue_act_features(post.text), post.get("class")) for post in posts
    ]
    size = int(len(featuresets) * 0.1)
    train_set, _ = featuresets[size:], featuresets[:size]
    global classifier
    classifier = nltk.NaiveBayesClassifier.train(train_set)


def find_nearest(array, value):
    """
    This function finds the nearest value in the array to the value passed in.
    This is essential when the date we're searching for is not present. In this case, we need to find the nearest date.
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


@celery.task(name="stargrowth")
def stargrowth(
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    if access_token:
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
            "Authorization": "token %s" % access_token,
        }
    else:
        headers = {
            "Accept": "application/vnd.github.v3.star+json",
        }

    api_prefix = urljoin("https://api.github.com/repos/", github_api) + "/"

    stargazers_url = urljoin(api_prefix, "stargazers?per_page=100")

    retry_strategy = Retry(
        total=LOOP,
        status_forcelist=[429, 500, 502, 503, 504, 403],
        backoff_factor=0.2,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    assert_status_hook = lambda response, * \
        args, **kwargs: response.raise_for_status()
    session.hooks["response"] = [assert_status_hook]

    try:
        response = session.get(stargazers_url, headers=headers)
    except request_error_codes:
        return EXCEPTION_MESSAGE

    # get the number of pages where every page has 100 stargazers
    pages = 1 if response.json() else 0

    # get start date
    global_start_date = response.json()[0]["starred_at"] if pages else None

    pattern = re.compile("(.*)page=(.*)$")
    if "last" in response.links.keys():
        match = pattern.match(response.links["last"]["url"])
        pages = int(match.group(2))

    def binary_search(array, low, high, key):
        """
        BINARY SEARCH

        This function binary searches the array [1, ..., pages] and returns the page that contains the key, i.e., the previous date to determine the number of stargazers between the previous date and the current date.

        NOTE: The stargazers API specifies starred_at dates in ascending order.

        ALGORITHM

        After retrieving the middle page at the start of the loop, (mid - 1) and (mid + 1) pages are retrieved.

        Why?

        Every page has certain set of stargazers where the first and last entries's starred_at fields specify the start and end dates of that specific page respectively.
        To determine if the key (previous date) is within the page's date range, we check if the date lies between the start and end dates.
        However, we miss the dates that fall between the previous page's and next page's last and first dates, respectively, and the current page's start and end date.

        For example, consider the current page's first starred_at entry is 2021-11-19T00:00:00Z and last entry is 2021-11-20T00:00:00Z, previous page's last entry is 2021-11-14T00:00:00Z and next page's first entry is 2021-11-25T00:00:00Z.
        If we retrieve date range between 2021-11-19T00:00:00Z and 2021-11-20T00:00:00Z, we miss the date range between:
            * 2021-11-14T00:00:00Z and 2021-11-19T00:00:00Z
            * 2021-11-20T00:00:00Z and 2021-11-25T00:00:00Z

        Hence, we retrieve every page's previous and successive pages using (mid - 1) and (mid + 1).
        We consider previous page's last date as the start date and next page's first date as the last date.
        As per our example, our search space would now be from 2021-11-14T00:00:00Z to 2021-11-25T00:00:00Z!

        Lastly, when the right date range for the key is retrieved, the relevant page number is returned.
        """
        if high >= low:
            mid = (high + low) // 2

            start_date = None
            end_date = None

            if 1 <= mid - 1 <= pages:
                index = -1
                try:
                    temp_response_one = session.get(
                        urljoin(
                            api_prefix, f"stargazers?per_page=100&page={mid-1}"),
                        headers=headers,
                    )
                except request_error_codes as e:
                    return EXCEPTION_MESSAGE
            else:
                # else part handles the case when mid - 1 is an invalid page number.
                # In this case, we set start_date to the current page's start date (but not the previous page's last date).
                index = 0
                try:
                    temp_response_one = session.get(
                        urljoin(
                            api_prefix, f"stargazers?per_page=100&page={mid}"),
                        headers=headers,
                    )
                except request_error_codes as e:
                    return EXCEPTION_MESSAGE

            start_date = datetime.datetime.strptime(
                temp_response_one.json()[
                    index]["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

            if 1 <= mid + 1 <= pages:
                index = 0
                try:
                    temp_response_two = session.get(
                        urljoin(
                            api_prefix, f"stargazers?per_page=100&page={mid+1}"),
                        headers=headers,
                    )
                except request_error_codes as e:
                    return EXCEPTION_MESSAGE
            # else part handles the case when mid + 1 is an invalid page number.
            # In this case, we set end_date to the current page's end date (but not the successive page's start date).
            else:
                index = -1
                try:
                    temp_response_two = session.get(
                        urljoin(
                            api_prefix, f"stargazers?per_page=100&page={mid}"),
                        headers=headers,
                    )
                except request_error_codes as e:
                    return EXCEPTION_MESSAGE

            end_date = datetime.datetime.strptime(
                temp_response_two.json()[
                    index]["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

            # check if the key lies between start_date and end_date
            if (start_date and end_date) and (start_date <= key <= end_date):
                return mid
            elif start_date and key < start_date:
                return binary_search(array, low, mid - 1, key)
            else:
                return binary_search(array, mid + 1, high, key)
        else:
            return -1

    if pages == 0:
        return NO_DATA_MESSAGE

    # loop through pages -- create an array
    array = list(range(1, pages + 1))

    result_stars_dict = OrderedDict()
    year = None

    def populate_result(now, cummulative_count, year=None):
        if not year:
            year = now.year
        if now.year != year:
            result_stars_dict[f"{now.year} {now.month}/{now.day}"] = cummulative_count
            year = now.year
        else:
            result_stars_dict[f"{now.month}/{now.day}"] = cummulative_count

        return year

    previous_datetime = datetime.datetime.now()
    remaining_stars_in_page = 0
    visited_flag = False

    def last_page_star_count():
        try:
            last_page = session.get(
                urljoin(api_prefix, f"stargazers?per_page=100&page={pages}"),
                headers=headers,
            )
        except request_error_codes:
            return EXCEPTION_MESSAGE

        return len(last_page.json())

    for i, _ in enumerate(range(timedelta_frequency)):
        # fetch time
        now = previous_datetime
        previous_datetime = now - datetime.timedelta(days=timedelta)

        # return the resultant page number (the one where we have our previous date)
        result = binary_search(array, 1, len(array), previous_datetime)

        if result == -1:
            number_of_stars = 0

            # if the "result" was positive earlier, i.e., if previous_date lies within the stars' date range,
            # we need not fetch the total number of stars because remaining_stars_in_page would be populated already.
            if not visited_flag and previous_datetime < datetime.datetime.strptime(
                global_start_date, "%Y-%m-%dT%H:%M:%SZ"
            ):
                # If the previous date is before the first page's start date, then we need to fetch the total number of stars
                # For example: if the first page's start date is 2021-11-14T00:00:00Z, and our previous date is 2021-11-21T00:00:00Z,
                # then we need not fetch the star count because 2021-11-21T00:00:00Z isn't within the overall date range.
                number_of_stars = (pages - 1) * 100 + last_page_star_count()
            elif visited_flag:
                number_of_stars = remaining_stars_in_page + \
                    ((len(array) - 1) * 100)

            year = populate_result(now, number_of_stars, year)
            continue
        elif isinstance(result, int):
            stars_last_page = 0
            page_stars = 0

            # fetch result page
            try:
                result_page_response = session.get(
                    urljoin(
                        api_prefix, f"stargazers?per_page=100&page={result}"),
                    headers=headers,
                )
            except request_error_codes as e:
                return EXCEPTION_MESSAGE

            result_page = result_page_response.json()

            # fetch starred dates of the resultant page as a list
            starred_at = [
                datetime.datetime.strptime(
                    x["starred_at"], "%Y-%m-%dT%H:%M:%SZ")
                for x in result_page
            ]

            if not visited_flag:
                if result != pages:
                    # Only if the resultant page number is not in the last page, will we enter this branch and fetch number of stars from the last page.
                    # This condition is to handle the case when the last page has less than 100 stargazers.
                    stars_last_page = last_page_star_count()
            else:
                if result != pages:
                    stars_last_page = remaining_stars_in_page
                else:
                    stars_last_page = -(len(starred_at) -
                                        remaining_stars_in_page)

            if result_page and (
                datetime.datetime.strptime(
                    result_page[0]["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
                <= previous_datetime
                <= datetime.datetime.strptime(
                    result_page[-1]["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
            ):
                # find the nearest date to the previous date from the starred dates
                index = int(find_nearest(starred_at, previous_datetime))

                if starred_at[index] >= previous_datetime:
                    """
                    If the resultant date is greater than or equal to the previous date, consider the resultant date as well.
                    For example, if the date we're searching for is 2021-11-19T00:00:00Z. Assume it isn't present in the stargazers result but we have 2021-11-20T00:00:00Z and 2021-11-18T00:00:00Z.
                    The date we need to count our stars from starts from the date 2021-11-20T00:00:00Z but not from 2021-11-18T00:00:00Z.
                    If 2021-11-20T00:00:00Z is what we are retrieving, we blindly go by the logic: len(starred_at) - start
                    (if we have 100 stars and the date we retrieved is at the index 5, then it is 100 - 5 = 95 stars).
                    """
                    page_stars = len(result_page) - index
                else:
                    # else part handles the case when the nearest resultant date is less than the previous date (but, stars must start from previous date).
                    # Hence, let's ignore the nearest date by subtracting 1 from the index.
                    page_stars = (len(result_page) - index) - 1
            elif result_page:
                """
                else part handles the case when the previous date is not present in the result page.
                This means the date is present in two possible ranges:
                * The first range is from the last date of the previous page to the first date of the resultant page.
                * The second range is from the last date of the resultant page to the first date of the successive page.
                """
                if previous_datetime < datetime.datetime.strptime(
                    result_page[0]["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
                ):
                    # we blindly consider all stars of the current page if the previous date (the date we searched for) is less than the start date of the current page
                    page_stars = len(result_page)
                else:
                    # if the previous date is greater than the last date of the current page (which should be the case in else), we do not consider stars in the current page.
                    # We only consider stars in the successive page as computed below.
                    page_stars = 0

            remaining_stars_in_page = len(result_page) - page_stars
            visited_flag = True

            # calculate number of stars in all pages starting from (resultant page + 1) to (last page - 1).
            # NOTE: we already computed the number of stars in the last and resultant/current page.
            # implement this logic only if resultant page is not the last page.
            remaining_pages_stars = 100 * \
                (pages - result - 1) if pages > result else 0

            # finally, compute the total number of stars for the last 30 days
            cummulative_count = remaining_pages_stars + stars_last_page + page_stars

            year = populate_result(now, cummulative_count, year)
        else:
            # ERROR
            break

        current_task.update_state(
            state="PROGRESS", meta={"current": i + 1, "total": timedelta_frequency}
        )

        # unset & set variables
        pages = result
        array = list(range(1, pages + 1))

    return {"graph_data": OrderedDict(reversed(list(result_stars_dict.items())))}


@celery.task(name="openissuegrowth")
def openissuegrowth(
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
    issue_stats: bool = False,
):
    """
    NOTE: Every PR is an issue.
    """
    if access_token:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token %s" % access_token,
        }
    else:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

    api_prefix = urljoin("https://api.github.com/repos/", github_api) + "/"
    retry_strategy = Retry(
        total=LOOP,
        status_forcelist=[429, 500, 502, 503, 504, 403],
        backoff_factor=0.2,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    assert_status_hook = lambda response, * \
        args, **kwargs: response.raise_for_status()
    session.hooks["response"] = [assert_status_hook]

    issues_url = urljoin(api_prefix, "issues?per_page=100")

    response = None
    try:
        response = session.get(issues_url, headers=headers)
    except request_error_codes:
        return EXCEPTION_MESSAGE

    issue_map = None
    no_of_issues = 0
    if issue_stats:
        no_of_issues = 50
        issue_map = {"addressed": [], "unaddressed": []}
        issues = response.json()
        for issue_index, each_issue in enumerate(issues[:no_of_issues]):
            if "pull_request" not in each_issue and each_issue["state"] == "open":
                issue_open_state = "unaddressed"
                timeline_url = each_issue["timeline_url"]
                try:
                    timeline = session.get(
                        urljoin(timeline_url, "?per_page=100"),
                        headers=headers,
                    )
                except request_error_codes:
                    return EXCEPTION_MESSAGE

                pattern = re.compile("(.*)page=(.*)$")
                pages = 1 if timeline.json() else 0
                if "last" in timeline.links.keys():
                    match = pattern.match(timeline.links["last"]["url"])
                    pages = int(match.group(2))

                timeline_last_page = None
                try:
                    if pages:
                        timeline_last_page = session.get(
                            urljoin(timeline_url,
                                    f"?per_page=100&page={pages}"),
                            headers=headers,
                        ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE

                last_timeline_event = (
                    timeline_last_page[-1] if timeline_last_page else None
                )
                if (
                    last_timeline_event
                    and last_timeline_event["event"] == "cross-referenced"
                    and last_timeline_event["source"]["issue"]["state"] == "closed"
                ):
                    issue_open_state = "addressed"
                elif each_issue["comments"] > 0:
                    comments_url = each_issue["comments_url"]
                    try:
                        comments_list = session.get(
                            comments_url,
                            headers=headers,
                        ).json()
                    except request_error_codes:
                        return EXCEPTION_MESSAGE
                    if classifier.classify(
                        dialogue_act_features(comments_list[-1]["body"])
                    ) in ["whQuestion", "ynQuestion"]:
                        issue_open_state = "unaddressed"
                    else:
                        issue_open_state = "addressed"

                issue_map[issue_open_state].append(
                    {
                        "url": each_issue["html_url"],
                        "title": each_issue["title"],
                    }
                )

            current_task.update_state(
                state="PROGRESS",
                meta={"current": issue_index + 1,
                      "total": timedelta_frequency + 50},
            )

    # get the number of pages if every page has 100 issues
    pages = 1 if response.json() else 0
    pattern = re.compile("(.*)page=(.*)$")
    if "last" in response.links.keys():
        match = pattern.match(response.links["last"]["url"])
        pages = int(match.group(2))

    def binary_search(array, low, high, key):
        """
        BINARY SEARCH

        This function binary searches the array [1, ..., pages] and returns the page that contains the key, i.e., the previous date to determine the number of stargazers between the previous date and the current date.

        NOTE: The issues API specifies created_at dates in descending order.

        ALGORITHM

        After retrieving the middle page at the start of the loop, (mid - 1) and (mid + 1) pages are retrieved.

        Why?

        Every page has a certain set of issues where the first and last entries's created_at fields specify the end and start dates of that specific page respectively.
        To determine if key (previous date) is within the page's date range, we check if the date lies between the start and end dates.
        However, we miss the dates that fall between the previous page's and next page's last and first dates, respectively, and the current page's start and end date.

        For example, consider the current page's first created_at entry is 2021-11-20T00:00:00Z and last entry is 2021-11-10T00:00:00Z, previous page's last date is 2021-11-21T00:00:00Z and next page's first date is 2021-11-09T00:00:00Z.
        If we retrieve date range between 2021-11-20T00:00:00Z and 2021-11-10T00:00:00Z, we miss the date range between:
            * 2021-11-21T00:00:00Z and 2021-11-20T00:00:00Z
            * 2021-11-10T00:00:00Z and 2021-11-09T00:00:00Z

        Hence, we retrieve every page's previous and successive pages using (mid - 1) and (mid + 1).
        We consider previous page's last date as the end date and next page's first date as the start date (as the entries are in descending order).
        As per our example, our search space would now be from 2021-11-21T00:00:00Z (end date) to 2021-11-09T00:00:00Z (start date)!

        Lastly, when we retrive the right date range for our key, the relevant page number is returned.
        """
        if high >= low:
            mid = (high + low) // 2

            start_date = None
            end_date = None

            if 1 <= mid - 1 <= pages:
                index = -1
                try:
                    temp_response_one = session.get(
                        urljoin(
                            api_prefix, f"issues?per_page=100&page={mid-1}"),
                        headers=headers,
                    ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE
            else:
                # else part handles the case when mid - 1 is an invalid page number.
                # In this case, we set end_date to the current page's first date (but not the previous page's last date).
                index = 0
                try:
                    temp_response_one = session.get(
                        urljoin(api_prefix, f"issues?per_page=100&page={mid}"),
                        headers=headers,
                    ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE

            end_date = datetime.datetime.strptime(
                temp_response_one[index]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

            if 1 <= mid + 1 <= pages:
                index = 0
                try:
                    temp_response_two = session.get(
                        urljoin(
                            api_prefix, f"issues?per_page=100&page={mid+1}"),
                        headers=headers,
                    ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE

            # else part handles the case when mid + 1 is an invalid page number.
            # In this case, we set start_date to the current page's last date (but not the successive page's first date).
            else:
                index = -1
                try:
                    temp_response_two = session.get(
                        urljoin(api_prefix, f"issues?per_page=100&page={mid}"),
                        headers=headers,
                    ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE

            start_date = datetime.datetime.strptime(
                temp_response_two[index]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            )

            # check if key lies between start_date and end_date
            if start_date <= key <= end_date:
                return mid
            elif key > end_date:
                return binary_search(array, low, mid - 1, key)
            else:
                return binary_search(array, mid + 1, high, key)
        else:
            return -1

    if pages == 0:
        return NO_DATA_MESSAGE

    # loop through pages -- create an array
    array = list(range(1, pages + 1))

    result_issues_dict = OrderedDict()
    year = None

    def populate_result(now, cummulative_count, year=None):
        if not year:
            year = now.year
        if now.year != year:
            result_issues_dict[f"{now.year} {now.month}/{now.day}"] = cummulative_count
            year = now.year
        else:
            result_issues_dict[f"{now.month}/{now.day}"] = cummulative_count

        return year

    previous_datetime = datetime.datetime.now()
    remaining_issues_in_page = 0
    low_bound = 1
    visited_flag = False

    for i, _ in enumerate(range(timedelta_frequency)):
        # fetch time
        now = previous_datetime
        previous_datetime = now - datetime.timedelta(days=timedelta)

        # return the resultant page number (the one where we have our previous date)
        result = binary_search(array, 1, len(array), previous_datetime)

        if result == -1:
            last_page_response = None
            number_of_stars = 0

            # fetch last page
            if array:
                try:
                    last_page_response = session.get(
                        urljoin(
                            api_prefix, f"issues?per_page=100&page={array[-1]}"),
                        headers=headers,
                    ).json()
                except request_error_codes:
                    return EXCEPTION_MESSAGE

            # if the "result" was positive earlier, i.e., if previous_date lies within the issues' date range,
            # then we need not fetch the total number of issues because remaining_issues_in_page would be populated already.
            if (not visited_flag) and last_page_response:
                # If previous datetime is less than the last date of the last page, i.e., the start date,
                # then we need to fetch the total number of issues.
                # For example: if the last page's last date is 2021-11-14T00:00:00Z, and our previous date is 2021-11-21T00:00:00Z,
                # then we need not fetch the issue count because 2021-11-21T00:00:00Z isn't within the overall date range.
                if previous_datetime < datetime.datetime.strptime(
                    last_page_response[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                ):
                    number_of_stars = (pages - 1) * 100 + \
                        len(last_page_response)
            elif visited_flag:
                number_of_stars = remaining_issues_in_page
                +((len(array) - 2) * 100 if len(array) > 2 else 0)
                +(len(last_page_response) if len(array) >= 2 else 0)

            # if the previous date isn't present in the list of dates
            year = populate_result(
                now,
                number_of_stars,
                year,
            )
            continue
        elif isinstance(result, int):
            # fetch result page
            try:
                result_page = session.get(
                    urljoin(api_prefix, f"issues?per_page=100&page={result}"),
                    headers=headers,
                ).json()
            except request_error_codes:
                return EXCEPTION_MESSAGE

            # fetch created_at dates of the resultant page as a list
            created_at = [
                datetime.datetime.strptime(
                    x["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                for x in result_page
            ]

            if visited_flag:
                if low_bound == result:
                    remaining_issues_in_page = -(
                        len(result_page) - remaining_issues_in_page
                    )

            if result_page and (
                datetime.datetime.strptime(
                    result_page[-1]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
                <= previous_datetime
                <= datetime.datetime.strptime(
                    result_page[0]["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                )
            ):
                # find the nearest date to the previous month's date from created_at dates
                index = int(find_nearest(created_at, previous_datetime))

                if created_at[index] >= previous_datetime:
                    """
                    If the resultant date is greater than or equal to previous month's date, consider the resultant date as well.
                    For example, if the date we're searching for is 2021-11-19T00:00:00Z. Assume it isn't present in the issues result but we have 2021-11-20T00:00:00Z and 2021-11-18T00:00:00Z.
                    The date we need to count our issues from starts from the date 2021-11-20T00:00:00Z but not from 2021-11-18T00:00:00Z.
                    If 2021-11-20T00:00:00Z is what we are retrieving, we blindly go by the logic: index + 1.
                    (if we have 100 issues and the date we retrieved is at index 5
                    (note that 5 if five steps away from the most recent issue), then it is 5 + 1 = 6 issues).
                    NOTE: since index starts from 0, we need to add 1 to the index.
                    """
                    page_issues = index + 1
                else:
                    """
                    else part handles the case when the nearest resultant date is less than the previous date.
                    In this case, we shouldn't consider the nearest date, hence we wouldn't add 1 to the index (this automically deletes one entry ~ the nearest date entry).
                    """
                    page_issues = index

            elif result_page:
                """
                else part handles the case when the previous date is not present in the result page.
                This means that the date is present in two possible ranges:
                * The first range is from the last date of the previous page to the first date of the resultant page.
                * The second range is from the last date of the resultant page to the first date of the successive page.
                """
                if previous_datetime > result_page[0]["created_at"]:
                    """
                    If the previous month's date is greater than the start date of the current page, we do not consider stars in the current page.
                    We only consider stars in the successive page as computed below.
                    """
                    page_issues = 0
                else:
                    """
                    We blindly consider all stars of the current page if the previous date (the date we searched for) is less than the end date of the current page.
                    """
                    page_issues = len(result_page)

            # calculates issues of all pages starting from first page to (resultant page - 1).
            # NOTE: we already computed stars in the resultant page.
            if not visited_flag:
                remaining_pages_issues = (
                    100 * (result - low_bound) if result > low_bound else 0
                )
            else:
                remaining_pages_issues = (
                    100 * (result - low_bound - 1) if result > low_bound else 0
                )

            # finally, compute the total number of issues in the last x days
            cummulative_count = (
                remaining_pages_issues + page_issues + remaining_issues_in_page
            )

            remaining_issues_in_page = len(result_page) - page_issues

            # flag to indicate whether there has been a "result" hit
            visited_flag = True

            year = populate_result(now, cummulative_count, year)
        else:
            # ERROR
            break

        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1 + no_of_issues,
                "total": timedelta_frequency + no_of_issues,
            },
        )

        # unset & set variables
        low_bound = result
        array = list(range(low_bound, pages + 1))

    return {
        "graph_data": OrderedDict(reversed(list(result_issues_dict.items()))),
        "issue_map": issue_map,
    }


@celery.task(name="contributorgrowth")
def contributorgrowth(
    github_api: str,
    access_token: Optional[str] = None,
    timedelta: int = 7,
    timedelta_frequency: int = 2,
):
    if access_token:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token %s" % access_token,
        }
    else:
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

    api_prefix = urljoin("https://api.github.com/repos/", github_api) + "/"
    retry_strategy = Retry(
        total=LOOP,
        status_forcelist=[429, 500, 502, 503, 504, 403],
        backoff_factor=0.2,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    assert_status_hook = lambda response, * \
        args, **kwargs: response.raise_for_status()
    session.hooks["response"] = [assert_status_hook]

    previous_datetime = datetime.datetime.now()

    result_contributors_dict = OrderedDict()
    year = None

    def populate_result(now, new_contributors, year=None):
        if not year:
            year = now.year
        if now.year != year:
            result_contributors_dict[
                f"{now.year} {now.month}/{now.day}"
            ] = int(new_contributors)
            year = now.year
        else:
            result_contributors_dict[f"{now.month}/{now.day}"] = int(
                new_contributors)

        return year

    for i, _ in enumerate(range(timedelta_frequency)):
        # fetch time
        now = previous_datetime
        previous_datetime = now - datetime.timedelta(days=timedelta)
        previous_datetime_iso = previous_datetime.strftime(
            "%Y-%m-%dT%H:%M:%SZ")

        # fetch commits for the last n days
        commits_url = urljoin(
            api_prefix, f"commits?since={previous_datetime_iso}&per_page=100"
        )
        try:
            commits_raw = session.get(commits_url, headers=headers)
        except request_error_codes:
            return EXCEPTION_MESSAGE

        commit_growth = commits_raw.json()

        while "next" in commits_raw.links.keys():
            try:
                commits_raw = session.get(
                    commits_raw.links["next"]["url"], headers=headers
                )
            except request_error_codes:
                return EXCEPTION_MESSAGE
            commit_growth.extend(commits_raw.json())

        contributor_names = []
        for commit in commit_growth:
            if "author" in commit and commit["author"] and "login" in commit["author"]:
                contributor_names.append(commit["author"]["login"])
            else:
                contributor_names.append(commit["commit"]["author"]["name"])

        # count the number of commits per contributor
        contributor_count = Counter(contributor_names)

        contributors_url = urljoin(
            api_prefix, "contributors?per_page=100&anon=1")

        try:
            contributors_raw = session.get(contributors_url, headers=headers)
        except request_error_codes:
            return EXCEPTION_MESSAGE

        def get_contributors(contributors_raw, new_contributors=0):
            """
            Loop through contributors page by page and validate if the contributor is new or not.
            """
            for contributor in contributors_raw.json():
                contributor_name = None

                # the first 500 contributors have GitHub info associated so "login" key would exist.
                # the rest of the contributors are anonymous so "login" key would not exist; instead we'd have to use the "name" key.
                if "login" in contributor and contributor["login"] in contributor_count:
                    contributor_name = contributor["login"]
                elif "name" in contributor and contributor["name"] in contributor_count:
                    contributor_name = contributor["name"]

                if contributor_name:
                    # if number of contributions for the last n days is equal to the total number of contributions, then the contributor is new
                    if (
                        contributor_name in contributor_count
                        and contributor_count[contributor_name]
                        == contributor["contributions"]
                    ):
                        new_contributors += 1

                    # delete the evaluated contributor from the list
                    del contributor_count[contributor_name]

            return new_contributors

        def contributors_helper(contributors_raw):
            try:
                contributors_raw = requests.get(
                    contributors_raw.links["next"]["url"], headers=headers
                )
            except request_error_codes:
                return EXCEPTION_MESSAGE
            return contributors_raw

        new_contributors = 0
        if contributor_count:
            # first iteration
            new_contributors = get_contributors(contributors_raw)

            # second,..., nth iteration
            while "next" in contributors_raw.links.keys():
                contributors_raw = contributors_helper(contributors_raw)
                new_contributors = get_contributors(
                    contributors_raw, new_contributors)

                # if there are no more contributors to evaluate, then break the loop
                if not len(contributor_count):
                    break

        year = populate_result(now, new_contributors, year)

        current_task.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": timedelta_frequency,
            },
        )

    return {
        "graph_data": OrderedDict(reversed(list(result_contributors_dict.items()))),
    }
