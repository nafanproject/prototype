
import json
import re

from django import forms
from django.db import models
from django.forms import ModelForm

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

# A single-level description with the minimum number of DACS elements includes:

# Reference Code Element (2.1)
# Name and Location of Repository Element (2.2)
# Title Element (2.3)
# Date Element (2.4)
# Extent Element (2.5)
# Name of Creator(s) Element (2.6) (if known)
# Scope and Content Element (3.1)
# Conditions Governing Access Element (4.1)
# Languages and Scripts of the Material Element (4.5)
# Rights Statements for Archival Description (8.2)

class FindingAid(models.Model):
    repository = models.CharField(max_length=255, blank=True)
    reference_code = models.CharField(max_length=255, blank=True)
    name_and_location = models.CharField(max_length=255, blank=False)
    title = models.CharField(max_length=255, blank=False)
    date = models.CharField(max_length=255, blank=False)
    extent = models.CharField(max_length=255, blank=True)
    creator = models.CharField(max_length=255, blank=True)
    scope_and_content = models.TextField()
    governing_access = models.TextField()
    languages = models.CharField(max_length=255, blank=True)
    rights = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title

    def GetFindingAidsByRepository(name):
        return FindingAid.objects.filter(repository=name)

    def DACSIndex(aid):

        es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

        record = {'id': aid.pk, 'repository': aid.repository, 'content': aid.scope_and_content}
        json_record = json.dumps(record)

        try:
            outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))

    def Search(searchTerm):

        client = Elasticsearch()

        s = Search(using=client, index="nafan").query("match", content=searchTerm)

        s = s.highlight('content', fragment_size=100)

        # s = Search(using=client, index="snac") \
        #     .filter("term", category="search") \
        #     .query("match", content=searchTerm)   \
        #     .exclude("match", url="x")

        s.aggs.bucket('per_tag', 'terms', field='tags') \
            .metric('max_lines', 'max', field='lines')

        response = s.execute()

        # for hit in response:
        #     print(hit.meta.score, hit.content)

        hits = []

        for hit in response['hits']['hits']:

            response = {"repository": hit["_source"].repository, "content": hit["_source"].content}
            hits.append(response)
        
        return hits


class FindingAidForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = '__all__'
        
        widgets = {
            'repository': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'reference_code': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'name_and_location': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'title': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'date': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'extent': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'creator': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'scope_and_content': forms.Textarea(attrs={'class': 'form-control large_field'}),
            'governing_access': forms.Textarea(attrs={'class': 'form-control  large_field'}),
            'languages': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'rights': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'active': forms.BooleanField(),
        }

    def __init__(self, *args, **kwargs): 
        super(FindingAidForm, self).__init__(*args, **kwargs)                       
        self.fields['repository'].disabled = True


class FindingAidCreation(CreateView):
    model = FindingAid
    form_class = FindingAidForm
    success_url = reverse_lazy('findingaids')
    # initial = {"repository": "Placeholder title"}

    def get_initial(self):
        initial = super().get_initial()
        initial['repository'] = "Repository"
        return initial

class FindingAidUpdate(UpdateView):
    model = FindingAid
    form_class = FindingAidForm
    success_url = reverse_lazy('findingaids')


def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  cleantext = cleantext.replace("\r","")
  cleantext = cleantext.replace("\n","")
  return cleantext
