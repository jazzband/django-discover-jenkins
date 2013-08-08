from django.conf.urls import patterns, url

urlpatterns = patterns('',
     url(r'^test_click/$', 'django.views.generic.simple.direct_to_template',
         {'template': 'test_app/wm_test_click.html'}, name='wm_test_click')
)
