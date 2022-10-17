# prototype
NAFAN Prototype Project

This document discusses the more technical aspects of the NAFAN prototype.  Discussion of the operation of the application is contained in the Wiki.


Technical Stack:

The NAFAN prototype is written in Python and uses the Django framework.  The relational database is PostgresSQL and the search engine is Elasticsearch.

The following libraries are used.  These are listed in the requirements.txt file.
- beautifulsoup4
- elasticsearch
- elasticsearch-dsl
- pymarc
- PyPDF2
- requests
- sickle

Database Preparation:

To populate users, there needs to be one user in the NAFAN_nafanuser table with the user_type set to nafan_admin.  Thereafter, that user can set up everything within the application.  One change that has to happen is that the passwords in the database are not encrypted as yet.  Obviously this needs to change for any sort of production environment.

Styling:

The styling is based on bootstrap.
Yes, I know what a css file is and would have been happy to use it rather than put the styling in each page.  Spent a day trying to get it work properly in the deployment server without success and decided it wasn't worth pursuing for a prototype.  Feel free and superior doing it correctly.


EAD Sources:

1. ArchivesGrid - https://researchworks.oclc.org/nafan/source_data/  These are zipped files from the various repositories associated with the Archives 
  grid project
2. EADiva - https://eadiva.com/sampleEAD  These are a set of EAD files that were used to test the file harvest operation
3. Kerouac records at NYPL - This was used to produce the format of the EAD display 
      HTML: https://archives.nypl.org/brg/19191
      EAD: https://nyplorg-data-archives-production.s3.amazonaws.com/uploads/collection/generated_xml/brg19191.xml
4. OAC - The following are EAD files provided that allowed more robust testing of the EAD ingestion.
    1) GLBT Historical Society: "AIDS Legal Referral Panel records"
    * Single-level description
      HTML: https://oac.cdlib.org/findaid/ark:/13030/c8gx4jnt/
      EAD: http://voro.cdlib.org/oac-ead/prime2002/glhs/c8gx4jnt.xml
 
    2) Welga Archive, "Welga Project FIles"
    * Single-level description, with <dao> link at top to digital objects
      HTML: https://oac.cdlib.org/findaid/ark:/13030/c89w0mvx/
      EAD: http://voro.cdlib.org/oac-ead/prime2002/wpfaa/c89w0mvx.xml
 
    3) Go For Broke National Education Center: "Mary Yamamoto Shimizu Collection"
    * Single-level description
    * Includes link to PDF container list
      HTML: https://oac.cdlib.org/findaid/ark:/13030/c8891cg9/
      EAD: http://voro.cdlib.org/oac-ead/prime2002/catorgfb/2016.007_ead.xml
 
    4) African American Museum & Library at Oakland: "Guide to the African American Museum & Library at Oakland Oral History Collection"
    * Multilevel, goes to <c03>
    * Includes <dao> links to digital objects
      HTML: https://oac.cdlib.org/findaid/ark:/13030/c87m0dcs/
      EAD: https://voro.cdlib.org/oac-ead/prime2002/copl/caolaam/00191.xml
 
    5) UCB Environmental Design Archives, "Julia Morgan Records at the University of California Berkeley,"
    * Multilevel, goes to <c03>, detailed EAD encoding at file/item level with mixed content
    * Includes <dao> links
      HTML: https://oac.cdlib.org/findaid/ark:/13030/tf7r29p0df/
      EAD: https://voro.cdlib.org/oac-ead/prime2002/berkeley/ceda/morgangrp.xml
 
    6) UC Berkeley Bancroft Library, "City Lights Bookstore records"
    * Multilevel, goes to <c03>, detailed EAD encoding at file/item level with mixed content
    * Includes <dao> links to digital objects
      HTML: https://oac.cdlib.org/findaid/ark:/13030/kt5489q50w/
      EAD: https://voro.cdlib.org/oac-ead/prime2002/berkeley/bancroft/m72_107_cubanc.xml
 
    7) UC Santa Barbara Library, Special Research Collections: "El Teatro Campesino Archives"
      HTML: https://oac.cdlib.org/findaid/ark:/13030/c8xw4hsw/
      EAD: http://voro.cdlib.org/oac-ead/prime2002/ucsb/spcoll/cusb-cema5.xml

    8) Kitchen Sink example EAD
    * Containing all EAD tag permutations -- which can be used for test and display purposes. 
      HTML: https://github.com/SAA-SDT/EAD2002toEAD3/tree/master/samples/2002

