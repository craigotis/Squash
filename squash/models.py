from distutils.version import StrictVersion
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from squash.utils import *


## Django Profile Class ##
class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    created_at = models.DateTimeField(auto_now_add=True)

# definition of UserProfile from above

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

## Squash Models ##
class Project(models.Model):
    class Meta:
        permissions = (("can_browse", "Can browse Squash"), ("can_admin", "Can administer Squash"))

    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name

    def future_issues(self):
        future_issue_set = Issue.objects.filter(project = self, fix_version = None)
        return sorted(future_issue_set, cmp=issue_state_compare)

    def most_recent_version(self):
        unreleased_versions = [v for v in self.version_set.filter(released=False)]
        if (len(unreleased_versions) > 0):
            unreleased_versions.sort(key=lambda version: StrictVersion(version.version_number))
            return unreleased_versions[0]
        else:
            return None

    def sorted_versions(self):
        all_versions = [v for v in self.version_set.all()]
        all_versions.sort(key=lambda version: StrictVersion(version.version_number))
        all_versions.reverse()
        return all_versions

    def sorted_version_numbers(self):
        versions = [v.version_number for v in self.version_set.all()]
        versions.sort(key=StrictVersion)
        return versions
        
    def sorted_unreleased_version_numbers(self):
        versions = [v.version_number for v in self.version_set.filter(released=False)]
        versions.sort(key=StrictVersion)
        return versions
    
    def all_project_issues(self):
        return Issue.objects.filter(project = self)


class Version(models.Model):
    description = models.CharField(max_length=300)
    version_number = models.CharField(max_length=15)
    project = models.ForeignKey(Project)
    released = models.BooleanField(default=False)
    scheduled_release_date = models.DateField(null=True, blank=True, default=None)
    release_date = models.DateField(null=True, blank=True, default=None)
    
    def issues_sorted_by_state(self):
        return sorted(self.issuesAsFix.all(), cmp=issue_state_compare)
    
    def __str__(self):
        return self.version_number


ISSUE_STATE = (
    ('p', 'In Progress'),
    ('o', 'Open'),
    ('r', 'Resolved'),
    ('c', 'Closed'),
)


def is_valid_state(state):
    return len([i for i, v in enumerate(ISSUE_STATE) if v[0] == state]) == 1


def state_order(state):
    return [i for i, v in enumerate(ISSUE_STATE) if v[0] == state][0]


def issue_state_compare(x, y):
    x_order = state_order(x.state)
    y_order = state_order(y.state)
    if x_order == y_order:
        return 0
    elif x_order > y_order:
        return 1
    return -1


class Issue(models.Model):
    project = models.ForeignKey(Project)
    fix_version = models.ForeignKey(Version, related_name='issuesAsFix', null=True, blank=True, default=None)
    occurs_version = models.ForeignKey(Version, related_name='issuesAsOccurs', null=True, blank=True, default=None)
    issue_number = models.IntegerField(null=True)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=3000)
    state = models.CharField(max_length=1, choices=ISSUE_STATE)
    last_modified = models.DateTimeField(auto_now=True)
    
    def generate_issue_number(self):
        project_issues = self.project.all_project_issues()
        highest_so_far = 1
        for issue in project_issues:
            if self != issue and issue.issue_number and issue.issue_number >= highest_so_far:
                highest_so_far = issue.issue_number + 1
        self.issue_number = highest_so_far
    
    def save(self):
        if (is_valid_state(self.state) == False):
            print "Issue state not valid, setting to open"
            self.state = 'o'
        if (self.issue_number is None):
            self.generate_issue_number()
        super(Issue, self).save()
    
    def state_short_str(self):
        return self.state
    
    def state_str(self):
        state_lookup = [v[1] for i, v in enumerate(ISSUE_STATE) if v[0] == self.state];
        if (len(state_lookup) > 0):
            return state_lookup[0]
        return "(Invalid state: " + self.state + "))"

    def version_str(self):
        return str(self.fix_version.version_number)
    
    def __str__(self):
        return ('(No name) ' if is_empty(self.name) else self.name) + ' ' + self.state
