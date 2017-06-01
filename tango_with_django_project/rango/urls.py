from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^about', views.about, name='about'),
    url(r'^category/(?<category_name_slug>[\w\-]+)/$',
        views.show_category, name='show_category'),
    url(r'^$', views.index, name='index'),
]