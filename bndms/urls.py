"""
URL configuration for bndms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

import front_end.views as fe
import api.views as api
import bndms.settings as settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.root),
    path("api/reports", api.reports),
    path("", fe.home, name="home-page"),
    path("login/", fe.login, name="login-page"),
    path("logout/", LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name="logout-page"),
    path("register/", fe.register, name="register-page"),
    path("map/", fe.map, name="map-page"),
    path("reports/", fe.reports, name="reports-page"),
    path("create_report/", fe.create_report, name="create_report-page"),
    path("create_task/<str:pk>", fe.create_task, name="create_task-page"),
    path("reports/<str:pk>/tasks", fe.tasks, name='report_tasks-page'),
    path("see_tasks/<str:pk>", fe.assigned_tasks, name='assigned_task-page'),
    path("update_task_status/<str:pk>", fe.update_task_status, name='update_task_status-page'),
    path("delete_task/<uuid:pk>", fe.delete_task, name='delete_task-page'),
    path("delete_report/<uuid:pk>", fe.delete_report, name='delete_report-page'),
    path("update_task/<uuid:pk>", fe.update_task, name="update_task-page"),
    path("update_report/<uuid:pk>", fe.update_report, name="update_report-page"),
    path("create_news/", fe.create_news, name="create_news-page"),
    path("news/", fe.news_list, name="news-page"),
    path("update_news/<uuid:pk>", fe.update_news, name="update_news-page"),
    path("delete_news/<uuid:pk>", fe.delete_news, name="delete_news-page")
]
