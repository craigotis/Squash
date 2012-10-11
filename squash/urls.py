from django.conf.urls import patterns, include, url

urlpatterns = patterns('squash.views',

    # Auth
    
    (r'^login/$', 'login_user'),
    (r'^logout/$', 'logout_user'),

    # Application URLs

    url(r'^$', 'index'),
    
    url(r'^newIssue/create/$', 'new_issue_create'),
    url(r'^newIssue/(?P<project_key>\w+)/$', 'new_issue'),
    url(r'^newIssue/$', 'new_issue'),
    
    url(r'^issue/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'issue'),
    
    url(r'^start/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'start_issue'),
    url(r'^stop/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'stop_issue'),
    url(r'^resolve/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'resolve_issue'),
    url(r'^close/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'close_issue'),
    url(r'^deleteIssue/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'delete_issue'),
    url(r'^editIssue/save/$', 'save_issue'),
    url(r'^editIssue/(?P<project_key>\w+)/(?P<issue_num>\d+)/$', 'edit_issue'),
    
    # AJAX URLs
    url(r'^get_project_versions/(?P<project_key>\w+)/$', 'get_project_versions'),
    url(r'^get_unreleased_project_versions/(?P<project_key>\w+)/$', 'get_unreleased_project_versions'),
    # End AJAX URLs
    
    url(r'^newVersion/(?P<project_key>\w+)/create/$', 'create_version'),
    url(r'^newVersion/(?P<project_key>\w+)/$', 'new_version'),
    
    url(r'^confirmDeleteVersion/(?P<project_key>\w+)/(?P<version_num>((\d+).)+(\d+))/$', 'confirm_delete_version'),
    url(r'^deleteVersion/(?P<project_key>\w+)/(?P<version_num>((\d+).)+(\d+))/$', 'delete_version'),
    url(r'^releaseVersion/(?P<project_key>\w+)/(?P<version_num>((\d+).)+(\d+))/$', 'release_version'),
    
    url(r'^projects/$', 'projects'),
    
    url(r'^project/(?P<project_key>\w+)/$', 'project'),
    url(r'^project/(?P<project_key>\w+)/Future/$', 'project_version'),
    url(r'^project/(?P<project_key>\w+)/(?P<version_num>((\d+).)+(\d+))/$', 'project_version'),
    
    url(r'^newProject/create/$', 'create_project'),
    url(r'^newProject/$', 'new_project'),
    
    url(r'^confirmDeleteProject/(?P<project_key>\w+)/$', 'confirm_delete_project'),
    url(r'^deleteProject/(?P<project_key>\w+)/$', 'delete_project'),
    
    # Profile URLs
    
    url(r'^user/(?P<uname>\w+)/$', 'edit_user'),
    
    # Administrative URLs
    
    url(r'^users/$', 'users'),
    
    url(r'^saveUserPerms/(?P<uname>\w+)/$', 'save_user_permissions'),
)
