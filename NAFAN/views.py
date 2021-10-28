import json

from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse

from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect

from .models import NAFANLoginForm, NAFANLog, NAFANUser, NAFANUserForm
from .models import Repository, RepositoryForm, User_Repositories, UploadFileForm, RepositoryApplicationForm, save_uploaded_file
from .models import FindingAid, FindingAidForm

def home(request):

    search_term = request.GET.get('searchTerm', '')

    if search_term:
    # send_mail(
    #         'BASE_DIR',
    #         os.path.join(x, 'static'),
    #         'aaf8qn@virginia.edu',
    #         ['aaf8qn@virginia.edu'],  # This needs to be added to constants or application settings
    #         fail_silently=False,
    #     )

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

def newToNAFAN(request):

    list(messages.get_messages(request))

    # This handles users requesting entry into the NAFAN repository family
    if request.method == 'POST':

        form = RepositoryApplicationForm(request.POST)
        
        if form.is_valid():

            # May or may not want to save this information to the database
            # form.save()

            message = 'From ' + form.cleaned_data['full_name'] + "\r\n"
            message = message + 'Repository ' + form.cleaned_data['repository_name'] + "\r\n"
            message = message + 'Message ' + form.cleaned_data['message'] + "\r\n"
            
            # send_mail does not work locally
            # send_mail(
            #     'NAFAN Repository Application',
            #     message,
            #     form.cleaned_data['email'],
            #     ['aaf8qn@virginia.edu'],  # This needs to be added to constants or application settings
            #     fail_silently=False,
            # )

            messages.success(request, 'Your message has been sent to the NAFAN staff.')

            # This blanks out the fields on the form
            form = RepositoryApplicationForm()

    else:

        form = RepositoryApplicationForm()
        
    return render(request, 'NAFAN/newToNAFAN.html', {'form': form})

def contributor_admin(request):
    return render(request, "Admin/contributor_admin.html")

def nafan_admin(request):
    return render(request, "Admin/nafan_admin.html")

def contributor(request):
    return render(request, "FindingAids/finding_aids.html")

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


# Users

def users(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    searchField = request.GET.get('search_field', '')
    searchTerm = request.GET.get('search_term', '')
    statusFilter = request.GET.get('status_filter', '')

    user_list = NAFANUser.GetUsers(searchField, searchTerm, statusFilter)

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
        form.save()
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
        return HttpResponseRedirect("/Users/users")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "Users/update_user.html", context)


# Repositories

def repositories(request):

    searchField = request.GET.get('search_field', '')
    searchTerm = request.GET.get('search_term', '')

    email = request.session['current_login']
    user = NAFANUser.GetUser(email)

    if user.user_type == "nafan_admin":
        repositories = Repository.GetRepositories(searchField, searchTerm)
        return render(request,'Repositories/repositories.html',{"repositories":repositories, "user_type":user.user_type})
    else:
        repositories = Repository.GetUserRepositories(request.user.username)
        return render(request,'Repositories/repositories.html',{"repositories":repositories, "user_type":user.user_type})

def update_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Repository, id = id)
 
    # pass the object as instance in form
    form = RepositoryForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/Repositories/repositories")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "Repositories/update_repository.html", context)

def create_repository(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    form = RepositoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/Repositories/repositories")
         
    context['form']= form

    return render(request, "Repositories/create_repository.html", context)

def delete_repository(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Repository, id = id)
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # list view
        return HttpResponseRedirect("/Repositories/repositories")
 
    context["aid_name"] = obj.title
    return render(request, "Repositories/delete_repository.html", context)


# User Repositories

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

def user_repositories(request):
    username = request.GET.get('username', None)

    user_repositories = User_Repositories.GetRepositories(username)
    repositories = Repository.objects.all()

    return render(request,'NAFAN/Admin/user_repositories.html',
        {"repositories":repositories, 'user_repositories': user_repositories, 'username': username})

def add_user_repository(request):
    username = request.GET.get('username', None)
    repository = request.GET.get('repository', None)

    User_Repositories.AssignRepository(username, repository)

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
         
    email = request.session['current_login']
    user = NAFANUser.GetUser(email)
    context['user_type']= user.user_type

    context['repository_name']= repository.repository_name

    return render(request, "FindingAids/finding_aids.html", context)

def create_aid(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    repository = Repository.GetRepositoryByID(request.session['active_repository'])
    initial_dict = {
        "repository" : repository.repository_name
    }
    context['repository_name']= repository.repository_name

    # add the dictionary during initialization
    form = FindingAidForm(request.POST or None, initial = initial_dict)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/FindingAids/finding_aids/" + request.session['active_repository'])
         
    context['form']= form

    return render(request, "FindingAids/create_aid.html", context)

def delete_aid(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(FindingAid, id = id)
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # list view
        return HttpResponseRedirect("/FindingAids/finding_aids")
 
    context["aid_name"] = obj.title
    return render(request, "FindingAids/delete_aid.html", context)

def update_aid(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    aid = get_object_or_404(FindingAid, id = id)
 
    # pass the object as instance in form
    form = FindingAidForm(request.POST or None, instance = aid)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()

        FindingAid.DACSIndex(aid)

        return HttpResponseRedirect("/FindingAids/finding_aids/" + str(request.session['active_repository']))
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "FindingAids/update_aid.html", context)