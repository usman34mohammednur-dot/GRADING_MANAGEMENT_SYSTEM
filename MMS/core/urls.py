from django.urls import path
from . import views

app_name="core"

urlpatterns = [
    path('', views.home, name="home" ),
    path('about/', views.about, name="about" ),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_access/', views.student_access, name='student_access'),
     path('edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('view_grades/<int:student_id>/', views.view_student_grades, name='view_student_grades'),
    path('teachers_dashboard/', views.teacher_dashboard, name="teacher_dashboard" ),
   
    path('grades/<int:student_id>/', views.add_or_edit_grades, name='submit_grades'),
    path('delete/<int:pk>/', views.delete_admin, name="delete_me"),

    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('logout_stud/', views.logout_student, name='logout_student'),
    path('teacher/edit/<int:pk>/', views.edit_teacher, name='edit_teacher'),
    path('teacher/delete/<int:pk>/', views.delete_teacher, name='delete_teacher'),
    path('register-admin/', views.register_admin, name='register_admin'),
]