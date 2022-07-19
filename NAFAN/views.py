import json

from datetime import date
from multiprocessing.pool import ApplyResult

from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect

from .models import NAFANLoginForm, NAFANLog, NAFANAudit, NAFANUser, NAFANUserForm, NAFANContactForm, NAFANJoinUsForm
from .models import Repository, RepositoryForm, User_Repositories, UploadFileForm, RepositoryApplicationForm, save_uploaded_file
from .models import FindingAid, FindingAidSubjectHeader, DacsAidForm, MinimalAidForm, EADAidForm, MARCAidForm, PDFAidForm, HarvestFilesForm, NAFANJoinUs
from .models import Chronology, ControlAccess, AidProfile, AidProfileForm, HarvestProfile, HarvestProfileForm, FindingAidAudit

import lxml.etree as ET


def home(request):

    # FindingAid.ASpace()
    
    search_term = request.GET.get('searchTerm', '')

    if search_term:
    # send_mail(
    #         'BASE_DIR',
    #         os.path.join(x, 'static'),
    #         'aaf8qn@virginia.edu',
    #         ['aaf8qn@virginia.edu'],  # This needs to be added to constants or application settings
    #         fail_silently=False,
    #     )

        request.session['search_term'] = search_term

        response = FindingAid.Search(search_term)

        return render(request, 'NAFAN/index.html', {"search_term":search_term, "response":response})
    else:
        return render(request, "NAFAN/index.html")

def search_results(request):
    
    search_term = request.session['search_term']

    if search_term:
        response = FindingAid.Search(search_term)

        return render(request, 'NAFAN/index.html', {"search_term":search_term, "response":response})
    else:
        return render(request, "NAFAN/index.html")

def NAFANLogin(request):

    login_message = ""
    if request.method == 'POST':

        form = NAFANLoginForm(request.POST)
        if form.is_valid():

            # May or may not want to save this information to the database
            # application.save()

            user = NAFANUser.GetUser(form.cleaned_data['email'])
            if not user:
                login_message = "Your credentials were not found"
            else:
                request.session['current_login'] = user.email

                if user.user_type == "nafan_admin":
                    return redirect("nafan_admin")
                else:
                    if user.user_type == "contributor_admin":
                        return redirect("contributor_admin")
                    else:                   
                        if user.user_type == "contributor":
                            return redirect("contributor")
                        else:
                            return redirect("researcher")

    else:
        form = NAFANLoginForm()

    return render(request, 'NAFAN/NAFANLogin.html', {'form': form, 'login_message': login_message})

def joinus(request):

    list(messages.get_messages(request))

    if request.method == 'POST':

        form = NAFANJoinUsForm(request.POST)
        
        if form.is_valid():

            form.save()

            messages.success(request, 'Your message has been sent to the NAFAN staff.')

            # This blanks out the fields on the form
            form = NAFANJoinUsForm()

    else:

        form = NAFANJoinUsForm()
        
    return render(request, 'NAFAN/joinus.html', {'form': form})

def help(request, topic):

    context = {}
    context["title"] = topic

    if topic == "Finding Aid Title":
        context["contents"] = "The title identifies the finding aid.  It should be unique within your repository"
    else:
        context["contents"] = "This topic needs description."

    return render(request, "NAFAN//help.html", context)

def clear_join(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(NAFANJoinUs, id = id)
 
    # delete object
    obj.delete()

    context["action_items"] = NAFANJoinUs.GetActionItems()

    return render(request, "Admin/nafan_admin.html", context)

def forgot_password(request):
        
    return render(request, 'NAFAN/forgot_password.html')

def newToNAFAN(request):
        
    dom = ET.parse("uploads/ms0106.xml")
    xslt = ET.parse("uploads/eadcbs9,xsl")
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    print(ET.tostring(newdom, pretty_print=True))

def organizations(request):

    searchField = request.GET.get('search_field', '')
    searchTerm = request.GET.get('search_term', '')

    repositories = Repository.GetOrganizations(searchField, searchTerm)
    return render(request,'NAFAN/organizations.html',{"repositories":repositories})

def contact(request):

    list(messages.get_messages(request))

    if request.method == 'POST':

        form = NAFANContactForm(request.POST)
        
        if form.is_valid():

            # May or may not want to save this information to the database
            # form.save()

            message = 'From ' + form.cleaned_data['full_name'] + "\r\n"
            message = message + 'Message ' + form.cleaned_data['message'] + "\r\n"
            
            # send_mail does not work locally
            # send_mail(
            #     'NAFAN Repository Application' + form.cleaned_data['subject'],
            #     message,
            #     form.cleaned_data['email'],
            #     ['aaf8qn@virginia.edu'],  # This needs to be added to constants or application settings
            #     fail_silently=False,
            # )

            messages.success(request, 'Your message has been sent to the NAFAN staff.')

            # This blanks out the fields on the form
            form = NAFANContactForm()

    else:

        form = NAFANContactForm()
        
    return render(request, 'NAFAN/contact.html', {'form': form})

def spotlights(request):

    return render(request, 'NAFAN/spotlights.html')

def Repository_Info(request, repository_name):
        
    repository = Repository.GetRepositoryByName(repository_name)

    return render(request, 'NAFAN/Repository_Info.html', {"repository":repository})

def Aid_Details(request, id):
        
    aid = get_object_or_404(FindingAid, id = id)

    return render(request, 'NAFAN/Aid_Details.html', {'aid': aid})

def Browse_Repository(request, id):
        
    context ={}

    aid = get_object_or_404(FindingAid, id = id)
    
    context['repository_name'] = aid.repository
   
    context["dataset"] = FindingAid.GetFindingAidsByRepository(aid.repository)

    return render(request, 'NAFAN/Browse_Repository.html', context)

def Browse_Repository_Entries(request, id):
        
    context ={}

    repository = get_object_or_404(Repository, id = id)
    
    context['repository_name'] = repository.repository_name
   
    context["dataset"] = FindingAid.GetFindingAidsByRepository(repository.repository_name)

    return render(request, 'NAFAN/Browse_Repository.html', context)

def view_aid_public(request, id):
        
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    repo = Repository.GetRepositoryByName(aid.repository)
    # case statement for display of aid based on type
 
    # add form dictionary to context
    context["aid"] = aid

    # contents = []
    # contents = FindingAid.GetFindingAidContents(id, contents)
    context["contents"] = FindingAid.objects.filter(progenitorID=id).order_by('pk')
    context["chron"] = Chronology.objects.filter(finding_aid_id=id).order_by('sort_order')
    context["series"] = FindingAid.objects.filter(progenitorID=id,level="c01").order_by('pk')
    # series = FindingAid.objects.filter(progenitorID=id,level="c01").order_by('pk')
    # for ser in series:
    #     print(ser.title)
    context["names"] = ControlAccess.objects.filter(finding_aid_id=id,control_type="persname").order_by('term')
    context["subjects"] = ControlAccess.objects.filter(finding_aid_id=id,control_type="subject").order_by('term')
    context["materials"] = ControlAccess.objects.filter(finding_aid_id=id,control_type="genreform").order_by('term')

    return render(request, "NAFAN/view_aid_public.html", context)

def contributor_admin(request):
    return render(request, "Admin/contributor_admin.html")

def nafan_admin(request):
    context ={}
       
    context["action_items"] = NAFANJoinUs.GetActionItems()

    return render(request, "Admin/nafan_admin.html", context)

def contributor(request):

    user_email = request.session['current_login']

    repositories = User_Repositories.GetRepositories(user_email)

    repository = Repository.GetRepositoryByName(repositories.first().repository_name)

    return HttpResponseRedirect("/FindingAids/finding_aids/" + str(repository.id))

def researcher(request):
    return render(request, "NAFAN/researcher.html")

def NAFANlogout(request):
    logout(request)
    return render(request, "NAFAN/index.html")

def tracelog(request):

    search_term = request.GET.get('searchTerm', '')

    if search_term:
        log = NAFANLog.GetLog(request.POST.get('searchTerm'))
    else:
        log = NAFANLog.GetLog("")

    return render(request, 'Admin/tracelog.html', {'log_contents': log})

def audit(request):

    return render(request, 'Admin/audit.html')

def NAFANActions(request):

    return render(request, 'Admin/NAFANActions.html')

# Users

def users(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    searchField = request.GET.get('search_field', '')
    searchTerm = request.GET.get('search_term', '')
    statusFilter = request.GET.get('status_filter', '')

    email = request.session['current_login']
    user = NAFANUser.GetUser(email)

    if user.user_type == "nafan_admin":        
        user_list = NAFANUser.GetUsers(searchField, searchTerm, statusFilter)
    else:
        user_list = NAFANUser.GetUsersByContributor(email, searchField, searchTerm, statusFilter)
   
    # add the dictionary during initialization
    # context["dataset"] = NAFANUser.objects.all().order_by("email")
    context["dataset"] = user_list
         
    return render(request, "Users/users.html", context)

def create_user(request):
    # dictionary for initial data with
    # field names as keys
    context ={}

    # add the dictionary during initialization
    form = NAFANUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        repositories = Repository.GetUserRepositories(request.session['current_login'])
        for repo in repositories:
            User_Repositories.AssignRepository(user.email, repo)

        NAFANAudit.AddAudit(user.pk, NAFANAudit.USER_TARGET, NAFANAudit.CREATE_ACTION, request.session['current_login'], form.cleaned_data['notes'])
        return HttpResponseRedirect("/Users/users")
         
    context['form']= form

    return render(request, "Users/create_user.html", context)

def delete_user(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(NAFANUser, id = id)
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # list view
        return HttpResponseRedirect("/Users/users")
 
    context["user_name"] = obj.full_name
    return render(request, "Users/delete_user.html", context)

def update_user(request, id):
        # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(NAFANUser, id = id)
 
    # pass the object as instance in form
    form = NAFANUserForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        NAFANAudit.AddAudit(id, NAFANAudit.USER_TARGET, NAFANAudit.UPDATE_ACTION, request.session['current_login'], form.cleaned_data['notes'])
        return HttpResponseRedirect("/Users/users")
 
    # add form dictionary to context
    context["form"] = form
    context["audit"] = NAFANAudit.GetAudit(id, NAFANAudit.USER_TARGET)
 
    return render(request, "Users/update_user.html", context)


# Repositories

def repositories(request):

    search = True
    if request.GET.get("reset"):
        search = False
        searchTerm = ""
        searchField = ""
        status = "All"
    else:
        searchTerm = request.GET.get('search_term', '')
        searchField = request.GET.get('search_field', '')
        status = request.GET.get('status_filter', '')

    if not searchTerm and search:
        if 'repository_search_field' in request.session:
            searchField = request.session['repository_search_field']

            if not request.session.get('repository_search_term', None):
                request.session['repository_search_term'] = ""
            searchTerm = request.session['repository_search_term']

            if not request.session.get('repository_search_status', None):
                request.session['repository_search_status'] = ""

            status = request.session['repository_search_status']
    else:
        request.session['repository_search_field'] = searchField
        request.session['repository_search_term'] = searchTerm
        request.session['repository_search_status'] = status

    email = request.session['current_login']
    user = NAFANUser.GetUser(email)

    if user.user_type == "nafan_admin":
        repositories = Repository.GetRepositories(searchField, searchTerm, status)
        return render(request,'Repositories/repositories.html',{"repositories":repositories, "user_type":user.user_type})
    else:
        repositories = Repository.GetUserRepositories(request.session['current_login'])
        return render(request,'Repositories/repositories.html',{"repositories":repositories, "user_type":user.user_type})

def create_repository(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    form = RepositoryForm(request.POST or None)
    if form.is_valid():
        form.save()

        repository = Repository.GetRepositoryByID(form.instance.id)

        elasticsearch_id = FindingAid.CreateIndex(form.instance.id, "repository", repository.repository_name, repository.repository_name, repository.description, "")

        if elasticsearch_id != "Fail":
            Repository.objects.filter(pk=form.instance.id).update(elasticsearch_id=elasticsearch_id)

        return HttpResponseRedirect("/Repositories/repositories")
         
    context['form']= form

    return render(request, "Repositories/create_repository.html", context)

def update_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id.  This is a pointer to the object and changes on form.save, so anything not
    # displayed on the form is lost.
    obj = get_object_or_404(Repository, id = id)
    esID = obj.elasticsearch_id
 
    # pass the object as instance in form
    form = RepositoryForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():

        repository = form.save(commit=False)

        if esID:
            FindingAid.UpdateIndex(form.instance.id, esID, "repository", repository.repository_name, repository.repository_name, repository.description, "")
        else:
            esID = FindingAid.CreateIndex(form.instance.id, "repository", repository.repository_name, repository.repository_name, repository.description, "")
        
        repository.elasticsearch_id = esID
        repository.save()

        return HttpResponseRedirect("/Repositories/repositories")
 
    # add form dictionary to context
    context["form"] = form

    email = request.session['current_login']
    user = NAFANUser.GetUser(email)
    context["user_type"] = user.user_type

    return render(request, "Repositories/update_repository.html", context)

def delete_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Repository, id = id)

    FindingAid.RemoveIndex(obj.elasticsearch_id)
 
    # delete object
    obj.delete()

    return HttpResponseRedirect("/Repositories/repositories")

def report_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    obj = get_object_or_404(Repository, id = id)
    # context["repository_id"] = request.session['active_repository']
    context["repository_name"] = obj.repository_name
 
    return render(request, "Repositories/report_repository.html", context)

def invite_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    obj = get_object_or_404(Repository, id = id)
    # context["repository_id"] = request.session['active_repository']
    context["repository_name"] = obj.repository_name
    context["contact"] = obj.email
    context["subject"] = "Join us in NAFAN"

    return render(request, "Repositories/invite_repository.html", context)

def get_repository_search(request):

    return JsonResponse({'SearchField': request.session['repository_search_field'], 'SearchTerm': request.session['repository_search_term'], 'Status': request.session['repository_search_status']})

def get_organization_search(request):

    return JsonResponse({'SearchField': request.session['repository_search_field'], 'SearchTerm': request.session['repository_search_term']})

def export_repositories(request):

    Repository.ExportRepositories()
    
    return JsonResponse({'SearchField': request.session['repository_search_field'], 'SearchTerm': request.session['repository_search_term'], 'Status': request.session['repository_search_status']})


# User Repositories

def user_repositories(request, id):

    searchField = request.GET.get('search_field', '')
    searchTerm = request.GET.get('search_term', '')

    email = request.session['current_login']
    log_user = NAFANUser.GetUser(email)

    repositories = []

    if searchTerm:
        if log_user.user_type == "nafan_admin":
            repositories = User_Repositories.GetRepositoriesSearch(searchField, searchTerm)
            user_repositories = []
        else:
            repositories = User_Repositories.GetRepositories(email)

    user = get_object_or_404(NAFANUser, id = id)
    # if user.user_type != "nafan_admin":
    user_repositories = User_Repositories.GetRepositories(user.email)

    return render(request,'Users/user_repositories.html',
        {"repositories":repositories, 'user_repositories': user_repositories, 'username': user.email})

def upload_repositories(request):

    if request.method == 'POST':
        # form = UploadFileForm(request.POST, request.FILES)
        # if form.is_valid():
        fileName = save_uploaded_file(request.FILES['file'])
        response = Repository.handle_RepoData_upload(fileName)
        return HttpResponse(response)
    else:
        form = UploadFileForm()

    return render(request, 'Repositories/upload_repositories.html', {'form': form})

def add_user_repository(request):
    username = request.GET.get('username', None)
    repository = request.GET.get('repository', None)

    User_Repositories.AssignRepository(username, repository)
    # NAFANAudit.AddAudit(username, NAFANAudit.USER_TARGET, NAFANAudit.ADD_REPOSITORY_ACTION, request.session['current_login'], repository)

    from django.http import JsonResponse
    return JsonResponse({'result':'true'})

def remove_user_repository(request):
    username = request.GET.get('username', None)
    repository = request.GET.get('repository', None)

    User_Repositories.RemoveRepository(username, repository)
    # NAFANAudit.AddAudit(username, NAFANAudit.USER_TARGET, NAFANAudit.REMOVE_REPOSITORY_ACTION, request.session['current_login'], repository)

    from django.http import JsonResponse
    return JsonResponse({'result':'true'})


# Finding Aids

def finding_aids(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    request.session['active_repository'] = id

    # add the dictionary during initialization
    repository = Repository.GetRepositoryByID(id)
    context["dataset"] = FindingAid.GetFindingAidsByRepository(repository.repository_name)

    x = User_Repositories.GetRepositories(request.session['current_login'])
    for e in x:
        print(e.repository_name)

    context["repositories"] = User_Repositories.GetRepositories(request.session['current_login'])
        
    email = request.session['current_login']
    user = NAFANUser.GetUser(email)
    context['user_type'] = user.user_type

    context['repository_name'] = repository.repository_name

    return render(request, "FindingAids/finding_aids.html", context)

def aid_profile(request):
    context ={}
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    context['repository_name']= repository.repository_name

    if AidProfile.Exists(request.session['active_repository']):
        profile = AidProfile.GetAidProfileByID(request.session['active_repository'])
        form = AidProfileForm(request.POST or None, instance = profile)
    else:
        initial_dict = {
            "repository_id" : repository.pk,
        }
        form = AidProfileForm(request.POST or None, initial = initial_dict)

    if request.method == 'POST':
        if form.is_valid():
            aid = form.save(commit=False)
            aid.repository_id = request.session['active_repository']
            aid.save()

            return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))

    context['form']= form
    context['repository_id']= request.session['active_repository']

    return render(request, "FindingAids/aid_profile.html", context)

def new_aid(request):

    dacs = '2'
    ead = '3'
    MARC = '4'
    PDF = '5'
    SCHEMA = '6'

    id = request.session['create_aid_format']

    if id == dacs:
        return redirect("create_dacs")
    if id == ead:
        return redirect("ingest_ead")
    if id == MARC:
        return redirect("ingest_marc")
    if id == PDF:
        return redirect("ingest_pdf")
    if id == SCHEMA:
        return redirect("ingest_schema")

def delete_aid(request, id):
 
    # fetch the object related to passed id
    obj = get_object_or_404(FindingAid, id = id)
 
    FindingAid.RemoveIndex(obj.elasticsearch_id)

    # Remove any components
    FindingAid.objects.filter(progenitorID=id).delete()

    # delete object
    obj.delete()

    return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
def create_dacs(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    aid_format = AidProfile.GetAidProfileByID(repository.pk)
    initial_dict = {
        "name_and_location" : repository.repository_name,
        "governing_access" : aid_format.governing_access,
        "rights" : aid_format.rights,
        "creative_commons" : aid_format.creative_commons,
        "repository" : repository.repository_name,
        }
    context['repository_name']= repository.repository_name

    # add the dictionary during initialization
    form = DacsAidForm(request.POST or None, initial = initial_dict)
    if form.is_valid():
        aid = form.save(commit=False)
        aid.aid_type = "dacs"
        aid.repository = context['repository_name']
        
        notes = aid.revision_notes
        aid.revision_notes = ""

        user = NAFANUser.GetUser(request.session['current_login'])
        aid.updated_by = user.full_name

        today = date.today()
        aid.last_update = today.strftime("%B %d, %Y")

        aid.save()

        elasticsearch_id = FindingAid.CreateIndex(form.instance.id, "dacs", aid.title, aid.repository, aid.scope_and_content, "")

        if elasticsearch_id != "Fail":
            FindingAid.objects.filter(pk=form.instance.id).update(elasticsearch_id=elasticsearch_id)

        FindingAidAudit.AddAudit(form.instance.id, notes, user.full_name, today)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
         
    context['form']= form
    context['repository_id']= request.session['active_repository']

    return render(request, "FindingAids/create_dacs.html", context)

def ingest_ead(request):

    repository = Repository.GetRepositoryByID(request.session['active_repository'])

    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            
            for f in request.FILES.getlist('file'):

                #fileName = save_uploaded_file(request.FILES['file'])

                fileName = save_uploaded_file(f)

                user = NAFANUser.GetUser(request.session['current_login'])

                FindingAid.EADIndex("new", repository.repository_name, fileName, user.full_name)
            
            return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))

    form = UploadFileForm()

    return render(request, 'FindingAids/ingest_ead.html', {'form': form, "repository_name":repository.repository_name, "repository_id": request.session['active_repository']})

def ingest_marc(request):
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    
    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fileName = save_uploaded_file(request.FILES['file'])

            FindingAid.MARCIndex("new", repository.repository_name, fileName)
            
            return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))

    form = UploadFileForm()

    return render(request, 'FindingAids/ingest_marc.html', {'form': form, "repository_name":repository.repository_name, "repository_id": request.session['active_repository']})

def ingest_pdf(request):
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])

    if request.method == 'POST':

        form = PDFAidForm(request.POST, request.FILES)
        if form.is_valid():

            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            fileName = save_uploaded_file(request.FILES['file'])

            FindingAid.PDFIndex("new", title, description, repository.repository_name, fileName)
            
            return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))

    form = PDFAidForm()

    return render(request, 'FindingAids/ingest_pdf.html', {'form': form, "repository_name":repository.repository_name, "repository_id": request.session['active_repository']})

def ingest_schema(request):

    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    
    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fileName = save_uploaded_file(request.FILES['file'])

            response = FindingAid.Schema_jsonLD_Index(repository.repository_name, fileName)
            
            return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))

    form = UploadFileForm()

    return render(request, 'FindingAids/ingest_schema.html', {'form': form, "repository_name":repository.repository_name, "repository_id": request.session['active_repository']})

def edit_dacs(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(FindingAid, id = id)
    esID = obj.elasticsearch_id
    repository = obj.repository
 
    # pass the object as instance in form
    form = DacsAidForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():

        aid = form.save(commit=False)
        aid.aid_type = "dacs"
        aid.repository = repository
        aid.elasticsearch_id = esID

        notes = aid.revision_notes
        aid.revision_notes = ""

        user = NAFANUser.GetUser(request.session['current_login'])
        aid.updated_by = user.full_name

        today = date.today()
        aid.last_update = today.strftime("%B %d, %Y")

        aid.save()

        FindingAid.UpdateIndex(form.instance.id, esID, "dacs", aid.title, aid.repository, aid.scope_and_content, "")
        FindingAidAudit.AddAudit(form.instance.id, notes, user.full_name, today)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    context["form"] = form
    context["repository_id"] = request.session['active_repository']
    context["repository_name"] = obj.repository
    context["finding_aid_id"] = id
    context["subject_headers"] = FindingAidSubjectHeader.GetSubjectHeaders(id)
    context["audit"] = FindingAidAudit.GetAudit(id)

    return render(request, "FindingAids/edit_dacs.html", context)

def edit_ead(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    # pass the object as instance in form
    form = EADAidForm(request.POST or None, instance = aid)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():

        fileName = save_uploaded_file(request.FILES['file'])

        FindingAid.EADIndex(aid.id, aid.repository, fileName)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    # context["form"] = form
    # context["repository_id"] = request.session['active_repository']
    # context["repository_name"] = aid.repository
    # context["repository_name"] = aid.repository

    # return render(request, "FindingAids/edit_ead.html", context)

    form = UploadFileForm()

    return render(request, 'FindingAids/edit_ead.html', {'form': form, "aid": aid, "repository_id": request.session['active_repository']})

def update_aid(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    request.session['active_finding_aid'] = id

    # case statement for display of aid based on type
    if aid.aid_type == "minimal":
        return HttpResponseRedirect("/FindingAids/edit_dacs/" + str(id))
    #     return HttpResponseRedirect("/FindingAids/edit_minimal/" + str(id))

    if aid.aid_type == "dacs":
        return HttpResponseRedirect("/FindingAids/edit_dacs/" + str(id))

    if aid.aid_type == "ead":
        return HttpResponseRedirect("/FindingAids/edit_ead/" + str(id))

    if aid.aid_type == "marc":
        return HttpResponseRedirect("/FindingAids/edit_marc/" + str(id))


    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(FindingAid, id = id)
    esID = obj.elasticsearch_id
    repository = obj.repository

    # pass the object as instance in form
    form = MinimalAidForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        aid = form.save(commit=False)
        aid.aid_type = "minimal"
        aid.repository = repository
        aid.elasticsearch_id = esID
        aid.save()

        FindingAid.UpdateIndex(form.instance.id, esID, "minimal", aid.title, aid.repository, aid.scope_and_content, "")

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    context["form"] = form
    context["repository_id"] = request.session['active_repository']
    context["repository_name"] = obj.repository
 
    return render(request, "FindingAids/edit_minimal.html", context)

def edit_marc(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    # pass the object as instance in form
    form = MARCAidForm(request.POST or None, instance = aid)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():

        fileName = save_uploaded_file(request.FILES['file'])

        FindingAid.MARCIndex(aid.id, aid.repository, fileName)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    context["form"] = form
    context["repository_id"] = request.session['active_repository']
    context["repository_name"] = aid.repository

    # return render(request, "FindingAids/edit_ead.html", context)

    form = UploadFileForm()

    return render(request, 'FindingAids/edit_ead.html', {'form': form, "aid": aid, "repository_id": request.session['active_repository']})

def edit_pdf(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    # pass the object as instance in form
    form = PDFAidForm(request.POST or None, instance = aid)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():

        fileName = save_uploaded_file(request.FILES['file'])

        FindingAid.PDFIndex(aid.id, aid.repository, fileName)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    context["form"] = form
    context["repository_id"] = request.session['active_repository']
    context["repository_name"] = aid.repository

    form = UploadFileForm()

    return render(request, 'FindingAids/edit_pdf.html', {'form': form, "aid": aid, "repository_id": request.session['active_repository']})

def view_aid(request, id):

    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    # case statement for display of aid based on type
 
    # add form dictionary to context
    context["aid"] = aid
    context["repository_id"] = request.session['active_repository']
 
    return render(request, "FindingAids/view_aid.html", context)

def set_finding_aid_format(request):

    request.session['create_aid_format'] = request.GET.get('format', None)

    from django.http import JsonResponse
    return JsonResponse({'result':'true'})

def add_subject_header(request):
    subject_header = request.GET.get('subject_header', None)
    aid_id = request.GET.get('aid_id', None)

    FindingAidSubjectHeader.AddSubjectHeader(aid_id, subject_header)

    from django.http import JsonResponse
    return JsonResponse({'result':'true'})

def delete_subject_header(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(FindingAidSubjectHeader, id = id)
 
    # delete object
    obj.delete()

    # after deleting redirect to
    return HttpResponseRedirect("/FindingAids/edit_dacs/" + str(request.session['active_finding_aid']))


# Harvest

def harvest_aids(request):
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    
    harvest_profile_id = request.session['active_harvest']
    harvest_profile = get_object_or_404(HarvestProfile, id = harvest_profile_id)

        # FILE_TYPES = [('EAD', 'EAD'), ('MARC', 'MARC'), ('PDF', 'PDF'), ('Schema', 'Schema.org'), ('Other', 'Other')]
        # HARVEST_TYPES = [('Directory', 'Directory'), ('Sitemap', 'Sitemap'), ('OAI', 'OAI-PMH'), ('Other', 'Other')]

        # https://eadiva.com/sampleEAD
        # if format == "ead":
        #     FindingAid.HarvestEAD(directory, repository.repository_name)

    user = NAFANUser.GetUser(request.session['current_login'])

    if harvest_profile.harvest_type == "File":
        FindingAid.HarvestEADFile(harvest_profile.harvest_location, repository.repository_name, user.full_name)

    if harvest_profile.harvest_type == "Directory":
        FindingAid.HarvestEAD(harvest_profile.harvest_location, repository.repository_name)

    if harvest_profile.harvest_type == "OAI":
        FindingAid.HarvestOAI(harvest_profile.harvest_location, repository.repository_name)

    if harvest_profile.harvest_type == "Sitemap":
        FindingAid.HarvestSitemap(harvest_profile.harvest_location, repository.repository_name)

    return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
         
def harvest_profiles(request):
    context ={}
 
    context['profiles']= HarvestProfile.GetHarvestProfiles(request.session['active_repository'])
    context['repository_id'] = request.session['active_repository']

    return render(request, "FindingAids/harvest_profiles.html", context)

def create_harvest_profile(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    initial_dict = {
        "repository_id" : repository.pk,
    }
    context['repository_name']= repository.repository_name

    # add the dictionary during initialization
    form = HarvestProfileForm(request.POST or None, initial = initial_dict)
    if form.is_valid():
        harvest = form.save(commit=False)
        harvest.repository_id = request.session['active_repository']
        harvest.save()

        return HttpResponseRedirect("/FindingAids/harvest_profiles")
         
    context['form']= form
    context['repository_id']= request.session['active_repository']
    context['repository_name']= repository.repository_name

    return render(request, "FindingAids/create_harvest_profile.html", context)

def edit_harvest_profile(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    request.session['active_harvest'] = id

    # fetch the object related to passed id
    obj = get_object_or_404(HarvestProfile, id = id)
    repository = Repository.GetRepositoryByID(obj.repository_id)

     # pass the object as instance in form
    form = HarvestProfileForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        harvest = form.save(commit=False)
        harvest.repository_id = repository.pk
        harvest.save()

        return HttpResponseRedirect("/FindingAids/harvest_profiles")

    context['form']= form
    context['repository_id']= request.session['active_repository']
    context['repository_name']= repository.repository_name

    return render(request, "FindingAids/edit_harvest_profile.html", context)

def delete_harvest_profile(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(HarvestProfile, id = id)
 
    # delete object
    obj.delete()
    
    # after deleting redirect to
    # list view
    return HttpResponseRedirect("/FindingAids/harvest_profiles")
