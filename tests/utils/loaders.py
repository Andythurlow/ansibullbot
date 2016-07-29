#!/usr/bin/env python

from datetime import datetime
from lib.wrappers.issuewrapper import IssueWrapper
from tests.utils.issue_mock import IssueMock
from tests.utils.issuetriager_mock import TriageIssuesMock

def get_triagermock_for_datafile(datafile):
    im = IssueMock(datafile)
    iw = IssueWrapper(repo=None, issue=im)
    triage = TriageIssuesMock(verbose=True)

    triage.issue = iw
    triage.issue.get_events()
    triage.issue.get_comments()

    # add additional mock data from fixture
    triage.force = True
    triage._now = im.ydata.get('_now', datetime.now())
    triage.number = im.ydata.get('number', 1)
    triage.github_repo = im.ydata.get('github_repo', 'core')
    triage.match = im.ydata.get('_match')
    triage.module_indexer.match = im.ydata.get('_match')
    triage._module = triage.match['name']
    triage._ansible_members = im.ydata.get('_ansible_members', [])
    triage._module_maintainers = im.ydata.get('_module_maintainers', [])

    return triage

