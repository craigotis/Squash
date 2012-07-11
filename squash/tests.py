"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

import sys

from squash.models import *

class SimpleTest(TestCase):

    def test_is_valid_state(self):
        self.assertTrue(is_valid_state('p'))
        self.assertFalse(is_valid_state('x'))

    def test_issue_state_order(self):
        self.assertEqual(state_order('p'), 0)

    def test_issue_throws_if_bad_state(self):
        p = Project()
        p.save()
    
        v = Version()
        v.version_number = '1.0.0'
        v.project = p
        v.save()
    
        i = Issue()
        i.project = p;
        i.fix_version = v
        i.state = 'x'
        
        i.save()
        
        self.assertEqual(i.state_short_str(), 'o')

    def test_issue_state_short_str(self):
        i = Issue()
        i.state = 'o'
        
        self.assertEqual(i.state_short_str(), 'o')


    def test_issue_state_str(self):
        i = Issue()
        i.state = 'o'
        
        self.assertEqual(i.state_str(), 'Open')


    def test_issue_state_sorting(self):
        p = Project()
        p.save()
    
        v = Version()
        v.version_number = '1.0.0'
        v.project = p
        v.save()
        
        num_issues = 12
        
        for c in range(num_issues):
            i = Issue()
            i.state = ISSUE_STATE[c % 4][0]
            i.project = p
            i.fix_version = v
            i.save()
        
        self.assertEqual(v.issuesAsFix.count(), num_issues)
        
        sorted_issues = v.issues_sorted_by_state()
        
        self.assertTrue(len(sorted_issues), num_issues)
        self.assertEqual(sorted_issues[0].state[0], 'p')
        self.assertEqual(sorted_issues[1].state[0], 'p')
        self.assertEqual(sorted_issues[2].state[0], 'p')
        self.assertEqual(sorted_issues[3].state[0], 'o')
        self.assertEqual(sorted_issues[4].state[0], 'o')
        self.assertEqual(sorted_issues[5].state[0], 'o')