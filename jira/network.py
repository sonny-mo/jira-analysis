import attr
import requests
from typing import List
from urllib.parse import urlencode, urljoin

from .auth import get_config
from .issue import StatusChange, JiraTicket
from .project import JiraProject


_JIRA_URL_BASE = "https://hotjar.atlassian.net/rest/api/3/"


def get_issues(project: JiraProject) -> List[JiraTicket]:
    issues = []
    config = get_config("./credentials.yaml")
    jira_url = urljoin(_JIRA_URL_BASE, "search")
    query = urlencode({"jql": "project={}".format(project.key), "expand": "changelog"})
    response = requests.get("{}?{}".format(jira_url, query), auth=attr.astuple(config))
    response_json = response.json()
    page_size, total = (
        response_json["maxResults"],
        response_json["total"],
    )
    issues.extend([JiraTicket.from_jira_ticket(t) for t in response_json["issues"]])

    for start in range(page_size, total, page_size):
        query = urlencode(
            {
                "jql": "project={}".format(project.key),
                "expand": "changelog",
                "startAt": start,
            }
        )
        response = requests.get(
            "{}?{}".format(jira_url, query), auth=attr.astuple(config)
        )
        response_json = response.json()
        issues.extend([JiraTicket.from_jira_ticket(t) for t in response_json["issues"]])
    return issues


def get_project(key: str) -> JiraProject:
    config = get_config("./credentials.yaml")
    response = requests.get(
        "https://hotjar.atlassian.net/rest/api/3/project/{key}".format(key=key),
        auth=attr.astuple(config),
    )
    return JiraProject.from_jira_project(response.json())


def get_issue(key: str) -> JiraTicket:
    config = get_config("./credentials.yaml")
    response = requests.get(
        "https://hotjar.atlassian.net/rest/api/3/issue/{key}?expand=changelog".format(
            key=key
        ),
        auth=attr.astuple(config),
    )
    return JiraTicket.from_jira_ticket(response.json())