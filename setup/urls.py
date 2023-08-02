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
from LITReviews import views
from accounts.views import login_view, logout_view, register_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", login_view, name="login"),
    path("accounts/register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("LITReviews/home/", views.home_view, name="home"),
    path("LITReviews/subscription/", views.subscription_view, name="subscription"),
    path("LITReviews/unfollow_user/", views.unfollow_user, name="unfollow-user"),
    path("LITReviews/ticket/create_ticket/", views.create_ticket, name="create-ticket"),
    path("LITReviews/post/", views.post_view, name="post"),
    path(
        "LITReviews/ticket/<int:ticket_id>/create_review/",
        views.create_review,
        name="create-review",
    ),
    path(
        "LITReviews/ticket/<int:ticket_id>/", views.ticket_detail, name="ticket-detail"
    ),
    path(
        "LITReviews/ticket/<int:ticket_id>/change/",
        views.modify_ticket,
        name="modify-ticket",
    ),
    path(
        "LITReviews/review/<int:review_id>/", views.review_detail, name="review-detail"
    ),
    path(
        "LITReviews/review/<int:review_id>/change/",
        views.modify_review,
        name="modify-review",
    ),
    path(
        "LITReviews/review/<int:review_id>/delete/",
        views.delete_review,
        name="delete-review",
    ),
    path(
        "LITReviews/ticket/<int:ticket_id>/delete/",
        views.delete_ticket,
        name="delete-ticket",
    ),
    path("LITReviews/feed/", views.feed, name="feed"),
    path(
        "LITReviews/create_review_ticket/",
        views.create_review_ticket,
        name="create-review-ticket",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
