"""
URL configuration for setup project.

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
from django.contrib import admin
from django.urls import path
from LITReviews.views import home_view, subscription_view, follow_user, unfollow_user, create_ticket, ticket_detail, post_view, create_review
from accounts.views import login_view, logout_view, register_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('LITReviews/login/', login_view, name='login'),
    path('LITReviews/register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('LITReviews/home/', home_view, name='home'),
    path('LITReviews/subscription/', subscription_view, name='subscription'),
    path('LITReviews/follow_user/', follow_user, name='follow-user'),
    path('LITReviews/unfollow_user/', unfollow_user, name='unfollow-user'),
    path('LITReviews/create_ticket/', create_ticket, name='create-ticket'),
    path('LITReviews/post/', post_view, name='post'),
    path('LITReviews/<int:ticket_id>/create_review/', create_review, name='create-review'),
    path('LITReviews/<int:ticket_id>/', ticket_detail, name='ticket-detail'),  

]
