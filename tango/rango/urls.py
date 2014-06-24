from django.conf.urls import patterns, url
from rango.views import *

urlpatterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^about/$', about, name='about'),
    url(r'^category/(?P<category_name_url>\w+)/add_page/$', add_page, name='add_page'),
    url(r'^category/(?P<category_name_url>\w+)/$', category, name='category'),
    url(r'^add_category(?:/(?P<category_name_url>\w+))?/$', add_category, name='add_category'),
    url(r'^register/$', register, name='register'),
    url(r'^login/$', user_login, name='login'),
    url(r'^logout/$', user_logout, name='logout'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^goto/$', track_url, name='goto'),
    url(r'^like_category/$', like_category, name='like_category'),
    url(r'^suggest_category/$', suggest_category, name='suggest_category'),
)

