from django.urls import path, include
from NAFAN import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url
from .models import UserCreation, UserUpdate
from .models import FindingAidCreation, FindingAidUpdate

urlpatterns = [
    path("", views.home, name="home"),
    path("nafanlogin/", views.NAFANLogin, name="NAFANLogin"),
    path("newToNAFAN/", views.newToNAFAN, name="newToNAFAN"),
    path('accounts/', include('django.contrib.auth.urls')),
    path("contributor/", views.contributor, name="contributor"),
    path("contributor_admin/", views.contributor_admin, name="contributor_admin"),
    path("Admin/nafan_admin/", views.nafan_admin, name="nafan_admin"),
    path("researcher/", views.researcher, name="researcher"),
    path('logout/', views.NAFANlogout, name='logout'),
    path("Admin/tracelog/", views.tracelog, name="tracelog"),
    path("Admin/audit/", views.audit, name="audit"),
    
    # path("Admin/users/", views.users, name="users"),
    # url(r'^Admin/user_new/$', UserCreation.as_view(), name='user_new'),
    # url(r'^Admin/user_edit/(?P<pk>\d+)/$', UserUpdate.as_view(), name='user_edit'),
    # url(r'^Admin/user_delete/(?P<pk>\d+)/$', UserDelete.as_view(), name='user_delete'),

    path('Admin/upload_repositories/', views.upload_repositories, name='upload_institutes'),
    path("Admin/user_repositories/", views.user_repositories, name="user_repositories"),
    path('ajax/add_user_repository/', views.add_user_repository, name='add_user_repository'),
    path("Admin/repositories/", views.repositories, name="repositories"),

    path("Admin/finding_aids/", views.finding_aids, name="finding_aids"),    
    url(r'^Admin/findingaid_new/$', FindingAidCreation.as_view(), name='findingaid_new'),
    url(r'^Admin/findingaid_edit/(?P<pk>\d+)/$', FindingAidUpdate.as_view(), name='findingaid_edit'),

    path("Users/users", views.users, name="users"),    
    path("Users/create_user", views.create_user, name="create_user"),    
    path('Users/update_user/<int:id>', views.update_user, name="update_user" ),
    path('Users/delete_user/<int:id>', views.delete_user, name="delete_user" ),

    path("FindingAids/finding_aids/<int:id>", views.finding_aids, name="finding_aids"),    
    path("FindingAids/create_aid", views.create_aid, name="create_aid"),    
    path('FindingAids/update_aid/<int:id>', views.update_aid, name="update_aid" ),
    path('FindingAids/delete_aid/<int:id>', views.delete_aid, name="delete_aid" ),

    path("Repositories/repositories", views.repositories, name="repositories"),    
    path('Repositories/update_repository/<int:id>', views.update_repository, name="update_repository" ),
    path("Repositories/create_repository", views.create_repository, name="create_repository"),    
    path('Repositories/delete_repository/<int:id>', views.delete_repository, name="delete_repository" ),
]