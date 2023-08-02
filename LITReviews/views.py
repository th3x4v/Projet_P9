from django.shortcuts import render, redirect
from accounts.models import User
from LITReviews.models import UserFollows, Ticket, Review
from LITReviews.forms import ReviewForm, TicketForm, ReviewTicketForm
from django.db import IntegrityError
from django.db.models import Count, CharField, Value
from itertools import chain
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session


def home_view(request):
    return render(request, "LITReviews/home.html")


@login_required
def subscription_view(request):
    """Renders the subscription page and handles the follow and search operations"""
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


@login_required
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


@login_required
def create_ticket(request):
    """Creates a new ticket"""
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect("post")
    else:
        form = TicketForm()

    return render(request, "LITReviews/create_ticket.html", {"form": form})


@login_required
def create_review_ticket(request):
    """Creates a new ticket and a review at the same time"""
    if request.method == "POST":
        form = ReviewTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket, review = form.make_review_ticket()
            ticket.user = request.user
            ticket.save()
            review.user = request.user
            review.save()
            return redirect("post")
    else:
        form = ReviewTicketForm()

    return render(request, "LITReviews/create_review_ticket.html", {"form": form})


@login_required
def ticket_detail(request, ticket_id):
    """Renders the ticket detail page"""
    error = False
    error_message = ""
    ticket = Ticket.objects.get(id=ticket_id)
    ticket_reviews = Review.objects.filter(ticket_id=ticket_id)
    if Review.objects.filter(ticket=ticket, user=request.user).exists():
        review_exist = True
    else:
        review_exist = False
    context = {
        "review_exist": review_exist,
        "ticket_reviews": ticket_reviews,
        "ticket": ticket,
        "error": error,
        "error_message": error_message,
    }
    return render(request, "LITReviews/ticket_detail.html", context)


@login_required
def feed(request):
    """Renders the feed page"""
    user = request.user
    # Get the tickets created by the user
    user_tickets = Ticket.objects.filter(user=user)

    # Get the IDs of the users that the current user follows and the current user
    feed_user_ids = list(
        UserFollows.objects.filter(user=user).values_list("followed_user_id", flat=True)
    )
    feed_user_ids.append(user.id)

    # Get the id of the ticket reviewed by a user not followed by the current user
    No_followers_ticket_id = list(
        Review.objects.filter(ticket__in=user_tickets)
        .exclude(user__in=feed_user_ids)
        .values_list("ticket_id", flat=True)
    )
    # Get the tickets created by the user and the followed users
    user_tickets_feed = Ticket.objects.filter(user_id__in=feed_user_ids)
    user_tickets_feed = user_tickets.annotate(content_type=Value("TICKET", CharField()))
    # Get the reviews written by the user and by the not followed the current user
    user_reviews_feed = Review.objects.filter(user_id__in=feed_user_ids)
    user_reviews_not_followed_feed = Review.objects.filter(
        ticket_id__in=No_followers_ticket_id
    )
    user_reviews_feed = user_reviews_feed.annotate(
        content_type=Value("REVIEW", CharField())
    )
    user_reviews_not_followed_feed = user_reviews_not_followed_feed.annotate(
        content_type=Value("REVIEW", CharField())
    )
    # Combine the tickets and reviews using the chain function to create the feed
    user_posts = sorted(
        chain(user_tickets_feed, user_reviews_feed, user_reviews_not_followed_feed),
        key=lambda post: post.time_created,
        reverse=True,
    )
    # check the review without created with no inital ticket
    review_without_ticket = check_review_without_ticket(user_posts)

    context = {
        "user_posts": user_posts,
        "review_without_ticket": review_without_ticket,
    }

    return render(request, "LITReviews/feed.html", context)


@login_required
def post_view(request):
    """Renders post page of the user"""
    user = request.user
    # Get the tickets created by the user
    user_tickets = Ticket.objects.filter(user=user)
    user_tickets = user_tickets.annotate(content_type=Value("TICKET", CharField()))
    # Get the reviews written by the user
    user_reviews = Review.objects.filter(user=user)
    user_reviews = user_reviews.annotate(content_type=Value("REVIEW", CharField()))
    # Combine the tickets and reviews using the chain function
    user_posts = sorted(
        chain(user_tickets, user_reviews),
        key=lambda post: post.time_created,
        reverse=True,
    )
    # check the review created with no initial ticket
    review_without_ticket = check_review_without_ticket(user_posts)

    context = {
        "user_posts": user_posts,
        "review_without_ticket": review_without_ticket,
    }

    return render(
        request,
        "LITReviews/post.html",
        context,
    )


def check_review_without_ticket(user_posts):
    """check if the review is created no in a ticket answer"""
    review_without_ticket = []
    for i in range(len(user_posts)):
        if i + 1 < len(user_posts) and user_posts[i].content_type == "REVIEW":
            if (
                user_posts[i].ticket == user_posts[i + 1]
                and user_posts[i].user == user_posts[i + 1].user
                and user_posts[i].time_created.strftime("%d/%m/%Y %H:%M")
                == user_posts[i + 1].time_created.strftime("%d/%m/%Y %H:%M")
            ):
                review_without_ticket.append(user_posts[i + 1])
    return review_without_ticket


@login_required
def create_review(request, ticket_id):
    """create a review"""
    error = False
    error_message = ""
    ticket = Ticket.objects.get(id=ticket_id)

    ticket_reviews = Review.objects.filter(ticket_id=ticket_id)

    # Check if the current user has already commented this ticket
    if ticket_id in ticket_reviews:
        error = True
        error_message = "Vous avez déja écris un commentaire sur ce billet"
        context = {
            "ticket_reviews": ticket_reviews,
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
    """Modifiy a ticket"""
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


@login_required
def review_detail(request, review_id):
    review = Review.objects.get(id=review_id)
    return render(request, "LITReviews/review_detail.html", {"review": review})


@login_required
def modify_review(request, review_id):
    """Modifiy a review"""
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
    """Delete a review"""
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
    """Delete a ticket"""
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
