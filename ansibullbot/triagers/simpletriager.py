#!/usr/bin/env python

# This is a triager for the combined repos that should have happend
# in the 12-2016 timeframe.
#   https://groups.google.com/forum/#!topic/ansible-devel/mIxqxXRsmCI
#   https://groups.google.com/forum/#!topic/ansible-devel/iJouivmSSk4
#   https://github.com/ansible/proposals/issues/30

# Key features:
#   * daemonize mode that can continuously loop and process w/out scripts
#   * closed issues will also be processed (pygithub will kill ratelimits for
#     this, so use a new caching+index tool)
#   * open issues in ansible-modules-[core|extras] will be closed with a note
#     about pr|issue mover
#   * maintainers can be assigned to more than just the files in
#     lib/ansible/modules
#   * closed issues with active comments will be locked with msg about opening
#     new
#   * closed issues where submitter issues "reopen" command will be reopened
#   * false positives on module issue detection can be corrected by a wide range
#     of people
#   * more people (not just maintainers) should have access to a subset of bot
#     commands
#   * a generic label add|remove command will allow the community to fill in
#     where the bot can't
#   * different workflows should be a matter of enabling different plugins

import copy
import logging

from pprint import pprint
from ansibullbot.triagers.defaulttriager import DefaultTriager
from ansibullbot.wrappers.issuewrapper import IssueWrapper


class SimpleTriager(DefaultTriager):

    def run(self):

        # make a repo object for the github api
        repo = self.ghw.get_repo(self.repopath)

        # map for issue type to label
        label_map = repo.get_label_map()

        # collect issues
        if not self.args.number:
            issues = repo.get_issues()
        else:
            issue = repo.get_issue(int(self.args.number))
            issues = [issue]

        # iterate through issues and apply actions
        for issue in issues:

            logging.info('triaging %s' % issue.html_url)
            actions = copy.deepcopy(self.EMPTY_ACTIONS)

            # wrap the issue for extra magic
            iw = self.wrap_issue(self.ghw, repo, issue)

            # what did the submitter provide in the body?
            td = iw.template_data
            missing = iw.missing_template_sections
            if missing and 'needs_template' not in iw.labels:
                actions['newlabel'].append('needs_template')

            # what type of issue is this?
            if 'issue type' in td:
                mapped_label = label_map.get(td['issue type'])
                if mapped_label:
                    if mapped_label not in iw.labels:
                        actions['newlabel'].append(mapped_label)

            pprint(actions)
            self.apply_actions(iw, actions)
