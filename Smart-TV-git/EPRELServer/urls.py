"""
URL configuration for EPRELServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.urls import path
from .app import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [

    path('', views.displayHomePage, name='home'),
    path('search/', views.searchLibrary, name='searchLibrary'),
    path('api/search/', views.search, name='search'),
    path('TVDataParser/api/parse_excel/', views.parse_excel, name='parse_excel'),
    #path('doc/', views.show_documentation, name='documentation'),
    path('TVDataParser/', views.show_DataAnalytics_page, name='data analytics'),
    path('APIPage/', views.showAPI, name= 'API'),
    path('liveDashboardPage/', views.showLiveDashboardMonthly, name='liveDashboard'),
    path('liveDashboardPage/', views.showLiveDashboardMonthly, name='liveDashboard'),
    path('search/explanation.txt/', views.showExplanation, name= 'explanation'),
    #path('liveDashboardDaily/', views.getDashboardDaily, name='liveDashboard1'),
    #path('liveDashboardParser/', views.getDashboardParsed, name='liveDashboard2'),
    path('api/', views.apiEndpoint, name='apiEndpoint'),
    path('<path:undefined_path>/', views.display404, name='any_other_request'),
]









