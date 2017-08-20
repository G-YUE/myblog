from django.conf.urls import url
from django.contrib import admin
from background import views

urlpatterns = [
    url(r'^index.html/$', views.manage),
    url(r'^upload_img.html/$', views.upload),
    url(r'^(?P<type>\w+)/$', views.classify),
    url(r'^(?P<type>\w+)/(?P<article_type_id>\d+)-(?P<category_id>\d+)-(?P<tags__nid>\d+).html/$', views.classify),
    url(r'^article/(?P<type>(add)|(edit)).html/$',views.article_add_edit),
    url(r'^article/del.html/$',views.article_del),

    url(r'^category/(?P<type>(add)|(edit)).html/$', views.category_add_edit),
    url(r'^category/del.html/$', views.category_del),

    url(r'^tag/(?P<type>(add)|(edit)).html/$', views.tag_add_edit),
    url(r'^tag/del.html/$', views.tag_del),



]
