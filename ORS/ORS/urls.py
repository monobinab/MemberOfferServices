"""ORS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from campaign import views
from rest_framework.authtoken import views as authviews


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(
            regex=r'^api/login/$',
            view=views.login_view,
            name="customer_login_rest_api"
    ),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
    url(r'^$', views.index),
    url(
        regex=r"^api/logout/$",
        view=views.logout_view,
        name="logout_api"
    ),
    url(
            regex=r"^api/campaign/$",
            view=views.campaign,
            name="campaign_api"
    ),
    url(r'^api/campaign/(?P<campaign_id>\w+)/$', views.campaign),
]

