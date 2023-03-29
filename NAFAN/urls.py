from django.urls import path, include
from NAFAN import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path("index", views.home, name="home"),
    path("nafanlogin/", views.NAFANLogin, name="NAFANLogin"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("help/<str:topic>", views.help, name="help"),    
    path("search_results/", views.search_results, name="search_results"),
    path("joinus/", views.joinus, name="joinus"),
    path("clear_join/<int:id>", views.clear_join, name="clear_join"),
    path('Repository_Info/<str:repository_name>', views.Repository_Info, name="Repository_Info" ),
    path('Browse_Repository/<int:id>', views.Browse_Repository, name="Browse_Repository" ),
    path('Browse_Repository_Entries/<int:id>', views.Browse_Repository_Entries, name="Browse_Repository_Entries" ),
    path('view_aid_preliminary/<int:id>', views.view_aid_preliminary, name="view_aid_preliminary" ),
    path('view_aid_public/<int:id>', views.view_aid_public, name="view_aid_public" ),
    path('accounts/', include('django.contrib.auth.urls')),
    path("contributor/", views.contributor, name="contributor"),
    path("contributor_admin/", views.contributor_admin, name="contributor_admin"),
    path("researcher/", views.researcher, name="researcher"),
    path('logout/', views.NAFANlogout, name='logout'),

    path("Admin/nafan_admin/", views.nafan_admin, name="nafan_admin"),
    path('Admin/upload_repositories/', views.upload_repositories, name='upload_repositories'),
    path("Admin/user_repositories/", views.user_repositories, name="user_repositories"),
    path("Admin/repositories/", views.repositories, name="repositories"),
    path("Admin/audit/", views.audit, name="audit"),
    path("Admin/tracelog/", views.tracelog, name="tracelog"),
    path('ajax/add_user_repository/', views.add_user_repository, name='add_user_repository'),
    path('ajax/remove_user_repository/', views.remove_user_repository, name='remove_user_repository'),

    path("Users/users", views.users, name="users"),    
    path("Users/create_user", views.create_user, name="create_user"),    
    path('Users/update_user/<int:id>', views.update_user, name="update_user" ),
    path('Users/delete_user/<int:id>', views.delete_user, name="delete_user" ),
    path('Users/user_repositories/<int:id>', views.user_repositories, name="user_repositories" ),

    path("Repositories/repositories", views.repositories, name="repositories"),    
    path('Repositories/update_repository/<int:id>', views.update_repository, name="update_repository" ),
    path("Repositories/create_repository", views.create_repository, name="create_repository"),    
    path('Repositories/delete_repository/<int:id>', views.delete_repository, name="delete_repository" ),
    path('Repositories/report_repository/<int:id>', views.report_repository, name="report_repository" ),
    path("Repositories/export_repositories", views.export_repositories, name="export_repositories"),    
    path('ajax/get_repository_search/', views.get_repository_search, name='get_repository_search'),

    path("FindingAids/finding_aids/<int:id>", views.finding_aids, name="finding_aids"),    
    path('FindingAids/view_aid/<int:id>', views.view_aid, name="view_aid" ),
    path('FindingAids/update_aid/<int:id>', views.update_aid, name="update_aid" ),
    path('FindingAids/delete_aid/<int:id>', views.delete_aid, name="delete_aid" ),
    path("FindingAids/create_dacs", views.create_dacs, name="create_dacs"),    
    path("FindingAids/create_pdf", views.create_pdf, name="create_pdf"),    
    path("FindingAids/edit_dacs/<int:id>", views.edit_dacs, name="edit_dacs"),    
    path('FindingAids/ingest_ead', views.ingest_ead, name="ingest_ead" ),
    path("FindingAids/edit_ead/<int:id>", views.edit_ead, name="edit_ead"),    
    path("FindingAids/edit_pdf/<int:id>", views.edit_pdf, name="edit_pdf"),    
    path('FindingAids/ingest_pdf/<int:id>', views.ingest_pdf, name="ingest_pdf" ),
    path('FindingAids/ingest_marc', views.ingest_marc, name="ingest_marc" ),
    path("FindingAids/edit_marc/<int:id>", views.edit_marc, name="edit_marc"),    
    path('FindingAids/ingest_schema', views.ingest_schema, name="ingest_schema" ),
    path("FindingAids/new_aid", views.new_aid, name="new_aid"),    
    path("FindingAids/harvest_aids", views.harvest_aids, name="harvest_aids"),    
    path("FindingAids/create_harvest_profile", views.create_harvest_profile, name="create_harvest_profile"),    
    path("FindingAids/edit_harvest_profile/<int:id>", views.edit_harvest_profile, name="edit_harvest_profile"),    
    path("FindingAids/delete_harvest_profile/<int:id>", views.delete_harvest_profile, name="delete_harvest_profile"),    
    path("FindingAids/harvest_profiles", views.harvest_profiles, name="harvest_profiles"),    
    path("FindingAids/aid_profile", views.aid_profile, name="aid_profile"),    
    path('FindingAids/delete_subject_header/<int:id>', views.delete_subject_header, name="delete_subject_header" ),

    path('ajax/set_finding_aid_format', views.set_finding_aid_format, name="set_finding_aid_format"),    
    path('ajax/add_subject_header/', views.add_subject_header, name='add_subject_header'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
