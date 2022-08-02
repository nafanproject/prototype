# prototype
NAFAN Prototype Project

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

