from django.shortcuts import render, redirect
from accounts.models import User
from LITReviews.models import UserFollows, Ticket, Review
from LITReviews.forms import ReviewForm, TicketForm
from django.db import IntegrityError
from django.db.models import Count, CharField, Value
from itertools import chain
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed, HttpResponse


def home_view(request):
    return render(request, "LITReviews/home.html")


def subscription_view(request):
    error = False
    error_message = ""
    user = request.user
    followed_users = UserFollows.objects.filter(user=user.id)
    followers = UserFollows.objects.filter(followed_user=user.id)
    search_users = None
    if request.method == "POST":
        search_query = request.POST.get("search")
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

    return render(
        request,
        "LITReviews/subscription.html",
        {
            "search_users": search_users,
            "followers": followers,
            "followed_users": followed_users,
            "error": error,
            "error_message": error_message,
        },
    )

def unfollow_user(request):
    if request.method == "POST":
        user = request.user
        user_id = int(request.POST.get("user_id"))
        UserFollows.objects.filter(user=user, followed_user_id=user_id).delete()
        # Redirect back to the subscription page
        return redirect("subscription")


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
    ticket = Ticket.objects.get(id=ticket_id)
    return render(request, "LITReviews/ticket_detail.html", {"ticket": ticket})


def post_view(request):
    # Get the current user
    user = request.user

    tickets = Ticket.objects.filter(user=user)

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

    return render(
        request,
        "LITReviews/post.html",
        {"user_posts": user_posts, "tickets": tickets},
    )


def create_review(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)

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


def modify_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)

    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = TicketForm(instance=ticket)

    return render(
        request, "LITReviews/modify_ticket.html", {"form": form, "ticket": ticket}
    )


def review_detail(request, review_id):
    review = Review.objects.get(id=review_id)
    return render(request, "LITReviews/review_detail.html", {"review": review})


def modify_review(request, review_id):
    review = Review.objects.get(id=review_id)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ReviewForm(instance=review)

    return render(
        request, "LITReviews/modify_review.html", {"form": form, "review": review}
    )

def delete_review(request, review_id):
    ticket = Review.objects.get(id=review_id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('post')

    # If the request method is not POST, render the confirmation template
    return render(request, "LITReviews/delete_review.html", {'review': review})

def delete_ticket(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('post')

    # If the request method is not POST, render the confirmation template
    return render(request, "LITReviews/delete_ticket.html", {'ticket': ticket})