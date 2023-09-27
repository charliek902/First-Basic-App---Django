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

    path('', views.home, name='home'),
    path('api/search/', views.search, name='search'),
    path('api/parse_excel/', views.parse_excel, name='parse_excel'),
    path('doc/', views.show_documentation, name='documentation'),
    path('<path:undefined_path>/', views.anyOtherRequest, name='any_other_request'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Serve .js files with 'application/javascript' MIME type
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT, 'show_indexes': True, 'mimetype': 'application/javascript'}),
        
        # Add a URL pattern for serving EPREL.css with 'text/css' MIME type
        re_path(r'^static/EPREL\.css$', serve, {'document_root': settings.STATIC_ROOT, 'show_indexes': True, 'mimetype': 'text/css'}),
    ]







