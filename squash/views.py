from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404

from distutils.version import StrictVersion

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Permission

from datetime import date

import simplejson

from django.conf import settings

from squash.models import Project
from squash.models import Version
from squash.models import Issue

from squash.utils import get_ref, is_empty

# Log in
def login_user(request):
    state = None
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            # Access the profile to automatically create it if it doesn't exist
            user.profile
            if user.is_active:
                login(request, user)
                
                state = "You're successfully logged in!"
                
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('squash/login.html', {'state':state, 'username': username}, context_instance=RequestContext(request))

# Log out
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/squash/')

# The index
@permission_required('squash.can_browse')
def index(request):
    projects_list = Project.objects.all()
    return render_to_response('squash/index.html', {'projects_list' : projects_list}, context_instance=RequestContext(request))

# New issue page
@permission_required('squash.add_issue')
def new_issue(request, project_key=None):
    projects_list = Project.objects.all()
    if project_key:
        current_project = Project.objects.get(key=project_key)
    else:
        current_project = None
    return render_to_response('squash/create_issue.html', {'projects_list' : projects_list, 'current_project' : current_project}, context_instance=RequestContext(request))

# Create a new issue
@permission_required('squash.add_issue')
def new_issue_create(request):
    try:
        p = Project.objects.get(key=request.POST['project'])
    except Project.DoesNotExist:
        raise Http404('Unable to find project with key ' + request.POST['project'])
        
    try:
        version_string = request.POST['version']
        print 'Version string:', version_string
        if (is_empty(version_string) or version_string == 'Future'):
            v = None
        else:
            v = p.version_set.get(version_number=version_string)
    except Version.DoesNotExist:
        raise Http404
    
    i = Issue()
    i.project = p
    i.state = 'o'
    i.name = request.POST['issue_name']
    i.description = request.POST['issue_description']
    
    if v:
        v.issuesAsFix.add(i)
        v.save()
    
    i.save()
    
    return redirect('/squash/issue/' + p.key + '/' + str(i.issue_number))

# Create Project page
def new_project(request):
    return render_to_response('squash/create_project.html', context_instance=RequestContext(request))
    
# Create a new Project
def create_project(request):
    proj_key = request.POST['project_key']
    existing_project = Project.objects.filter(key = proj_key)
    if (len(existing_project) > 0):
        return render_to_response('squash/create_project.html', {'error_message' : 'A project with that key already exists'}, context_instance=RequestContext(request))
    
    proj_name = request.POST['project_name']
    
    if (is_empty(proj_key) or is_empty(proj_name)):
        return render_to_response('squash/create_project.html', {'error_message' : 'Key or Name empty, both must be provided'}, context_instance=RequestContext(request))
    
    proj = Project()
    proj.key = proj_key
    proj.name = proj_name
    proj.save()

    return redirect('/squash/project/' + proj.key)

# A list of all Projects
@permission_required('squash.can_browse')
def projects(request):
    projects = Project.objects.all()
    return render_to_response('squash/projects.html', {'projects_list' : projects}, context_instance=RequestContext(request))

# A specific project
@permission_required('squash.can_browse')
def project(request, project_key):
    try:
        project = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    return render_to_response('squash/project.html', {'project' : project}, context_instance=RequestContext(request))

# The issues for a project
@permission_required('squash.can_browse')
def project_version(request, project_key, version_num='Future'):
    try:
        project = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    if version_num == 'Future':
        version = None
    else:    
        try:
            version = project.version_set.get(version_number=version_num)
        except Version.DoesNotExist:
            raise Http404
    return render_to_response('squash/project_version.html', {'project' : project, 'version' : version}, context_instance=RequestContext(request))

# Save editing changes for an Issue
@permission_required('squash.change_issue')
def save_issue(request):
    project_key = request.POST['project_key']
    issue_num = request.POST['issue_number']
    version_number = request.POST['issue_version']
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    try:
        issue = Issue.objects.get(project=proj, issue_number=issue_num)
    except Issue.DoesNotExist:
        raise Http404
    
    version = None
    if version_number != 'Future':
        try:
            version = Version.objects.get(project=proj, version_number = version_number)
        except Issue.DoesNotExist:
            raise Http404
    
    issue_new_name = request.POST['issue_name']
    issue_new_description = request.POST['issue_description']
    issue.name = issue_new_name
    issue.fix_version = version
    issue.description = issue_new_description
    issue.save()
    
    return redirect('/squash/issue/' + proj.key + '/' + str(issue.issue_number));
    
# Begin to edit an Issue
@permission_required('squash.change_issue')
def edit_issue(request, project_key, issue_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
        
    try:
        issue = Issue.objects.get(project=proj, issue_number=issue_num)
    except Issue.DoesNotExist:
        raise Http404
        
    print 'Found issue', issue
    
    return render_to_response('squash/edit_issue.html', {'issue' : issue}, context_instance=RequestContext(request))

# A specific issue
@permission_required('squash.can_browse')
def issue(request, project_key, issue_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    try:
        issue = Issue.objects.get(project=proj, issue_number=issue_num)
    except Issue.DoesNotExist:
        raise Http404
    
    return render_to_response('squash/issue.html', {'project' : proj, 'version' : issue.fix_version, 'issue' : issue}, context_instance=RequestContext(request))
    
# Confirming the deletion of a Version
@permission_required('squash.delete_version')
def confirm_delete_version(request, project_key, version_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    try:
        version = Version.objects.get(version_number=version_num)
    except Version.DoesNotExist:
        raise Http404
    
    print 'Confirming delete'
    return render_to_response('squash/delete_version.html', {'project' : proj, 'version' : version}, context_instance=RequestContext(request))
    
# Delete a Version
@permission_required('squash.delete_version')
def delete_version(request, project_key, version_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    try:
        version = Version.objects.get(version_number=version_num)
    except Version.DoesNotExist:
        raise Http404

    referal = get_ref(request)
    if not referal:
        raise Http404
    if not "confirmDeleteVersion" in referal:
        raise Http404
    
    version.delete()
    
    return render_to_response('squash/delete_version.html', {'project' : proj, 'version' : version, 'success' : True}, context_instance=RequestContext(request))

# Release a Version
@permission_required('squash.change_version')
def release_version(request, project_key, version_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    try:
        version = Version.objects.get(version_number=version_num)
    except Version.DoesNotExist:
        raise Http404

    version.released = True
    version.release_date = date.today()
    version.save()
    
    return render_to_response('squash/delete_version.html', {'project' : proj, 'version' : version, 'success' : True}, context_instance=RequestContext(request))

# Return the page for a new version
@permission_required('squash.add_version')
def new_version(request, project_key):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    return render_to_response('squash/create_version.html', {'project' : proj}, context_instance=RequestContext(request))

# Actually create the version
@permission_required('squash.add_version')
def create_version(request, project_key):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    version_num = request.POST['version_number']
    
    try:
        StrictVersion().parse(version_num)
    except ValueError:
        return render_to_response('squash/create_version.html', {'project' : proj, 'error_message' : 'Invalid version number format.'}, context_instance=RequestContext(request))
    
    existing_issues = proj.version_set.filter(version_number = version_num)
    
    if (len(existing_issues) > 0):
        return render_to_response('squash/create_version.html', {'project' : proj, 'error_message' : 'A version with this version number already exists.'}, context_instance=RequestContext(request))
    
    v = Version()
    v.project = proj
    v.description = request.POST['version_description']
    v.version_number = version_num
    v.save()
    
    return redirect("/squash/project/" + proj.key + "/" + version_num)

# Confirming the deletion of a Project
@permission_required('squash.delete_project')
def confirm_delete_project(request, project_key):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    
    return render_to_response('squash/delete_project.html', {'project' : proj}, context_instance=RequestContext(request))
    
# Delete a Project
@permission_required('squash.delete_project')
def delete_project(request, project_key):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404

    referal = get_ref(request)
    if not referal:
        raise Http404
    if not "confirmDeleteProject" in referal:
        raise Http404
    
    proj.delete()
    
    return render_to_response('squash/delete_project.html', {'project' : proj, 'success' : True}, context_instance=RequestContext(request))

# Delete an Issue
@permission_required('squash.delete_issue')
def delete_issue(request, project_key, issue_num):
    try:
        proj = Project.objects.get(key=project_key)
    except Project.DoesNotExist:
        raise Http404
    try:
        issue = Issue.objects.get(project=proj, issue_number=issue_num)
        fix_version = issue.fix_version
        issue.delete()
    except Issue.DoesNotExist:
        raise Http404
    
    if fix_version:
        return redirect('/squash/project/' + proj.key + '/' + fix_version.version_number)
    return redirect('/squash/project/' + proj.key + '/Future')

# Start work on an Issue
@permission_required('squash.change_issue')
def start_issue(request, project_key, issue_num):
    proj = get_object_or_404(Project, key=project_key)
    
    issue = get_object_or_404(Issue, project=proj, issue_number=issue_num)
    issue.state = 'p'
    issue.save()
    
    return redirect('/squash/issue/' + proj.key + '/' + str(issue.issue_number))
    
# Stop work on an Issue
@permission_required('squash.change_issue')
def stop_issue(request, project_key, issue_num):
    proj = get_object_or_404(Project, key=project_key)
    
    issue = get_object_or_404(Issue, project=proj, issue_number=issue_num)
    issue.state = 'o'
    issue.save()
    
    return redirect('/squash/issue/' + proj.key + '/' + str(issue.issue_number))

# Mark Issue as Resolved
@permission_required('squash.change_issue')
def resolve_issue(request, project_key, issue_num):
    proj = get_object_or_404(Project, key=project_key)
    
    issue = get_object_or_404(Issue, project=proj, issue_number=issue_num)
    issue.state = 'r'
    issue.save()
    
    return redirect('/squash/project/' + proj.key + '/' + issue.fix_version.version_number)
    
# Mark Issue as Closed
@permission_required('squash.change_issue')
def close_issue(request, project_key, issue_num):
    proj = get_object_or_404(Project, key=project_key)
    
    issue = get_object_or_404(Issue, project=proj, issue_number=issue_num)
    issue.state = 'c'
    issue.save()
    
    return redirect('/squash/project/' + proj.key + '/' + issue.fix_version.version_number)

# Edit a User
@permission_required('squash.can_admin')
def edit_user(request, uname):
    user = get_object_or_404(User, username=uname)
    
    return render_to_response('squash/edit_user.html', {'user_to_edit' : user}, context_instance=RequestContext(request))

# Save a User's permission changes
@permission_required('squash.can_admin')    
def save_user_permissions(request, uname):
    user = get_object_or_404(User, username=uname)
    
    perm_dict = {'perm_add_issue' : 'add_issue',
                'perm_change_issue' : 'change_issue',
                'perm_delete_issue' : 'delete_issue',
                'perm_can_browse' : 'can_browse'}
    
    for key in perm_dict.keys():
        perm = get_object_or_404(Permission, codename=perm_dict[key])
        if key in request.POST:
            user.user_permissions.add(perm)
        else:
            user.user_permissions.remove(perm)
    
    user.save()
    
    request.session['success'] = True
    
    return redirect('/squash/user/' + uname)

# Get all Users
@permission_required('squash.can_admin', raise_exception=True)
def users(request):
    users = User.objects.all()
    
    users = sorted(users, key=lambda x: x.profile.created_at, reverse=True)
    return render_to_response('squash/users.html', {'users' : users}, context_instance=RequestContext(request))

########## START JSON GET METHODS ##########
@permission_required('squash.add_issue')
def get_project_versions(request, project_key):
    try:
        project = Project.objects.get(key=project_key)
        versions = project.sorted_version_numbers()
        res = HttpResponse(simplejson.dumps(versions, ensure_ascii=False), mimetype='application/json')
        return res
    except Project.DoesNotExist:
        raise Http404
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise