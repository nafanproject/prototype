
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from .models import GeeksForm, GeeksModel

    # path("Test/create_view", views.create_view, name="create_view"),    
    # path("Test/list_view", views.list_view, name="list_view"),    
    # path('Test/detail_view/<int:id>', views.detail_view, name="detail_view" ),
    # path('Test/update_view/<int:id>', views.update_view, name="update_view" ),
    # path('Test/delete_view/<int:id>', views.delete_view, name="delete_view" ),

def get_repository(request):
    name = request.GET.get('name', None)
    request.session['last_repository'] = name

    return HttpResponseRedirect("/FindingAids/finding_aids")

   # There has to be a better way
    response = Repository.GetRepositoryByName(name)
    x = response.pk

    return HttpResponse(json.dumps({'id': x}), content_type="application/json")

    # response_json = serializers.serialize('json', x)
    # return HttpResponse(response_json, content_type='application/json')


def create_view(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    form = GeeksForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/Test/list_view")
         
    context['form']= form
    return render(request, "Test/create_view.html", context)

def list_view(request):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    context["dataset"] = GeeksModel.objects.all()
         
    return render(request, "Test/list_view.html", context)

def detail_view(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
  
    # add the dictionary during initialization
    context["data"] = GeeksModel.objects.get(id = id)
          
    return render(request, "Test/detail_view.html", context)

def update_view(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(GeeksModel, id = id)
 
    # pass the object as instance in form
    form = GeeksForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        form.save()
        return HttpResponseRedirect("/Test/list_view")
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "Test/update_view.html", context)

def delete_view(request, id):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(GeeksModel, id = id)
 
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to
        # list view
        return HttpResponseRedirect("/Test/list_view")
 
    return render(request, "Test/delete_view.html", context)

def update_repository_by_name(request, name):
    # dictionary for initial data with
    # field names as keys
    context ={}
 
    obj = Repository.GetRepositoryByName(name)
 
    # pass the object as instance in form
    form = RepositoryForm(request.POST or None, instance = obj)
 
    # add form dictionary to context
    context["form"] = form
 
    return render(request, "Repositories/update_repository.html", context)

