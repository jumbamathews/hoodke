from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns=[
    url(r'^$',views.index,name = 'index'),    
    url(r'^sendemail/$',views.send_email,name = 'send-email'),
    url(r'^create-profile-admin/$',views.create_profile_admin,name = 'create-profile-admin'),
    url(r'^create-hood/$',views.create_hood,name = 'create-hood'),
    url(r'^update-hood/$',views.update_hood,name = 'update-hood'),
    url(r'^my-admin-profile/$',views.my_admin_profile,name = 'my-admin-profile'),
    url(r'^my-user-profile/$',views.my_user_profile,name = 'my-user-profile'),
    url(r'^add-resident/$',views.add_resident,name = 'add-resident'),
    url(r'^delete-hood/$',views.delete_hood,name = 'delete-hood'),
    url(r'^add-facility/$',views.add_facility,name = 'add-facility'),
    url(r'^add-business/$',views.add_business,name = 'add-business'),
    url(r'^delete-resident-profile/$',views.delete_resident_profile,name = 'delete-resident-profile'),
    url(r'^change-password/$',views.change_password,name = 'change-password'),
    url(r'^make-post/$',views.make_post,name = 'make-post'),
    url(r'^residents-list/$',views.residents_list,name = 'residents-list'),
    url(r'^delete-resident/(\d+)',views.delete_resident,name = 'delete-resident'),
    # url(r'^updatedescription/(\d+)',views.update_description,name = 'update-description'),
    url(r'^changeprofilephoto/$',views.change_profile_photo,name = 'change-profile-photo'),
    # url(r'^deleteprofile/$',views.delete_profile,name = 'delete-profile'),
    url(r'^search/$',views.search_business,name = 'search-business'),
    # url(r'^userprofile/(\d+)',views.user_profile,name = 'user-profile'),
    # url(r'^viewproject/(\d+)',views.view_project,name = 'view-project'),
    # url(r'^ajax/rateproject/$', views.rate_project, name='rate-project'),    
    # url(r'^api/profiles/$', views.ProfileList.as_view()),
    # url(r'^api/projects/$', views.ProjectList.as_view()),
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)