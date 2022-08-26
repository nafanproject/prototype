import csv

# This procedure takes the sorted repodata file and creates two files
# One file contains all the non-duplicate entries, the other the duplicated entries
# Duplicate in this case is considered true if the name, city, and state match
def finddups():

    try:
        dedupfile = csv.writer(open('data/DeDupFile.csv', 'w', newline='', encoding="utf8"))
        writededupheader(dedupfile)
        dupfile = csv.writer(open('data/DupFile.csv', 'w', newline='', encoding="utf8"))
        writedupheader(dupfile)

        with open('data/RepoDataSorted.csv', newline='', encoding="utf8") as csvfile:

            name = ""
            city = ""
            state = ""
            count = 0
            copyRow = []

            reader = csv.DictReader(csvfile)
            for row in reader:
                checkName = str.strip(row['repository_name_unauthorized'])
                checkCity = str.strip(row['st_city'])
                if name == checkName and city == checkCity and state == row['state']:
                    writeduplicate(dupfile,row)
                    if len(copyRow) > 0:
                        writededuplicate(dedupfile, copyRow, row['street_address_1'])
                    copyRow.clear()
                    count = count + 1
                else:
                    if len(copyRow) > 0:
                        writededuplicate(dedupfile, copyRow, "")
                    copyRow = row

                # print(row['repository_name_unauthorized'], row['state'])
                name = checkName
                city = checkCity
                state = row['state']


            print(count)
    except Exception as e:
        print(e)

# Write the column headers for the de-duplicate file
def writededupheader(dupfile):

    dupfile.writerow(['id', 'repository_name_unauthorized', 'name_notes', 'parent_org_unauthorized', 'repository_name_authorized', \
                      'repository_identifier_authorized', 'repository_type', 'location_type', 'street_address_1', 'street_address_2', 'po_box', \
                      'st_city', 'st_zip_code_5_numbers', 'st_zip_code_4_following_numbers', 'street_address_county', 'state', \
                      'url', 'latitude', 'longitude', 'language_of_entry', 'date_entry_recorded', 'entry_recorded_by', 'source_of_repository_data', \
                      'url_of_source_of_repository_data', 'notes', 'geocode_confidence'])

# Write the column headers for the duplicate file
def writedupheader(dupfile):

    dupfile.writerow(['id', 'repository_name_unauthorized', 'name_notes', 'parent_org_unauthorized', 'repository_name_authorized', \
                      'repository_identifier_authorized', 'repository_type', 'location_type', 'street_address_1', 'street_address_2', \
                      'st_city', 'st_zip_code_5_numbers', 'st_zip_code_4_following_numbers', 'street_address_county', 'state', \
                      'url', 'latitude', 'longitude', 'language_of_entry', 'date_entry_recorded', 'entry_recorded_by', 'source_of_repository_data', \
                      'url_of_source_of_repository_data', 'notes', 'geocode_confidence'])

# Write the de-duplicate file
def writededuplicate(dupfile, row, poBox):

    id =  row['id']
    repository_name_unauthorized =  row['repository_name_unauthorized']
    name_notes =  row['name_notes']
    parent_org_unauthorized =  row['parent_org_unauthorized']
    repository_name_authorized =  row['repository_name_authorized']
    repository_identifier_authorized =  row['repository_identifier_authorized']
    repository_type =  row['repository_type']
    location_type =  row['location_type']
    street_address_1 =  row['street_address_1']
    street_address_2 =  row['street_address_2']
    st_city =  row['st_city']
    st_zip_code_5_numbers =  row['st_zip_code_5_numbers']
    st_zip_code_4_following_numbers =  row['st_zip_code_4_following_numbers']
    street_address_county =  row['street_address_county']
    state =  row['state']
    url =  row['url']
    latitude =  row['latitude']
    longitude =  row['longitude']
    language_of_entry =  row['language_of_entry']
    date_entry_recorded =  row['date_entry_recorded']
    entry_recorded_by =  row['entry_recorded_by']
    source_of_repository_data =  row['source_of_repository_data']
    url_of_source_of_repository_data =  row['url_of_source_of_repository_data']
    notes =  row['notes']
    geocode_confidence =  row['geocode_confidence']

    # The addresses are not consistent


    if len(poBox) > 0:
        # First see if the Street Address and PO Box are switched
        if 'Box' in street_address_1:
            temp = poBox
            poBox = street_address_1
            street_address_1 = temp

        # Sometimes the poBox is in street_address_2
        if poBox == street_address_1:
            poBox = street_address_2

    dupfile.writerow([id, repository_name_unauthorized, name_notes, parent_org_unauthorized, repository_name_authorized, \
                      repository_identifier_authorized, repository_type, location_type, street_address_1, street_address_2, poBox,\
                      st_city, st_zip_code_5_numbers, st_zip_code_4_following_numbers, street_address_county, state, \
                      url, latitude, longitude, language_of_entry, date_entry_recorded, entry_recorded_by, source_of_repository_data, \
                      url_of_source_of_repository_data, notes, geocode_confidence])

# Write the duplicate file
def writeduplicate(dupfile, row):

    id =  row['id']
    repository_name_unauthorized =  row['repository_name_unauthorized']
    name_notes =  row['name_notes']
    parent_org_unauthorized =  row['parent_org_unauthorized']
    repository_name_authorized =  row['repository_name_authorized']
    repository_identifier_authorized =  row['repository_identifier_authorized']
    repository_type =  row['repository_type']
    location_type =  row['location_type']
    street_address_1 =  row['street_address_1']
    street_address_2 =  row['street_address_2']
    st_city =  row['st_city']
    st_zip_code_5_numbers =  row['st_zip_code_5_numbers']
    st_zip_code_4_following_numbers =  row['st_zip_code_4_following_numbers']
    street_address_county =  row['street_address_county']
    state =  row['state']
    url =  row['url']
    latitude =  row['latitude']
    longitude =  row['longitude']
    language_of_entry =  row['language_of_entry']
    date_entry_recorded =  row['date_entry_recorded']
    entry_recorded_by =  row['entry_recorded_by']
    source_of_repository_data =  row['source_of_repository_data']
    url_of_source_of_repository_data =  row['url_of_source_of_repository_data']
    notes =  row['notes']
    geocode_confidence =  row['geocode_confidence']

    dupfile.writerow([id, repository_name_unauthorized, name_notes, parent_org_unauthorized, repository_name_authorized, \
                      repository_identifier_authorized, repository_type, location_type, street_address_1, street_address_2, \
                      st_city, st_zip_code_5_numbers, st_zip_code_4_following_numbers, street_address_county, state, \
                      url, latitude, longitude, language_of_entry, date_entry_recorded, entry_recorded_by, source_of_repository_data, \
                      url_of_source_of_repository_data, notes, geocode_confidence])

