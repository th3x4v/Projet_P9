from django.shortcuts import render, redirect
from accounts.models import User
from LITReviews.models import UserFollows, Ticket, Review
from LITReviews.forms import ReviewForm, TicketForm
from django.db import IntegrityError
from django.db.models import Count, CharField, Value
from itertools import chain
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session


def home_view(request):
    return render(request, "LITReviews/home.html")


def subscription_view(request):
    """Renders the subscription page and handles the follow and search operations."""
    error = False
    error_message = ""
    user = request.user
    followed_users = UserFollows.objects.filter(user=user.id)
    followers = UserFollows.objects.filter(followed_user=user.id)
    users = User.objects.all()
    search_users = None
    if request.method == "POST":
        search_query = request.POST.get("searchs")
        if search_query:
            # Search operation
            search_users = (
                User.objects.filter(username__icontains=search_query)
                .exclude(id__in=followed_users.values("followed_user__id"))
                .exclude(id=user.id)
            )
        else:
            # Follow operation
            user_id = int(request.POST.get("user_id"))
            try:
                followed_user = User.objects.get(id=user_id)
                if user == followed_user:
                    error = True
                    error_message = "Vous ne pouvez pas vous suivre vous-même."
                else:
                    user_follows = UserFollows(user=user, followed_user=followed_user)
                    user_follows.save()
            except User.DoesNotExist:
                error = True
                error_message = f"L'utilisateur n'existe pas."
            except IntegrityError:
                error = True
                error_message = (
                    f"Vous suivez déjà l'utilisateur {followed_user.username}"
                )
    context = {
        "search_users": search_users,
        "followers": followers,
        "followed_users": followed_users,
        "users": users,
        "error": error,
        "error_message": error_message,
    }

    return render(request, "LITReviews/subscription.html", context)


def unfollow_user(request):
    """Handles the unfollow operation for a user"""
    error = False
    error_message = ""
    user = request.user
    followed_users = UserFollows.objects.filter(user=user.id)
    followers = UserFollows.objects.filter(followed_user=user.id)
    search_users = None
    if request.method == "POST":
        user_id = int(request.POST.get("user_id"))

        followed_user_ids = list(
            followed_users.values_list("followed_user_id", flat=True)
        )
        if user_id in followed_user_ids:
            UserFollows.objects.filter(user=user, followed_user_id=user_id).delete()
        else:
            error = True
            error_message = f"Vous ne suivez pas cet utilisateur"
    context = {
        "search_users": search_users,
        "followers": followers,
        "followed_users": followed_users,
        "error": error,
        "error_message": error_message,
    }

    return render(request, "LITReviews/subscription.html", context)


def create_ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("home")
    else:
        form = TicketForm()

    return render(request, "LITReviews/create_ticket.html", {"form": form})


def ticket_detail(request, ticket_id):
    error = False
    error_message = ""
    ticket = Ticket.objects.get(id=ticket_id)
    ticket_reviews = Review.objects.filter(ticket_id=ticket_id)
    context = {
        "ticket_reviews":ticket_reviews,
        "ticket": ticket,
        "error": error,
        "error_message": error_message,
    }
    return render(request, "LITReviews/ticket_detail.html", context)


def get_user_posts(users):
    # Get the tickets created by the user
    user_tickets = Ticket.objects.filter(user__in=users)
    user_tickets = user_tickets.annotate(content_type=Value("TICKET", CharField()))
    # Get the reviews written by the user
    user_reviews = Review.objects.filter(user__in=users)
    user_reviews = user_reviews.annotate(content_type=Value("REVIEW", CharField()))

    # Combine the tickets and reviews using the chain function
    user_posts = sorted(
        chain(user_tickets, user_reviews),
        key=lambda post: post.time_created,
        reverse=True,
    )

    return user_posts


def feed(request):
    user = request.user

    # Get the IDs of the users that the current user follows and the current user
    feed_user_ids = list(
        UserFollows.objects.filter(user=user).values_list("followed_user_id", flat=True)
    )
    feed_user_ids.append(user.id)

    user_reviews = Review.objects.filter(user=user.id)

    user_posts = get_user_posts(feed_user_ids)

    return render(
        request,
        "LITReviews/feed.html",
        {"user_posts": user_posts,"user_reviews": user_reviews}
    )


def post_view(request):
    # Get the current user
    user = request.user

    user_reviews = Review.objects.filter(user=user.id)

    user_posts = user_posts = get_user_posts([user.id])

    return render(
        request,
        "LITReviews/post.html",
        {"user_posts": user_posts, "user_reviews": user_reviews},
    )


def create_review(request, ticket_id):
    error = False
    error_message = ""

    ticket = Ticket.objects.get(id=ticket_id)

    ticket_reviews = Review.objects.filter(ticket_id=ticket_id)

    # Check if the current user has already commented this ticket
    if ticket_id in ticket_reviews:
        error = True
        error_message = "Vous avez déja écris un commentaire sur ce billet"
        context = {
            "ticket_reviews":ticket_reviews,
            "ticket": ticket,
            "error": error,
            "error_message": error_message,
        }
        return render(request, "LITReviews/ticket_detail.html", context)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect("home")
    else:
        form = ReviewForm()

    return render(
        request, "LITReviews/create_review.html", {"form": form, "ticket": ticket}
    )


@login_required
def modify_ticket(request, ticket_id):
    error = False
    error_message = ""
    ticket = Ticket.objects.get(id=ticket_id)

    # Check if the current user is the writer of the ticket or a superuser
    if ticket.user != ticket.user and not request.user.is_superuser:
        error = True
        error_message = "Vous n'êtes pas autorisé(e) à modifier ce billet"
        context = {
            "ticket": ticket,
            "error": error,
            "error_message": error_message,
        }
        return render(request, "LITReviews/ticket_detail.html", context)

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            context = {"form": form, "ticket": ticket}
            return render(request, "LITReviews/ticket_detail.html", context)
    else:
        form = TicketForm(instance=ticket)

    context = {"form": form, "ticket": ticket}
    return render(request, "LITReviews/modify_ticket.html", context)


def review_detail(request, review_id):
    review = Review.objects.get(id=review_id)
    return render(request, "LITReviews/review_detail.html", {"review": review})


@login_required
def modify_review(request, review_id):
    error = False
    error_message = ""
    review = Review.objects.get(id=review_id)

    # Check if the current user is the writer of the review or a superuser
    if request.user != review.user and not request.user.is_superuser:
        error = True
        error_message = "Vous n'êtes pas autorisé(e) à modifier ce commentaire"
        context = {
            "review": review,
            "error": error,
            "error_message": error_message,
        }
        return render(request, "LITReviews/review_detail.html", context)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect(request.META.get("HTTP_REFERER"))
    else:
        form = ReviewForm(instance=review)

    return render(
        request, "LITReviews/modify_review.html", {"form": form, "review": review}
    )


@login_required
def delete_review(request, review_id):
    error = False
    error_message = ""
    try:
        review = Review.objects.get(id=review_id)

        # Check if the current user is the writer of the review or a superuser
        if request.user != review.user and not request.user.is_superuser:
            error = True
            error_message = "Vous n'êtes pas autorisé(e) à supprimer ce commentaire"
            context = {
                "review": review,
                "error": error,
                "error_message": error_message,
            }
            return render(request, "LITReviews/review_detail.html", context)

        if request.method == "POST":
            review.delete()
            return redirect("post")

    except Review.DoesNotExist:
        error = True
        error_message = "Ce commentaire n'existe pas"
        context = {
            "error": error,
            "error_message": error_message,
        }
        return render(request, "LITReviews/feed.html", context)

    # If the request method is not POST, render the confirmation template
    return render(request, "LITReviews/delete_review.html", {"review": review})


@login_required
def delete_ticket(request, ticket_id):
    error = False
    error_message = ""
    try:
        ticket = Ticket.objects.get(id=ticket_id)

        # Check if the current user is the writer of the ticket or a superuser
        if request.user != ticket.user and not request.user.is_superuser:
            error = True
            error_message = "Vous n'êtes pas autorisé(e) à supprimer ce billet"
            context = {
                "ticket": ticket,
                "error": error,
                "error_message": error_message,
            }
            return render(request, "LITReviews/ticket_detail.html", context)

        if request.method == "POST":
            ticket.delete()
            return redirect("post")

    except Ticket.DoesNotExist:
        error = True
        error_message = "Le billet n'existe pas"
        context = {
            "error": error,
            "error_message": error_message,
        }
        return render(request, "LITReviews/feed.html", context)

    # If the request method is not POST, render the confirmation template
    return render(request, "LITReviews/delete_ticket.html", {"ticket": ticket})
