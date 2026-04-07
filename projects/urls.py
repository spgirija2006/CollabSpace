from django.urls import path
from . import views

urlpatterns = [
    path('browse/', views.browse_projects, name='browse_projects'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('project/<int:pk>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_pk>/applications/', views.manage_applications, name='manage_applications'),
    path('apply/<int:role_pk>/', views.apply_to_role, name='apply_to_role'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:app_pk>/status/<str:status>/', views.update_application_status, name='update_application_status'),
    path('application/<int:app_pk>/schedule-interview/', views.schedule_interview, name='schedule_interview'),
]