
import json
import re
import io
import requests
import json

from datetime import date

from django import forms
from django.db import models
from django.forms import ModelForm

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from bs4 import BeautifulSoup
from pymarc import MARCReader
from PyPDF2 import PdfFileReader
from sickle import Sickle

from django.conf import settings

# The field sizes in the table definitions are all over the place as this was just to get the prototype
# working with provided samples and there were no discussions of realistic values

FILE_TYPES = [('EAD', 'EAD'), ('MARC', 'MARC (under development)'), ('PDF', 'PDF (under development)')]
HARVEST_TYPES = [('File', 'File'),('Directory', 'Directory'), ('Sitemap', 'Sitemap'), ('OAI', 'OAI-PMH')]
DAYS = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '...')]
HOURS = [('12AM', '12AM'), ('12:30AM', '12:30AM'), ('1AM', '1AM'), ('4', '...')]
CCS = [('CC BY', 'CC BY:'), ('CC BY-SA', 'CC BY-SA'), ('CC BY-NC', 'CC BY-NC'), ('CC BY-NC-SA', 'CC BY-NC-SA'), ('CC BY-ND', 'CC BY-ND'), ('CC BY-NC-ND', 'CC BY-NC-ND'), ('CC0', 'CC0')]

# Handles chronitem
class Chronology(models.Model):
    finding_aid_id = models.CharField(max_length=32, blank=True)
    date = models.CharField(max_length=255, blank=True)
    event = models.CharField(max_length=1255, blank=True)
    sort_order = models.IntegerField()

# Handle controlaccess
class ControlAccess(models.Model):
    finding_aid_id = models.CharField(max_length=32, blank=True)
    term = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=1255, blank=True)
    control_type = models.CharField(max_length=1255, blank=True)

# Audits of Finding Aid creation and modification
class FindingAidAudit(models.Model):
    finding_aid_id = models.CharField(max_length=32, blank=True)
    revision_notes = models.CharField(max_length=255, blank=True)
    update_date = models.DateField(null=True)
    updated_by = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.revision_notes

    def AddAudit(finding_aid_id, revision_notes, updated_by, update_date):
        audit = FindingAidAudit()
        audit.finding_aid_id = finding_aid_id
        audit.revision_notes = revision_notes
        audit.updated_by = updated_by
        audit.update_date = update_date

        try:
            audit.save()
        except Exception as ex:
            print(str(ex))
            
        return True

    def GetAudit(finding_aid_id):
        return FindingAidAudit.objects.filter(finding_aid_id=finding_aid_id).order_by('-update_date')

# Used to add Subject Headers for a finding aid to be used with searches.  These have not been added to
# the Elasticsearch functionality.  I believe the desired implementation is to have them as available values
# per repository and then make them available to select at the finding aid level.
class FindingAidSubjectHeader(models.Model):
    finding_aid_id = models.CharField(max_length=32, blank=True)
    subject_header = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.subject_header

    def AddSubjectHeader(finding_aid_id, subject_header):
        assignment = FindingAidSubjectHeader()
        assignment.finding_aid_id = finding_aid_id
        assignment.subject_header = subject_header

        try:
            assignment.save()
        except Exception as ex:
            print(str(ex))
            
        return True

    # Need a remove

    def GetSubjectHeaders(finding_aid_id):
        return FindingAidSubjectHeader.objects.filter(finding_aid_id=finding_aid_id)

class FindingAid(models.Model):

    # Metadata related for NAFAN use
    aid_type = models.CharField(max_length=10, blank=True)
    elasticsearch_id = models.CharField(max_length=32, blank=True)
    last_update = models.CharField(max_length=32, blank=True)
    updated_by = models.CharField(max_length=32, blank=True)
    revision_notes = models.CharField(max_length=1023, blank=True)

    # Currently text, should probably be an ID
    repository = models.CharField(max_length=255, blank=True)

    # Basic finding structure corresponding to DACS several fields overlap with EAD
    reference_code = models.CharField(max_length=1255, blank=True)
    title = models.CharField(max_length=1255, blank=False)
    date = models.CharField(max_length=1255, blank=True)
    extent = models.CharField(max_length=1255, blank=True)
    creator = models.CharField(max_length=1255, blank=True)
    scope_and_content = models.TextField(blank=True)
    governing_access = models.TextField(blank=True)
    languages = models.CharField(max_length=1255, blank=True)
    rights = models.CharField(max_length=1255, blank=True)
    indent = models.CharField(max_length=255, blank=True)

    intra_repository = models.CharField(max_length=1255, blank=True)
    level = models.CharField(max_length=32, blank=True)
    creative_commons = models.CharField(max_length=32, blank=True)

    custodhist = models.CharField(max_length=1255, blank=True)
    acqinfo = models.CharField(max_length=5255, blank=True)
    processinfo = models.CharField(max_length=1255, blank=True)
    container = models.CharField(max_length=1255, blank=True)

    repository_link = models.CharField(max_length=1255, blank=True)
    digital_link = models.CharField(max_length=1255, blank=True)
    
    scope_and_content_raw = models.CharField(max_length=5255, blank=True)
    note = models.CharField(max_length=555, blank=True)

    abstract = models.TextField(blank=True)
    citation = models.CharField(max_length=1255, blank=True)
    bioghist = models.TextField(blank=True)
    originals_location = models.TextField(blank=True)
    
    ark = models.CharField(max_length=1255, blank=True)
    snac = models.CharField(max_length=1255, blank=True)
    wiki = models.CharField(max_length=1255, blank=True)
    associated_file = models.CharField(max_length=1255, blank=True)

    # archref needs to be treated like a <cXX> element
    # bibliography consists of a list of <bibref> and/or other elements, pull into single entry
    # <c> treated with a find_all and handled like the <cXX>
    
    # This is the base Finding aid ID used to maintain relationships between the archref and <cXX>
    # components within the search engine as each are independent entries
    progenitorID = models.IntegerField(default=0, blank=True)

    # This is used to keep the relationship going through <cXX> components
    parentID = models.IntegerField(default=0, blank=True)

    component = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.title

    # This needs to be converted to GetByID if the name are not made canonical and be duplicate
    def GetFindingAidsByRepository(name):
        return FindingAid.objects.filter(repository=name)

    # The Elasticsearch index consists of:
    # id - finding aid ID
    # type - type of item being indexed (web page, EAD, MARC, etc.)
    # title - title of the item being indexed
    # repository - name of the repository that owns the finding aid
    # content - whatever makes sense to index
    # source - Originally thought to hold things like file name, not sure if it is useful anymore
    # destination - Originally thought to hold the link to external links, not used and always blank currently

    def CreateIndex(id, index_type, title, repository_name, description, source):

        elasticsearch_id = "Fail"   # Bit dicey to mix and match IDs and text, but if Python doesn't care...

        # If there is something to index
        if title or description:
            es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))
            
            # For insert no need for {'doc': }
            record = {'id': id, 'type': index_type, 'title': title, 'repository': repository_name, 'content': description, 'source': source, 'destination': ""}
            json_record = json.dumps(record)

            try:
                outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                elasticsearch_id = outcome['_id']

            except Exception as ex:
                print('Error in indexing data')
                print(str(ex))
        
        return elasticsearch_id

    def UpdateIndex(id, elasticsearch_id, index_type, title, repository_name, description, source):

        # If there is something to index
        if title or description:
            
            es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

            # For update it needs to be wrapped in {'doc': }
            record = {'doc':{'id': id, 'type': index_type, 'title': title, 'repository': repository_name, 'content': description, 'source': source, 'destination': ""}}
            json_record = json.dumps(record)

            try:
                outcome = es.update(id=elasticsearch_id, index='nafan', doc_type='_doc', body=json_record)
                elasticsearch_id = outcome['_id']
            except Exception as ex:
                print('Error in indexing data')
                print(str(ex))

        return elasticsearch_id

    def RemoveIndex(elasticsearch_id):

        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        try:
            es.delete(index="nafan",doc_type="_doc", id=elasticsearch_id)
        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))

    def EADIndex(id, repository, filepath, user_name):
                    
        response = "OK"

        with open(filepath, newline='', encoding="utf8") as ead_file:

            if id == "new":
                aid = FindingAid()
            else:
                aid = FindingAid.objects.get(id=id)

            aid.aid_type = "ead"
            aid.repository = repository

            # Yank the text and start parsing it
            html_doc = ead_file.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            # Make an internal EAD from the initial file
            # The EAD parsing is not as elegant as it should be in a final implementation
            response = FindingAid.MakeEAD(id, soup, aid, user_name, filepath)

        return response

    def MakeEAD(id, soup, aid, user_name, filepath):
        
        response = "OK"

        # Access the search engine for indexing
        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        try:

            archdesc = soup.find('archdesc')
            did = archdesc.find('did')

            # parse the archdesc did
            aid = FindingAid.ParseDid(did, aid, "archdesc")

            # if the following weren't found in the high did, go look for them

            # Have to consider there will be more than one dao
            # The digital object can be specified with an entityref attribute.  Need example.
            digital_link = soup.find_all('dao') 
            # if FindingAid.legit_component(digital_link, component_level):
            for digitals in digital_link:
                aid.digital_link = digitals['href']   

            # There can be multiple accessrestrict entries
            if not aid.governing_access:
                aid.governing_access = String_or_p_tag(soup, 'accessrestrict')
                # governing_access = did.find_all('accessrestrict') 
                # if governing_access:
                #     for entry in governing_access:
                #         aid.governing_access = aid.governing_access + entry.get_text() + " "
                #     aid.governing_access = cleanhtml(str(aid.governing_access))
                #     aid.governing_access = aid.governing_access.strip()

            if not aid.rights:
                aid.rights = String_or_p_tag(soup, 'userestrict')
            
            if not aid.citation:
                aid.citation = String_no_p_tag(soup, 'prefercite')
            
            if not aid.bioghist:
                aid.bioghist = String_or_p_tag(soup, 'bioghist')
            
            if not aid.scope_and_content:
                aid.scope_and_content = String_or_p_tag(soup, 'scopecontent')
            
            if not aid.custodhist:
                aid.custodhist = String_or_p_tag(soup, 'custodhist')
            
            if not aid.acqinfo:
                aid.acqinfo = String_or_p_tag(soup, 'acqinfo')
            
            if not aid.processinfo:
                process = soup.find_all('processinfo')
                if process:
                    for item in process:
                        try:
                            aid.processinfo = aid.processinfo + " " + item.p.string
                        except Exception as ex:
                            print('Error handling processinfo ' + str(ex))

            if not aid.originals_location:
                aid.originals_location = String_or_p_tag(soup, 'originalsloc')
                
            # Mark the indexing date and the user who did the indexing
            today = date.today()
            aid.last_update = today.strftime("%B %d, %Y")
            aid.updated_by = user_name

            aid.save()

            # The progenitor is used to keep track of related archdesc and cXX entries
            progenitorID = aid.pk

            aid.ark = "ark://" + str(aid.pk)

            # If the snac and wiki links are going to be, a method for specifying them
            # needs to be introduced.  Same problem as always with mass uploads
            aid.snac = "https://snaccooperative.org"
            aid.wiki = "https://www.wikidata.org"

            sortOrder = 0
            chronology = soup.find_all('chronitem')
            if chronology:
                for chron in chronology:
                    item = Chronology()
                    item.finding_aid_id = aid.pk
                    item.date = chron.date.string
                    item.event = chron.event.string
                    item.sort_order = sortOrder
                    item.save()
                    sortOrder = sortOrder + 1

                    # after the aid is saved, other aspects of the finding aid can be associated

                    # the language information probably needs to come down here

                    # <controlaccess>
                    # subheaders
                    #   <corpname>
                    #   <famname>
                    #   <function>
                    #   <genreform>
                    #   <geogname>
                    #   <occupation>
                    #   <persname>
                    #   <subject>
                    #   <title>

            control = soup.find('controlaccess')
            if control:
                entries = control.find_all('corpname')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "corpname"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('famname')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "famname"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('function')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "function"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('genreform')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "genreform"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('geogname')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "geogname"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('occupation')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "occupation"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('persname')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "persname"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('subject')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "subject"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()
                entries = control.find_all('title')
                if entries:
                    for entry in entries:
                        item = ControlAccess()
                        item.finding_aid_id = progenitorID
                        item.control_type = "title"
                        item.term = entry.string
                        if entry.has_attr('authfilenumber'):
                            item.link = entry['authfilenumber']
                        item.save()

            # Once the control list is filled, add them to the finding aid through FindingAidSubjectHeader
            # Needs to be implemented
                
            # otherfindaid can be text or an extref link to another finding aid
            # There can be multiple subheaders or combinations thereof
            # has to be handled like <controlaccess>
            temp = ""
            other = soup.find('otherfindaid')
            if other:
                entries = other.find_all('bibref')
                for entry in entries:
                    temp = entry.get_text()
                    temp = cleanhtml(str(temp))

                        # The entry contains all the text of an element with the tags including the searched tag
                        # So theoretically the get_text could be indexed while the entry is stored in the database
                        # to be processed converting the tags to html format (or do it on the way into the database)
                        # print(entry)

                entries = other.find_all('extref')
                for entry in entries:
                    temp = entry.string
                    temp = entry['href']

            # Process the component fields through a recursive function
            components_list = []
            c01s = soup.find_all("c01")
            for c01 in c01s:
                FindingAid.ProcessComponents(soup, c01, progenitorID, progenitorID, 1)

            try:

                # Index the processed portion of the EAD.  Each component is indexed separately.

                source_url = filepath
                destination_url = ""

                if id == "new":

                    record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
                    json_record = json.dumps(record)

                    outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                    elasticsearch_id = outcome['_id']

                    aid.elasticsearch_id = elasticsearch_id

                    aid.save()
                else:

                    # Update an existing entry
                    record = {'doc':{'id': id, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': ""}}
                    json_record = json.dumps(record)

                    es.update(id=aid.elasticsearch_id, index='nafan', doc_type='_doc', body=json_record)

            except Exception as ex:
                print('Error in indexing data')
                print(str(ex))

        except Exception as e:
            print("Unable to process the " + filepath + " file " + str(e))
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def ParseDid(soup, aid, component_level):

        # There is a situation where the parsing of a <cXX> component can pick up the elements
        # associated with a child of the component since the child's elements are included in the
        # tag pickup

        # One way to possibly deal with this is to make sure the item's level matches the expected
        # level, meaning if we are parsing <c01> and the parent of an element is <c02>, we don't want
        # the data for that tag

        # ToDo: There are assignments in place that assign a string from an element.  If there is a subfield
        # within the string, the assignment is crashing.  For example some of the abstract elements in components
        # of syr-wayland-smith_p.xml in the eaddiva files.

        did = soup.find('did')
        if not did:
            did = soup

        aid.level = component_level

        title = did.find('unittitle')
        if FindingAid.legit_component(title, component_level):
            aid.title = title.string

        try:
            if not aid.title:
                if title:
                    searched_title = title.next
                    if searched_title:
                        aid.title = searched_title.string

            if not aid.title:
                subtitle = title.find('title')
                if subtitle:
                    aid.title = subtitle.string

        except Exception as ex:
            print('Error getting title')
            print(str(ex))

        if not aid.title:
            aid.title = "No title"
        
        dates = did.find_all('unitdate') 
        for date in dates: 
            if date.has_attr('type'):
                attribute = date['type']
                if attribute == "bulk":
                    aid.date = aid.date + " [bulk " + date.string + "]"   
                else:
                    aid.date = aid.date + " " + date.string
            else:
                aid.date = date.string
        if aid.date:
            aid.date = aid.date.strip()    

        containers = did.find_all('container') 
        for container in containers:
            if container.has_attr('type'):
                aid.container = aid.container + container['type']
            if container.string:
                aid.container = aid.container + " " + container.string + " "   

        repository = did.find('repository')
        if FindingAid.legit_component(repository, component_level):
            corpname = repository.find('corpname')
            if corpname:
                aid.intra_repository = corpname.string
            else:
                aid.intra_repository = ""

        reference_codes = did.find_all('unitid') 
        for entry in reference_codes:
            aid.reference_code = aid.reference_code + entry.string + "; "

        # Multiple creators looks a little weird with this technique
        creator = did.find_all('origination') 
        if creator:
            for entry in creator:
                aid.creator = aid.creator + entry.get_text() + " "
            aid.creator = cleanhtml(str(aid.creator))
            aid.creator = aid.creator.strip()

        # Using this technique smashes words together from different tags
        # Found this
        #   <container type="box" label="Box ">1 </container>
        # physdesc = did.find('physdesc')
        # if physdesc:
        #     aid.extent = physdesc.get_text()
        #     aid.extent = cleanhtml(str(aid.extent))

        physdescs = did.find_all('extent') 
        for entry in physdescs:
            aid.extent = aid.extent + entry.string + "; "

        aid.abstract = String_or_p_tag(did, 'abstract')

        # abstract = did.find('abstract')
        # if abstract:
        #     aid.abstract = abstract.string

        # if not aid.abstract:
        #     searched_abstract = abstract.next
        #     if searched_abstract:
        #         aid.abstract = searched_abstract.string

        # First see if langmaterial has text
        languages = did.find_all('langmaterial')
        for lang in languages:
            aid.languages = aid.languages  + " " + lang.get_text()

        # If there is no langmaterial text, look for languages
        aid.languages = aid.languages.strip()
        if not aid.languages:
            languages = did.find_all('language')
            for lang in languages:
                if lang.string:
                    aid.languages = aid.languages + " " + lang.string 
                else:
                    # If no language text, pull the langcode
                    aid.languages = lang['langcode']

        # Although the following are not necessarily in the high did, they are here because
        # they may be contained in a <cXX>

        # There can be multiple accessrestrict entries
        aid.governing_access = String_or_p_tag(did, 'accessrestrict')
        # governing_access = did.find_all('accessrestrict') 
        # if governing_access:
        #     for entry in governing_access:
        #         aid.governing_access = aid.governing_access + entry.get_text() + " "
        #     aid.governing_access = cleanhtml(str(aid.governing_access))
        #     aid.governing_access = aid.governing_access.strip()

        aid.rights = String_or_p_tag(did, 'userestrict')
        aid.citation = String_no_p_tag(did, 'prefercite')

        aid.bioghist = String_or_p_tag(did, 'bioghist')
        aid.scope_and_content = String_or_p_tag(did, 'scopecontent')
        aid.originals_location = String_or_p_tag(did, 'originalsloc')
        aid.note = String_or_p_tag(did, 'note')

        return aid

    def legit_component(component, component_level):

        if not component:
            return False

        component_parent = component.parent
        if component_parent.name == "did":
            component_parent = component_parent.parent

        if component_parent.name == component_level:
            return True

        return False

    def ProcessComponents(real_soup, soup, progenitorID, parentID, component_level):

        # Process this level
        current_level = ""
        if component_level < 10:
            current_level = "c0" + str(component_level)
        else:
            current_level = "c" + str(component_level)

        aid = FindingAid()

        # did = soup.find('did')
        # if did:
        #     aid = FindingAid.ParseDid(did, aid, current_level)
        # else:
        aid = FindingAid.ParseDid(soup, aid, current_level)

        if not aid.scope_and_content:
            # aid.scope_and_content = String_or_p_tag(soup, 'scopecontent')

                entries = soup.find_all('scopecontent')
                if entries:
                    entry = entries[0]

                    # finding tag whose child to be deleted
                    div_bs4 = entry.find('head')
                    
                    # delete the child element
                    if div_bs4:
                        div_bs4.clear()

                    element = entry.find('title')
                    if element:
                        new_tag = real_soup.new_tag("i")
                        new_tag.string = element.string
                        element.replace_with(new_tag)

                    aid.scope_and_content = str(entry)

        aid.progenitorID = progenitorID
        aid.parentID = parentID
        aid.component = current_level

        for x in range(1, component_level):
            aid.indent = aid.indent + "&nbsp;&nbsp;"

        aid.save()

        # Process the children
        component_level = component_level + 1

        if component_level < 10:
            search_for = "c0" + str(component_level)
        else:
            search_for = "c" + str(component_level)

        components = soup.find_all(search_for)
        for component in components:
            # did = component.find('did')
            # if did:
            #     FindingAid.ProcessComponents(did, progenitorID, aid.pk, component_level)
            # else:
                FindingAid.ProcessComponents(real_soup, component, progenitorID, aid.pk, component_level)

        return

    def GetFindingAidContents(id, contents):
        pass

    def MARCIndex(id, repository, filepath, user_name):

        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        response = "OK"

        #     # pyMarc can be used for ingesting MARC files
        #     # https://pymarc.readthedocs.io/en/latest/

        with open(filepath, 'rb') as marc_file:
            try:

                if id == "new":
                    aid = FindingAid()
                else:
                    aid = FindingAid.objects.get(id=id)

                aid.aid_type = "marc"
                aid.repository = repository
                aid.intra_repository = repository
                aid.name_and_location = repository

                reader = MARCReader(marc_file)
                for record in reader:
                    aid.title = record['245']['a']      # Title
                    aid.title = cleanhtml(str(aid.title))
                    aid.title = aid.title.rstrip(',')

                    try:
                        aid.creator = record['100']['a']      # "100, 110, or 111;"
                        aid.creator = cleanhtml(aid.creator)
                    except:
                        try:
                            aid.creator = record['110']['a']
                            aid.creator = cleanhtml(aid.creator)
                        except:
                            try:
                                aid.creator = record['111']['a']
                                aid.creator = cleanhtml(aid.creator)
                            except:
                                aid.creator = ""

                    try:
                        aid.reference_code = record['090']  # Call Number
                        aid.reference_code = cleanhtml(aid.reference_code)
                    except:
                        try:
                            aid.reference_code = record['099']
                            aid.reference_code = cleanhtml(aid.reference_code)
                        except Exception as e:
                            aid.reference_code = "mm 98084318"

                    try:
                        aid.date = record['245']['g']
                        aid.date = cleanhtml(aid.date)
                    except:
                        try:
                            aid.date = record['264']['c']
                            aid.date = cleanhtml(aid.date)
                        except Exception as e:
                            aid.date = "1897-2005"

                    try:
                        aid.extent = record['300']['a']
                        aid.extent = cleanhtml(aid.extent)
                        aid.extent = aid.extent + " items "
                    except Exception as e:
                        aid.extent = ""

                    try:
                        aid.languages = record['546']['a']
                        aid.languages = cleanhtml(aid.languages)
                    except Exception as e:
                        aid.languages = ""

                    try:
                        aid.citation = record['510']['a']
                        aid.citation = cleanhtml(aid.citation)
                    except Exception as e:
                        try:
                            aid.citation =  record['524']['a'] 
                            aid.citation = cleanhtml(aid.citation)
                        except Exception as e:
                            aid.citation = ""
                    
                    try:
                        aid.governing_access = record['506']['a'] 
                        aid.governing_access = cleanhtml(aid.governing_access)
                    except Exception as e:
                        aid.governing_access = ""

                    try:
                        aid.rights = record['540']['a'] 
                        aid.rights = cleanhtml(aid.governing_access)
                    except Exception as e:
                        aid.rights = ""

                    try:
                        aid.scope_and_content = record['520']['a'] 
                        aid.scope_and_content = cleanhtml(aid.scope_and_content)
                    except Exception as e:
                        aid.scope_and_content = ""

                    try:
                        aid.bioghist = record['545']['a']        # Biographical or Historical Data
                        aid.bioghist = cleanhtml(aid.bioghist)
                    except Exception as e:
                        aid.bioghist = ""

                    if not aid.scope_and_content:
                        try:
                            aid.scope_and_content = record['500']['a'] 
                            aid.scope_and_content = cleanhtml(aid.scope_and_content)
                        except Exception as e:
                            aid.scope_and_content = ""

                    # Mark the indexing date and the user who did the indexing
                    today = date.today()
                    aid.last_update = today.strftime("%B %d, %Y")
                    aid.updated_by = user_name

                    # Create a json object to index into ElasticSearch
                    source_url = filepath
                    destination_url = ""

                    aid.save()

                    # The snac and wiki links are not pulled out of the marc.  Not sure
                    # how these will be able to be done in a final version.
                    # NAFAN is hosting the Ginsburg entry, hence the ark is based on the
                    # id within NAFAN.  This is also a field that needs to specified.
                    # It seems there will need to be a set of fields associated with an
                    # ingest, the problem being a mass ingest.
                    if "Ginsburg" in aid.title:
                        aid.snac = "https://snaccooperative.org/view/52844840"
                        aid.wiki = "https://www.wikidata.org/wiki/Q11116"
                        aid.ark = "ark://" + str(aid.pk)
                    else:
                        aid.snac = "https://snaccooperative.org"
                        aid.wiki = "https://www.wikidata.org"
                        try:
                            aid.ark = record['856']['u']
                            aid.ark = cleanhtml(aid.ark)
                        except:
                            aid.ark = "ark://" + str(aid.pk)

                    progenitorID = aid.pk

                    FindingAid.MakeMarcSubject(record, progenitorID, '600')
                    FindingAid.MakeMarcSubject(record, progenitorID, '610')
                    FindingAid.MakeMarcSubject(record, progenitorID, '611')
                    FindingAid.MakeMarcSubject(record, progenitorID, '630')
                    FindingAid.MakeMarcSubject(record, progenitorID, '647')
                    FindingAid.MakeMarcSubject(record, progenitorID, '648')
                    FindingAid.MakeMarcSubject(record, progenitorID, '650')
                    FindingAid.MakeMarcSubject(record, progenitorID, '651')
                    FindingAid.MakeMarcSubject(record, progenitorID, '653')
                    FindingAid.MakeMarcSubject(record, progenitorID, '654')
                    FindingAid.MakeMarcSubject(record, progenitorID, '655')
                    FindingAid.MakeMarcSubject(record, progenitorID, '656')
                    FindingAid.MakeMarcSubject(record, progenitorID, '657')
                    FindingAid.MakeMarcSubject(record, progenitorID, '658')
                    FindingAid.MakeMarcSubject(record, progenitorID, '662')
                    FindingAid.MakeMarcSubject(record, progenitorID, '688')
                    
                    # 69X - Local Subject Access Fields (R)  Full | Concise

                    try:

                        if id == "new":

                            record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
                            json_record = json.dumps(record)

                            outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                            elasticsearch_id = outcome['_id']

                            aid.elasticsearch_id = elasticsearch_id

                            aid.save()
                        else:
                            record = {'doc':{'id': id, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}}
                            json_record = json.dumps(record)

                            es.update(id=aid.elasticsearch_id, index='nafan', doc_type='_doc', body=json_record)

                    except Exception as ex:
                        print('Error in indexing data')
                        print(str(ex))

            except Exception as e:
                response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def MakeMarcSubject(record, progenitorID, index, ):

        try:
            for f in record.get_fields(index):
                subject = f['a']
                item = ControlAccess()
                item.finding_aid_id = progenitorID
                item.control_type = "subject"
                item.term = subject
                item.save()                    
        except Exception as e:
            x = ""

    def PDFIndex(id, title, description, repository, filepath):

        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        response = "OK"

        try:

            pdfObj = open(filepath, 'rb')

            if id == "new":
                aid = FindingAid()
            else:
                aid = FindingAid.objects.get(id=id)

            aid.aid_type = "pdf"
            aid.repository = repository
            aid.name_and_location = repository

            # Create a json object to index into ElasticSearch
            aid.title = title
            source_url = filepath
            destination_url = ""

            if description:
                aid.scope_and_content = description
            else:
                reader = PdfFileReader(pdfObj)
                pdfPages = 0
                text = ""
                while pdfPages < reader.getNumPages():
                    text = text + reader.getPage(pdfPages).extractText()
                    pdfPages = pdfPages + 1
                    
                content = cleanhtml(str(text))
                aid.scope_and_content = content

            aid.save()

            try:

                if id == "new":

                    record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
                    json_record = json.dumps(record)

                    outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                    elasticsearch_id = outcome['_id']

                    aid.elasticsearch_id = elasticsearch_id

                    aid.save()
                else:
                    record = {'doc':{'id': id, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': ""}}
                    json_record = json.dumps(record)

                    es.update(id=aid.elasticsearch_id, index='nafan', doc_type='_doc', body=json_record)

            except Exception as ex:
                print('Error in indexing data')
                print(str(ex))

        except Exception as e:
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def Schema_jsonLD_Index(repository, url):

        response = "OK"
        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        try:

            aid = FindingAid()
            aid.aid_type = "schema"
            aid.repository = repository
            aid.name_and_location = repository

            # Opening the html file
            HTMLFile = open(filepath, "r")
  
            # Reading the file
            html_doc = HTMLFile.read()

            # Parse the html file
            soup = BeautifulSoup(html_doc, 'html.parser')

            dict = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))

            content = dict['description']
            aid.title = dict['name']

            # holdingArchive = soup.find("span", property="holdingArchive").next
            # identifier = soup.find("span", property="identifier").next
            # isPartOf = soup.find("a", property="isPartOf").next
            # dateCreated = soup.find("span", property="dateCreated").next
            # url = soup.find("a", property="url").next
            # about = soup.find("span", property="about").next
            # inLanguage = soup.find("span", property="inLanguage").next
            # description = soup.find("span", property="description").next
            # playerType = soup.find("span", property="playerType").next
            
            # Create a json object to index into ElasticSearch
            aid.title = cleanhtml(str(aid.title))
            source_url = filepath
            destination_url = ""
            content = cleanhtml(str(content))
            aid.scope_and_content = content

            aid.save()

            record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
            json_record = json.dumps(record)

            try:
                es.index(index='nafan', doc_type='_doc', body=json_record)
            except Exception as ex:
                print('Error in indexing data')
                print(str(ex))

        except Exception as e:
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def HarvestEADFile(url, repository, user_name):

        # url = 'https://eadiva.com/sampleEAD'
        ext = "xml"

        r = requests.get(url)

        aid = FindingAid()
        aid.aid_type = "ead"
        aid.repository = repository
        aid.name_and_location = repository

        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        response = FindingAid.MakeEAD("new", soup, aid, user_name, url)

        return response

    def HarvestPDFFile(url, repository, user_name):

        ext = "xml"

        r = requests.get(url)

        aid = FindingAid()
        aid.aid_type = "pdf"
        aid.repository = repository
        aid.name_and_location = repository

        # The file desired for the pdf demo is actually an EAD file.

        html_doc = r.text
        soup = BeautifulSoup(html_doc, 'html.parser')

        response = FindingAid.MakeEAD("new", soup, aid, user_name, url)

        return response

    def HarvestEAD(url, repository, user_name):

        # url = 'https://eadiva.com/sampleEAD'
        ext = "xml"

        def listFD(url, ext=''):
            page = requests.get(url).text
            soup = BeautifulSoup(page, 'html.parser')
            return [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

        for ead_file in listFD(url, ext):

            url = ead_file
            r = requests.get(url)

            aid = FindingAid()
            aid.aid_type = "ead"
            aid.repository = repository
            aid.name_and_location = repository

            html_doc = r.text
            soup = BeautifulSoup(html_doc, 'html.parser')

            response = FindingAid.MakeEAD("new", soup, aid, user_name, url)

        return response

    def HarvestOAI(url, repository):

        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        # sickle = Sickle('https://archives.library.vcu.edu/oai')       # Live VCU location
        # sickle = Sickle('https://nafan.archivesspace.org/oai')        # ArchivesSpace sandbox
        sickle = Sickle(url)
        
        recs = sickle.ListRecords(metadataPrefix="oai_ead")  # oai_dc pulls the Dublic Core files
        for r in recs:

            aid = FindingAid()
            aid.aid_type = "ead"
            aid.repository = repository
            aid.name_and_location = repository

            html_doc = r.raw
            soup = BeautifulSoup(html_doc, 'html.parser')

            aid.title = soup.find("titleproper").contents
            aid.title = cleanhtml(str(aid.title))
            source_url = ""             # Going to need to assign this
            destination_url = ""

            try:
                content = soup.find("scopecontent").contents
            except Exception as ex:
                try:
                    content = soup.find("bioghist").contents
                except Exception as ex:
                    content = "No content in the EAD finding aid"

            content = cleanhtml(str(content))
            aid.scope_and_content = content

            aid.reference_code = soup.find("unitid").contents
            aid.reference_code = cleanhtml(str(aid.reference_code))

            aid.extent = soup.find("extent").contents
            aid.extent = cleanhtml(str(aid.extent))

            aid.creator = soup.find("origination").contents
            aid.creator = cleanhtml(str(aid.creator))

            aid.date = soup.find("unitdate").contents
            aid.date = cleanhtml(str(aid.date))

            aid.languages = soup.find("langmaterial").contents
            aid.languages = cleanhtml(str(aid.languages))

            # aid.rights = soup.find("userestrict").contents
            # aid.rights = cleanhtml(str(aid.rights))

            aid.governing_access = soup.find("userestrict").contents
            aid.rights = cleanhtml(str(aid.rights))

            aid.save()

            try:

                record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
                json_record = json.dumps(record)

                outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                elasticsearch_id = outcome['_id']

                aid.elasticsearch_id = elasticsearch_id

                aid.save()

            except Exception as ex:
                print('Error in indexing data')
                print(aid.title)
                print(str(ex))

    def HarvestSitemap(sitemap_url, repository):

        es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        # https://portal.snaccooperative.org/system/files/media/documents/Public/NAFAN_Sitemap.txt

        page = requests.get(sitemap_url).text

        for url in page.splitlines():
            if url and url != "EAD":

                r = requests.get(url)

                aid = FindingAid()
                aid.aid_type = "ead"
                aid.repository = repository
                aid.name_and_location = repository

                html_doc = r.text
                soup = BeautifulSoup(html_doc, 'html.parser')

                # Create a json object to index into ElasticSearch
                # aid.title = soup.select('titleproper')[0].text.strip()
                # aid.title = cleanhtml(str(aid.title))
                aid.title = soup.find("titleproper").contents
                aid.title = cleanhtml(str(aid.title))
                source_url = url
                destination_url = ""

                # content = soup.select('bioghist')[0].text.strip()
                # content = cleanhtml(str(content))
                # aid.scope_and_content = content

                content = soup.find("bioghist").contents
                content = cleanhtml(str(content))
                aid.scope_and_content = content

                aid.reference_code = soup.find("unitid").contents
                aid.reference_code = cleanhtml(str(aid.reference_code))

                aid.extent = soup.find("extent").contents
                aid.extent = cleanhtml(str(aid.extent))

                aid.creator = soup.find("origination").contents
                aid.creator = cleanhtml(str(aid.creator))

                aid.date = soup.find("unitdate").contents
                aid.date = cleanhtml(str(aid.date))

                aid.languages = soup.find("langmaterial").contents
                aid.languages = cleanhtml(str(aid.languages))

                # aid.rights = soup.find("userestrict").contents
                # aid.rights = cleanhtml(str(aid.rights))

                aid.governing_access = soup.find("userestrict").contents
                aid.rights = cleanhtml(str(aid.rights))

                aid.save()

                try:

                    record = {'id': aid.pk, 'type': aid.aid_type, 'title': aid.title, 'repository': aid.repository, 'content': aid.scope_and_content, 'source': source_url, 'destination': destination_url}
                    json_record = json.dumps(record)

                    outcome = es.index(index='nafan', doc_type='_doc', body=json_record)
                    elasticsearch_id = outcome['_id']

                    aid.elasticsearch_id = elasticsearch_id

                    aid.save()

                except Exception as ex:
                    print('Error in indexing data')
                    print(str(ex))

    def ASpace():

        response = "OK"

        # # Sample
        # http://localhost:8089/agents/corporate_entities?page=1&page_size=10
        # # Test URL
        # https://aspacenafan.lyrtech.org/staff/api
        
        # url = 'https://aspacenafan.lyrtech.org/staff/api/agents/corporate_entities?page=1&page_size=10'
        # url = 'https://aspacenafan.lyrtech.org/staff/api/agents/repositories?resolve[]=[record_types, to_resolve]'

        # url = "https://aspacenafan.lyrtech.org/staff/api/agents/repositories?resolve[]=[record_types, to_resolve]"

        # result = requests.get(url).text

        baseURL = 'https://aspacenafan.lyrtech.org/staff/api'
        auth = requests.post('https://aspacenafan.lyrtech.org/staff/api/users/admin/login?password=admin&expiring=false').json()

        session = auth["session"]
        headers = {'X-ArchivesSpace-Session':session}

        results = (requests.get(baseURL + '/repositories?resolve[]=[record_types, to_resolve]', headers=headers)).json()

        # ('lock_version', 2)
        # ('repo_code', 'Space')
        # ('name', 'Repository that Manages Space')
        # ('org_code', 'US-CMALX')
        # ('parent_institution_name', 'Very Important University')
        # ('created_by', 'nancye')
        # ('last_modified_by', 'nancye')
        # ('create_time', '2019-07-26T20:31:59Z')
        # ('system_mtime', '2019-12-09T16:37:38Z')
        # ('user_mtime', '2019-12-09T16:37:38Z')
        # ('publish', True)
        # ('oai_is_disabled', False)
        # ('oai_sets_available', '["888","889","890","891","892","893","894","895","896","897","898"]')
        # ('slug', 'rms_1')
        # ('is_slug_auto', False)
        # ('country', 'US')
        # ('jsonmodel_type', 'repository')
        # ('uri', '/repositories/4')
        # ('display_string', 'Repository that Manages Space (Space)')
        # ('agent_representation', {'ref': '/agents/corporate_entities/26'})

        for result in results:
            print ("Name " + result["name"])
            collectionURL = baseURL + result["uri"] + '/resources?all_ids=true"'
            collections = (requests.get(collectionURL, headers=headers)).json()
            for collection in collections:

            #                 "http://localhost:8089/repositories/2/resource_descriptions/577.xml?include_unpublished=false&include_daos=true&numbered_cs=true&print_pdf=false&ead3=false" //
            # --output ead.xml

                finding_aid_URL = baseURL + result["uri"] + "/resources/" + str(collection) + "?resolve[]=[record_types, to_resolve]"
                finding_aid = (requests.get(finding_aid_URL, headers=headers)).json()

                # if finding_aid["title"] == "Wayward Family papers":
                if finding_aid["ead_id"]:
                    eadURL = baseURL + result["uri"] + "/resource_descriptions/" + finding_aid["ead_id"] + "?include_unpublished=false&include_daos=true&numbered_cs=true&print_pdf=false&ead3=false"
                    ead = (requests.get(eadURL, headers=headers)).json()
                    x = 23
                # #     print(finding_aid["title"])
                #     notes = finding_aid["notes"]
                # #     for note in notes:
                # #         subnote = note["subnotes"]
                # #         for anote in subnote:
                # #             print(anote["content"])

            # {'lock_version': 6, 
            # 'title': 'Wayward Family papers', 
            # 'publish': True, 
            # 'restrictions': False, 
            # 'ead_id': 'mss1776.xml', 
            # 'ead_location': 'http:library.carpediem.edu/ynhsc/mss1776.xml', 
            # 'finding_aid_title': 'Guide to the Wayward family papers <num>YNHSC.MSS.1776</num>', 
            # 'finding_aid_filing_title': 'Wayward family papers', 
            # 'finding_aid_date': '2013', 
            # 'finding_aid_language_note': 'English', 
            # 'created_by': 'admin', 
            # 'last_modified_by': 'jdcrouch', 
            # 'create_time': '2016-08-23T21:04:43Z', 
            # 'system_mtime': '2021-11-23T18:43:10Z', 
            # 'user_mtime': '2020-01-23T22:59:54Z', 
            # 'suppressed': False, 
            # 'is_slug_auto': False, 
            # 'id_0': 'YNHSC.MSS.1776', 
            # 'level': 'collection', 
            # 'finding_aid_description_rules': 'dacs', 
            # 'finding_aid_language': 'eng', 
            # 'finding_aid_script': 'Latn', 
            # 'finding_aid_status': 'unprocessed', 
            # 'jsonmodel_type': 'resource', 
            # 'external_ids': [], 
            # 'subjects': [{'ref': '/subjects/1'}, {'ref': '/subjects/2'}, {'ref': '/subjects/3'}, {'ref': '/subjects/4'}], 
            # 'linked_events': [], 
            # 'extents': [{'lock_version': 0, 'number': '2.0', 'container_summary': '2 record cartons', 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'portion': 'whole', 'extent_type': 'linear_feet', 'jsonmodel_type': 'extent'}], 
            # 'lang_materials': [{'lock_version': 0, 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'jsonmodel_type': 'lang_material', 'notes': [], 'language_and_script': {'lock_version': 0, 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'language': 'eng', 'jsonmodel_type': 'language_and_script'}}, {'lock_version': 0, 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'jsonmodel_type': 'lang_material', 'notes': [{'jsonmodel_type': 'note_langmaterial', 'persistent_id': 'fa17b095d3467baeaf88c5c981d506db', 'type': 'langmaterial', 'content': ['English'], 'publish': True}]}, {'lock_version': 0, 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'jsonmodel_type': 'lang_material', 'notes': [{'jsonmodel_type': 'note_langmaterial', 'persistent_id': 'aspace_31a3b463224b7136adf96568d5f753d3', 'type': 'langmaterial', 'content': ['Collection materials are all in English.'], 'publish': True}]}], 
            # 'dates': [{'lock_version': 0, 'expression': '1847-1963', 'begin': '1847', 'end': '1963', 'created_by': 'jdcrouch', 'last_modified_by': 'jdcrouch', 'create_time': '2020-01-23T22:59:54Z', 'system_mtime': '2020-01-23T22:59:54Z', 'user_mtime': '2020-01-23T22:59:54Z', 'date_type': 'inclusive', 'label': 'creation', 'jsonmodel_type': 'date'}], 
            # 'external_documents': [], 
            # 'rights_statements': [], 
            # 'linked_agents': [{'role': 'creator', 'terms': [], 'ref': '/agents/people/2'}, {'role': 'creator', 'terms': [], 'ref': '/agents/families/1'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/2'}, {'role': 'subject', 'terms': [], 'ref': '/agents/families/1'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/3'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/4'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/5'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/6'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/7'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/8'}, {'role': 'subject', 'terms': [], 'ref': '/agents/people/71'}], 
            # 'revision_statements': [], 
            # 'instances': [], 
            # 'deaccessions': [], 
            # 'related_accessions': [], 
            # 'classifications': [{'ref': '/repositories/2/classifications/3'}], 
            # 'notes': [{'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_8ad18fac03f5ad568e471b2f87607c3a', 'label': 'Scope and Contents note', 'type': 'scopecontent', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'The Wayward family papers includes material from several Wayward descedents living in the 19th and 20th centuries, and was collected by variou family members. Document types in the collection include correspondence, diaries, clippings, posters and audio tapes about the Wayward family and their various activities.\n\n See the scope and content note for each series for more details about the collection contents.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_16a847d2b72a736ac9bf9a4a65329e8c', 'label': 'Family History', 'type': 'bioghist', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'The Wayward family emigrated from England with the original settlers of the fertile Lush River valley in Massachusetts. Makepeace and Constance Wayward, along with five children, were among the founders of City on a Hill when they were expelled from the Massachusetts Bay Colony in 1657 for unorthodox religious practices.\n\n Significant family members represented in the collection include Asa Wellspring Wayward, Sarah Wayward Lewis, Grover Allen Wayward, and Theresa Wayward Auchincloss, the creator of the collection.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_e1cea27fbe64ad9667e8d7f5f489476c', 'label': 'Arrangement note', 'type': 'arrangement', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'Arranged in four series: 1. Asa Wellspring diaries. 2. Sarah Wayward Lewis materials. 3. Grover Allen Wayward OFF records. 4. Theresa Wayward Auchinclos materials.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_bcd7f266ade147b53110deafc5953b8e', 'label': 'Immediate Source of Acquisition note', 'type': 'acqinfo', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'Donated in 1986 by Elspeth Smithie Bourgeois, a graduate of Carpe Diem University.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_70af99af9bb1012f4ba5d1d950a14327', 'label': 'Custodial History note', 'type': 'custodhist', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': "When Theresa Auchincloss died in 1963, the collection was bequeathed to her grandson George Van Buskirk Smithie. Smithie, at the time interested in his family's distinguished history, found himself in dire financial straints by the mid-1960s and apparently sold some of the earliest materials in the collection to a private collector. Some of this material may constitute a 1991 donation of early Wayward family material to the Pittsfield Athenaeum, but the provenance of that material is unclear. The whereabouts of other material sold by Smithie, if there was addiitonal materials, is unknown. Smithie died of mysterious causes in Boston in 1975, at which time the remaining Wayward family material came into the possession of his sister, Elspeth Smithie Bourgeois, an alumna of Carpe Diem University, who donated the collection in 1986.", 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_2626474ebf63300ab1fbdc02665690c8', 'label': 'Processing Information note', 'type': 'processinfo', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'The collection was inventoried upon accession in 1986, but languished in the Your Name Here Special Collections unprocessed backlog until 2006, when an intern from the Simmons College graduate program processed it. This was done as part of a concerted effort to provide access to the backlog. The 19th century material was refoldered and standard preservation measures were taken. Since several of the letters were deteriorating, all were placed in mylar sleeves to facilitate future use by researchers without further damaging them. The remainder of the collection was processed according to the repository’s basic-level processing guidelines: materials were refoldered only when original folders were deteriorating, arrangement work within individual folders was not done, and fasteners were removed only if visibly rusting. Everything was then arranged alphabetically by type of material.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_13c8b6d93460f98be49273116576695b', 'label': 'Appraisal note', 'type': 'appraisal', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'The collection has been appraised by Ernesto Proffitt and Daughters, who notes the primary value of the collection, historical and thus monetary, resides in the 19th century materials diaries of Asa Wellspring Wayward and the journals and correspondence on Sarah Wayward Lewis.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_7c47852ab54a7b2cbf34c5ce29953866', 'label': 'Related Archival Materials note', 'type': 'relatedmaterial', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'Other additional Wayward family papers are in the custody of the Pittsfield Athenaeum. Those materials may have been part of the collection housed in YNHSC at one time but were possibly sold to the Pittsfield Athenaeum in the mid-1960s by George VAn Buskirk Smithie, a prior owner of the Wayward family papers now in the custody of Carpe Diem University.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_88eb50378651d2cc1253e4b06326308d', 'label': 'Conditions Governing Access', 'type': 'accessrestrict', 'rights_restriction': {'local_access_restriction_type': []}, 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'The collection is available for research.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_34fefef0069244364ba72fd7146a31f0', 'label': 'IP Rights', 'type': 'userestrict', 'rights_restriction': {'local_access_restriction_type': []}, 'subnotes': [{'jsonmodel_type': 'note_text', 'content': 'Intellectual property rights have not been transferred to YNHSC; however, the IP rights for a many of the collection materials have expired and passed to the public domain.', 'publish': True}], 'publish': True}, {'jsonmodel_type': 'note_multipart', 'persistent_id': 'aspace_10f7eb371f3a5fe997c5553012771988', 'label': 'Preferred Citation note', 'type': 'prefercite', 'subnotes': [{'jsonmodel_type': 'note_text', 'content': '[Item title / description; Box "n" / Folder "n"]. Wayward Family Papers (MSS 1776). Your Name Here Special Collections. Carpe Diem University.', 'publish': True}], 'publish': True}], 
            # 'metadata_rights_declarations': [], 
            # 'uri': '/repositories/2/resources/1', 
            # 'repository': {'ref': '/repositories/2'}, 
            # 'tree': {'ref': '/repositories/2/resources/1/tree'}}

            # print ("Code " + result["repo_code"])
            # for item in result.items():
            #     print(item)

        return response

    def Search(searchTerm):

        client = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}], http_auth=(settings.ES_USER, settings.ES_PASSWORD))

        q = Q("multi_match", query=searchTerm, fields=['title', 'content'])
        s = Search(using=client, index="nafan").query(q)
        # s = Search(using=client, index="nafan").query("match", content=searchTerm)

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

            response = {"finding_aid_id": hit["_source"].id, "repository_type": hit["_source"].type,"repository": hit["_source"].repository, "title": hit["_source"].title, "content": hit["_source"].content, "source": hit["_source"].source}
            hits.append(response)
        
        return hits

class AidSupplementForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = ['ark', 'repository_link', 'snac', 'wiki']
        
        widgets = {
            'ark': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository_link': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'snac': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'wiki': forms.TextInput(attrs={'class': 'form-control large_field'}),
        }

    def __init__(self, *args, **kwargs): 
        super(AidSupplementForm, self).__init__(*args, **kwargs)  

class AidProfile(models.Model):
    repository_id = models.IntegerField(default=1, blank=True, null=True)
    governing_access = models.TextField(blank=True)
    rights = models.TextField(blank=True)
    creative_commons = models.CharField(max_length=32, blank=True)

    def GetAidProfileByID(id):
        return AidProfile.objects.get(repository_id=id)

    def Exists(id):
        return AidProfile.objects.filter(repository_id=id).exists()

class AidProfileForm(ModelForm):
    class Meta:
        model = AidProfile
        fields = '__all__'
        
        widgets = {
            'governing_access': forms.Textarea(attrs={'class': 'form-control  large_field'}),
            'rights': forms.Textarea(attrs={'class': 'form-control  large_field'}),
            'creative_commons': forms.Select(choices=CCS),
        }

    def __init__(self, *args, **kwargs): 
        super(AidProfileForm, self).__init__(*args, **kwargs)  

class HarvestProfile(models.Model):
    repository_id = models.IntegerField(default=1, blank=True, null=True)
    harvest_name = models.CharField(max_length=255, blank=True)
    harvest_location = models.CharField(max_length=255, blank=True)
    harvest_type = models.CharField(max_length=255, blank=True)
    default_format = models.CharField(max_length=255, blank=True)
    harvest_day = models.CharField(max_length=10, blank=True)
    harvest_time = models.CharField(max_length=10, blank=True)

    def GetHarvestProfiles(id):
        return HarvestProfile.objects.filter(repository_id=id)

    def Exists(id):
        return HarvestProfile.objects.filter(repository_id=id).exists()

class HarvestProfileForm(ModelForm):
    class Meta:
        model = HarvestProfile
        fields = '__all__'
        
        widgets = {
            'harvest_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'harvest_location': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'harvest_type': forms.Select(choices=HARVEST_TYPES),
            'default_format': forms.Select(choices=FILE_TYPES),
            'harvest_day': forms.Select(choices=DAYS),
            'harvest_time': forms.Select(choices=HOURS),
        }

    def __init__(self, *args, **kwargs): 
        super(HarvestProfileForm, self).__init__(*args, **kwargs)  

class DacsAidForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = '__all__'
        
        widgets = {
            'repository': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'ark': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'reference_code': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'name_and_location': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'title': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'date': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'extent': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'creator': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'scope_and_content': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'governing_access': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'languages': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'rights': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'active': forms.BooleanField(),
            'repository_link': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'snac': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'wiki': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'digital_link': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'revision_notes': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'creative_commons': forms.Select(choices=CCS),
        }

    def __init__(self, *args, **kwargs): 
        super(DacsAidForm, self).__init__(*args, **kwargs)                       
        self.fields['repository'].disabled = True

class EADAidForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = '__all__'
        
        widgets = {
            'aid_type': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'name_and_location': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'title': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'scope_and_content': forms.Textarea(attrs={'class': 'form-control large_field'}),
            'active': forms.BooleanField(),
        }

    def __init__(self, *args, **kwargs): 
        super(EADAidForm, self).__init__(*args, **kwargs)                       
        self.fields['aid_type'].disabled = True
        self.fields['repository'].disabled = True
        self.fields['title'].disabled = True
        self.fields['scope_and_content'].disabled = True

class MARCAidForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = '__all__'
        
        widgets = {
            'aid_type': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'name_and_location': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'title': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'scope_and_content': forms.Textarea(attrs={'class': 'form-control large_field'}),
            'active': forms.BooleanField(),
        }

    def __init__(self, *args, **kwargs): 
        super(MARCAidForm, self).__init__(*args, **kwargs)                       
        self.fields['aid_type'].disabled = True
        self.fields['repository'].disabled = True
        self.fields['title'].disabled = True
        self.fields['scope_and_content'].disabled = True

class PDFAidForm(forms.Form):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control large_field'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control large_field'}))
    file = forms.FileField()

class DacsAidForm(ModelForm):
    class Meta:
        model = FindingAid
        fields = '__all__'
        
        widgets = {
            'repository': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'ark': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'reference_code': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'name_and_location': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'title': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'date': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'extent': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'creator': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'scope_and_content': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'governing_access': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'languages': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'rights': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'active': forms.BooleanField(),
            'repository_link': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'snac': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'wiki': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'digital_link': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'revision_notes': forms.Textarea(attrs={'class': 'form-control', 'rows':4, 'cols':15}),
            'creative_commons': forms.Select(choices=CCS),
        }

    def __init__(self, *args, **kwargs): 
        super(DacsAidForm, self).__init__(*args, **kwargs)                       
        self.fields['repository'].disabled = True
        
class HarvestFilesForm(forms.Form):
    directory = forms.CharField(max_length=255)
    format = forms.CharField(max_length=255)

class Schema(models.Model):

    def handle_microdata_upload(filepath):

        response = "OK"
        # es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

        try:

            # Opening the html file
            HTMLFile = open(filepath, "r")
  
            # Reading the file
            html_doc = HTMLFile.read()

            # Parse the html file
            soup = BeautifulSoup(html_doc, 'html.parser')

            # There is no way to parse this unless "Conditions Governing Access" is always there
            # <span class="label">Conditions Governing Access</span>
            # <span class="val">Please check with the Theatre and Performance enquiry team regarding access arrangements before making an appointment
            # to listen to this item.</span><br/>

            for item in soup.findAll("div"):
                itemtype = item.get("itemtype").split('/')[-1]

            additionalType = soup.find("link", itemprop="additionalType").attrs['href'].split('/')[-1]

            name = soup.find("h1", itemprop="name").next
            holdingArchive = soup.find("span", itemprop="holdingArchive").next
            identifier = soup.find("span", itemprop="identifier").next
            isPartOf = soup.find("a", itemprop="isPartOf").next
            dateCreated = soup.find("span", itemprop="dateCreated").next
            url = soup.find("a", itemprop="url").next
            about = soup.find("span", itemprop="about").next
            inLanguage = soup.find("span", itemprop="inLanguage").next
            description = soup.find("span", itemprop="description").next
            playerType = soup.find("span", itemprop="playerType").next

            print (identifier.next)

            # Build whatever seems reasonable to index.

                            # record = {'snac_id': snac_list[link_count], 'url': url, 'content': text}
                            # json_record = json.dumps(record)

                            # try:
                            #     outcome = es.index(index='snac', doc_type='_doc', body=json_record)
                            # except Exception as ex:
                            #     print('Error in indexing data')
                            #     print(str(ex))

        except Exception as e:
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def handle_rdf_upload(filepath):

        response = "OK"
        # es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

        try:

            # Opening the html file
            HTMLFile = open(filepath, "r")
  
            # Reading the file
            html_doc = HTMLFile.read()

            # Parse the html file
            soup = BeautifulSoup(html_doc, 'html.parser')

        # <div  vocab="https://schema.org/" typeof="ArchiveComponent AudioObject">
        # <h1 property="name">Sound Recording of Lines from My Grandafther's Forehead (Radio)</h1>
        # <span class="val"><a property="holdingArchive" href="https://archiveshub.jisc.ac.uk/search/locations/eae30daa-1bf9-33d9-bf1c-7aeb220d2e76">V&A Theatre and Performance</a></span><br/>
        # <span class="val" property="holdingArchive">V&A Theatre and Performance Collections</span><br/>
        # <span class="val" property="identifier">GB 71 THM/407/8/3</span><br/>
        # <span class="val"><a property="isPartOf" href="https://archiveshub.jisc.ac.uk/data/gb71-thm/407/thm/407/8">THM/407/8 - Audio Recordings</a></span><br/>
        # <span class="val" property="dateCreated">1971-1972</span><br/>
        # <span class="val"><a property="url" href="https://archiveshub.jisc.ac.uk/data/gb71-thm/407/thm/407/8/3">https://archiveshub.jisc.ac.uk/data/gb71-thm/407/thm/407/8/3</a></span><br/>
        # <span class="val" property="about">Comedy</span><br/>
        # <span class="val" property="inLanguage" content="EN">English</span><br/>
        # <span class="val" property="description">Sound recording of the first radio broadcast of Lines from My Grandfather's Forehead by Ronnie Barker and others.
        # Duration: max 90 mins.</span><br/>
        # <span class="val" property="playerType">Audio Cassette</span><br/>

            for item in soup.findAll("div"):
                itemtype = item.get("typeof").split(' ')[-1]
            holdingArchiveLink = soup.find("a", property="holdingArchive").attrs['href']

            name = soup.find("h1", property="name").next
            holdingArchive = soup.find("span", property="holdingArchive").next
            identifier = soup.find("span", property="identifier").next
            isPartOf = soup.find("a", property="isPartOf").next
            dateCreated = soup.find("span", property="dateCreated").next
            url = soup.find("a", property="url").next
            about = soup.find("span", property="about").next
            inLanguage = soup.find("span", property="inLanguage").next
            description = soup.find("span", property="description").next
            playerType = soup.find("span", property="playerType").next

            print (identifier.next)

            # Build whatever seems reasonable to index.

                            # record = {'snac_id': snac_list[link_count], 'url': url, 'content': text}
                            # json_record = json.dumps(record)

                            # try:
                            #     outcome = es.index(index='snac', doc_type='_doc', body=json_record)
                            # except Exception as ex:
                            #     print('Error in indexing data')
                            #     print(str(ex))

        except Exception as e:
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

    def handle_jsonLD_upload(filepath):

        response = "OK"
        # es = Elasticsearch([{'host': settings.ES_HOST, 'port': settings.ES_PORT}])

        try:

            # Opening the html file
            HTMLFile = open(filepath, "r")
  
            # Reading the file
            html_doc = HTMLFile.read()

            # Parse the html file
            soup = BeautifulSoup(html_doc, 'html.parser')



            dict = json.loads("".join(soup.find("script", {"type":"application/ld+json"}).contents))

            context = dict['@context']
            name = dict['name']

            # holdingArchive = soup.find("span", property="holdingArchive").next
            # identifier = soup.find("span", property="identifier").next
            # isPartOf = soup.find("a", property="isPartOf").next
            # dateCreated = soup.find("span", property="dateCreated").next
            # url = soup.find("a", property="url").next
            # about = soup.find("span", property="about").next
            # inLanguage = soup.find("span", property="inLanguage").next
            # description = soup.find("span", property="description").next
            # playerType = soup.find("span", property="playerType").next
            
            a = 1
            # Build whatever seems reasonable to index.

                            # record = {'snac_id': snac_list[link_count], 'url': url, 'content': text}
                            # json_record = json.dumps(record)

                            # try:
                            #     outcome = es.index(index='snac', doc_type='_doc', body=json_record)
                            # except Exception as ex:
                            #     print('Error in indexing data')
                            #     print(str(ex))

        except Exception as e:
            response = "Unable to process the " + filepath + " file " + str(e)

        return response

class Word(models.Model):
    # textract can be used for Word files (and other types)
    # https://textract.readthedocs.io/en/stable/
    pass

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  cleantext = cleantext.replace("\r","")
  cleantext = cleantext.replace("\t","")
  cleantext = cleantext.replace("\n","")
  cleantext = cleantext.replace("'\n',","")
  cleantext = cleantext.replace("'\\n'"," ")

  return cleantext

def strip_p(text):
  cleantext = text.replace("<p>","")
  cleantext = text.replace("</p>","")

  return cleantext

def String_or_p_tag(soup, tag):

    # Need to consider multiple <p> tags within a tag

    response = ""
    element = soup.find(tag)
    if element:

        div_bs4 = element.find('head')
                
        # # delete the child element
        if div_bs4:
            div_bs4.clear()

        response = element.string

        # If the return_value is blank, see if they put in a <p> entries
        if not response:
            response = str(element)

        response = element.get_text()

    if not response:
        response = ""

    return response

def String_no_p_tag(soup, tag):

    # Need to consider multiple <p> tags within a tag

    response = ""
    element = soup.find(tag)
    if element:
        response = element.string

        # If the return_value is blank, see if they put in a <p> entries
        if not response:
            response = element.p.string

    if not response:
        response = ""

    return response

