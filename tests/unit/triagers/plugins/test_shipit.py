#!/usr/bin/env python

import json
import logging
import shutil
import tempfile
import unittest

from tests.utils.issue_mock import IssueMock
from tests.utils.repo_mock import RepoMock
from tests.utils.helpers import get_issue
from ansibullbot.triagers.plugins.shipit import get_shipit_facts
from ansibullbot.wrappers.issuewrapper import IssueWrapper
from ansibullbot.wrappers.historywrapper import HistoryWrapper


class ModuleIndexerMock(object):

    def __init__(self, namespace_maintainers):
        self.namespace_maintainers = namespace_maintainers

    def get_maintainers_for_namespace(self, namespace):
        return self.namespace_maintainers


class TestShipitFacts(unittest.TestCase):

    def setUp(self):
        self.meta = {
            'is_new_module': False,
            'module_match': {
                'namespace': 'system',
                'maintainers': ['abulimov'],
            }
        }

    def test_submitter_is_maintainer(self):
        """
        Submitter is a namespace maintainer: approval must be automatically
        added
        """
        datafile = 'tests/fixtures/shipit/0_issue.yml'
        statusfile = 'tests/fixtures/shipit/0_prstatus.json'
        with get_issue(datafile, statusfile) as iw:
            namespace_maintainers = ['LinusU', 'mscherer']
            facts = get_shipit_facts(iw, self.meta, ModuleIndexerMock(namespace_maintainers), core_team=['bcoca'], botnames=['ansibot'])

            self.assertEqual(iw.submitter, 'mscherer')
            self.assertEqual(['LinusU', 'mscherer'], facts['community_usernames'])
            self.assertEqual(['mscherer'], facts['shipit_actors'])
            self.assertEqual(facts['shipit_count_ansible'], 0)     # bcoca
            self.assertEqual(facts['shipit_count_maintainer'], 0)  # abulimov
            self.assertEqual(facts['shipit_count_community'], 1)   # LinusU, mscherer
            self.assertFalse(facts['shipit'])

    def test_submitter_is_core_team_and_maintainer(self):
        """
        Submitter is a namespace maintainer *and* a core team member: approval
        must be automatically added
        https://github.com/ansible/ansible/pull/21620
        """
        datafile = 'tests/fixtures/shipit/1_issue.yml'
        statusfile = 'tests/fixtures/shipit/1_prstatus.json'
        with get_issue(datafile, statusfile) as iw:
            namespace_maintainers = ['LinusU']
            facts = get_shipit_facts(iw, self.meta, ModuleIndexerMock(namespace_maintainers), core_team=['bcoca', 'mscherer'], botnames=['ansibot'])

            self.assertEqual(iw.submitter, 'mscherer')
            self.assertEqual(['LinusU'], facts['community_usernames'])
            self.assertEqual(['LinusU', 'mscherer'], facts['shipit_actors'])
            self.assertEqual(facts['shipit_count_ansible'], 1)     # bcoca, mscherer
            self.assertEqual(facts['shipit_count_maintainer'], 0)  # abulimov
            self.assertEqual(facts['shipit_count_community'], 1)   # LinusU
            self.assertTrue(facts['shipit'])
