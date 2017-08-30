"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from app01 import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # url(r'^user.html/$', views.test),
    url(r'thumbs/$',views.thumbs),
    url(r'comment/$',views.comment),
    url(r'comment-(?P<nid>\d+).html/$',views.comment),
    url(r'^manage/', include("background.urls")),


    url(r'^$', views.index),
    url(r'^all/(?P<type_id>\d+)', views.index),


    url(r'^login/', views.login),
    url(r'^login1/', views.login1),
    url(r'^logout/', views.logout),
    url(r'^register/', views.register),
    url(r'^application/', views.application),
    # url(r'^avatar/', views.avatar),


    url(r'^check_code/', views.check_code),

    url(r'^(?P<user>\w+)/$', views.user_blog),
    url(r'^(?P<user>\w+)/(?P<articleid>\d+)$', views.user_article),
    url(r'^(?P<user>\w+)/tag/(?P<tid>\w+).html', views.tag_blog),
    url(r'^(?P<user>\w+)/category/(?P<tid>\w+).html', views.tag_blog),
    url(r'^(?P<user>\w+)/datetime/(?P<year>\d+)-(?P<mouth>\d+).html', views.tag_blog),

]
