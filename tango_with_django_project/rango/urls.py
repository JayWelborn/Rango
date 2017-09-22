from django.conf.urls import url

from . import views

app_name = 'rango'

urlpatterns = [

    url(r'^$', views.index, name='index'),

    url(r'^about/$',
        views.about,
        name='about'),

    url(r'^add_category/$',
        views.add_category,
        name='add_category'),

    url(r'^add_page',
        views.add_page,
        name='add_page'),

    url(r'^category/(?P<category_name_slug>[\w\-]+)/$',
        views.show_category,
        name='show_category'),

    url(r'^category/(?P<category_name_slug>[\w\-]+)/add_page/$',
        views.add_page,
        name='add_page'),

    url(r'^logout/$',
        views.user_logout,
        name='logout'),

    url(r'^restricted/$',
        views.restricted,
        name='restricted'),

    url(r'^search/$',
        views.search,
        name='search'),

    url(r'^goto/',
        views.track_url,
        name='goto'),

    url(r'^profile/edit/$',
        views.ProfileUpdateView.as_view(),
        name='edit_profile'),

    url(r'^profile/list/$',
        views.ListUsers.as_view(),
        name='list_users'),

    url(r'^profile/(?P<pk>[0-9]+)$',
        views.ProfileView.as_view(),
        name='profile'),

    url(r'^like/$',
        views.like_category,
        name='like_category'),

    url(r'^suggest/',
        views.suggest_category,
        name='suggest_category')
]
