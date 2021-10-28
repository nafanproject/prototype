from django import forms
from django.db import models
from django.forms import ModelForm
from django.conf import settings

from zipfile import ZipFile

import csv
import os

# https://docs.djangoproject.com/en/3.2/topics/db/examples/many_to_many/

# Each contributor can be associated to multiple repositories and each repository can have multiple users
# There is some inclination to make the parent organization its own class in order to store information about
# the parent separate from the repository.  This would be acheived by a new class with the identifier id in the
# repository.  The RepoData, while having a parent field was sparsely populated for that field.
class Repository(models.Model):

    # This id choice assumes we use the imported ids from RepoData.
    repo_id = models.CharField(max_length=255, blank=False)
    repository_name = models.CharField(verbose_name="Repository", max_length=255, blank=False)
    name_notes = models.CharField(max_length=255, blank=True)
    parent_organization = models.CharField(max_length=255, blank=True)
    repository_name_authorized = models.CharField(max_length=255, blank=True)
    repository_identifier_authorized = models.CharField(max_length=255, blank=True)
    repository_type = models.CharField(max_length=255, blank=True)
    location_type = models.CharField(max_length=255, blank=True)
    street_address_1 = models.CharField(max_length=255, blank=True)
    street_address_2 = models.CharField(max_length=255, blank=True)
    po_box = models.CharField(max_length=255, blank=True)
    st_city = models.CharField(verbose_name="City", max_length=255, blank=True)
    st_zip_code_5_numbers = models.CharField(max_length=255, blank=True)
    st_zip_code_4_following_numbers = models.CharField(max_length=255, blank=True)
    street_address_county = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    latitude = models.CharField(max_length=255, blank=True)
    longitude = models.CharField(max_length=255, blank=True)
    language_of_entry = models.CharField(max_length=255, blank=True)
    date_entry_recorded = models.CharField(max_length=255, blank=True)
    entry_recorded_by = models.CharField(max_length=255, blank=True)
    source_of_repository_data = models.CharField(max_length=255, blank=True)
    url_of_source_of_repository_data = models.CharField(max_length=255, blank=True)
    notes = models.CharField(max_length=5096, blank=True)
    geocode_confidence = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.repository_name

    # This function assumes the RepoData file has been de-duplicated
    def handle_RepoData_upload(filepath):

        response = "OK"

        with open(filepath, newline='', encoding="utf8") as csvfile:
            try:

                name = ""
                count = 0

                reader = csv.DictReader(csvfile)
                for row in reader:

                    name = row['repository_name_unauthorized']

                    repository = Repository()
                    repository.repo_id = row['id']
                    repository.repository_name = row['repository_name_unauthorized'].replace("\n", " ")
                    repository.name_notes = row['name_notes']
                    repository.parent_organization = row['parent_org_unauthorized']
                    repository.repository_name_authorized = row['repository_name_authorized']
                    repository.repository_identifier_authorized = row['repository_identifier_authorized']
                    repository.repository_type = row['repository_type']
                    repository.location_type = row['location_type']
                    repository.street_address_1 = row['street_address_1']
                    repository.street_address_2 = row['street_address_2']
                    repository.po_box = row['po_box']
                    repository.st_city = row['st_city']
                    repository.st_zip_code_5_numbers = row['st_zip_code_5_numbers']
                    repository.st_zip_code_4_following_numbers = row['st_zip_code_4_following_numbers']
                    repository.street_address_county = row['street_address_county']
                    repository.state = row['state']
                    repository.url = row['url']
                    repository.latitude = row['latitude']
                    repository.longitude = row['longitude']
                    repository.language_of_entry = row['language_of_entry']
                    repository.date_entry_recorded = row['date_entry_recorded']
                    repository.entry_recorded_by = row['entry_recorded_by']
                    repository.source_of_repository_data = row['source_of_repository_data']
                    repository.url_of_source_of_repository_data = row['url_of_source_of_repository_data']
                    repository.notes = row['notes']
                    repository.geocode_confidence = row['geocode_confidence']

                    count = count + 1
                    # if count < 100:
                    try:
                        repository.save()
                    except Exception as e:
                        response = "Exception " + repository.repository_name + " " + str(e)
                        return response

                response = str(count) + " institutes found"
            except Exception as e:
                response = "Unable to process the " + filepath + " file after " + name + " " + str(e)

        return response

    def GetRepositoryByID(id):
        return Repository.objects.get(id=id)

    def GetRepositoryByName(name):
        return Repository.objects.get(repository_name=name)

    def GetRepositoryByNameSerialize(name):
        return Repository.objects.filter(repository_name=name)

    def GetRepositories(searchField, searchTerm):
        results = []
        if searchTerm:
            if searchField == "repository_name":
                    results = Repository.objects.filter(repository_name__icontains=searchTerm).order_by('repository_name')
            else:
                    results = Repository.objects.filter(state__icontains=searchTerm).order_by('repository_name')
        else:
            return Repository.objects.all()[:50]

        return results

    def GetUserRepositories(username):
        return Repository.objects.all()[:50]

##############################

class RepositoryForm(ModelForm):
    class Meta:
        model = Repository
        fields = '__all__'

        widgets = {
            'repository_name': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'parent_organization': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository_type': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'street_address_1': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'st_city': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'state': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'st_zip_code_5_numbers': forms.TextInput(attrs={'class': 'form-control large_field'}),
        }

##############################

class User_Repositories(models.Model):

    user_name = models.CharField(max_length=255, blank=False)
    repository_name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.repository_name

    def GetRepositories(username):
        return User_Repositories.objects.filter(user_name=username).order_by('repository_name')

    def AssignRepository(username, repository_name):
        assignment = User_Repositories()
        assignment.user_name = username
        assignment.repository_name = repository_name
        assignment.save()

        return True

    def RemoveRepository(username, repository_name):
        User_Repositories.objects.filter(user_name=username).filter(repository_name=repository_name).delete()



##############################

class RepositoryApplication(models.Model):

    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    repository_name = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

class RepositoryApplicationForm(ModelForm):
    class Meta:
        model = RepositoryApplication
        fields = '__all__'
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'email': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'cols': '5'}),
        }

##############################

class UploadFileForm(forms.Form):
    # title = forms.CharField(max_length=50)
    file = forms.FileField()


def extract_uploaded_zip(filename):

    # opening the zip file in READ mode
    with ZipFile(filename, 'r') as zip:

        zip.extractall(os.path.join(settings.BASE_DIR, 'uploads'))

    os.remove(filename)
    return filename


def save_uploaded_file(f):
    filename = os.path.join(settings.BASE_DIR, 'uploads', f.name)
    # with open(filename, 'wb') as destination:
    #     for chunk in f.chunks():
    #         destination.write(chunk)
    return filename