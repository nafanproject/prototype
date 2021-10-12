
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages

from .models import RepositoryApplicationForm

def home(request):

    # search_term = request.GET.get('searchTerm', '')
    # if search_term:

    #     response = NAFAN_ElasticSearch.search(search_term)

    #     return render(request, 'NAFAN/index.html', {"search":search_term, "response":response})
    # else:

    return render(request, "NAFAN/index.html")

def newToNAFAN(request):

    list(messages.get_messages(request))

    # This handles users requesting entry into the NAFAN repository family
    if request.method == 'POST':

        form = RepositoryApplicationForm(request.POST)
        
        if form.is_valid():

            # May or may not want to save this information to the database
            # application.save()

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
