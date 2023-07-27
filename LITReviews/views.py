from django.shortcuts import render, redirect
from accounts.models import User
from LITReviews.models import UserFollows, Ticket, Review
from LITReviews.forms import ReviewForm, TicketForm
from django.db import IntegrityError


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
            search_users2 = (
                User.objects.filter(username__icontains=search_query)
                .exclude(id__in=followed_users.values("user_id"))
                .exclude(id=user.id)
            )

        else:
            # Follow operation
            user_id = int(request.POST.get("user_id"))
            try:
                followed_user = User.objects.get(id=user_id)
                user_follows = UserFollows(user=user, followed_user=followed_user)
                user_follows.save()
            except User.DoesNotExist:
                error = True
                error_message = f"L'utilisateur n'existe pas."
            except IntegrityError:
                error = True
                error_message = f"Vous suivez déjà l'utilisateur {followed_user.username}"

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

def follow_user(request):
    pass

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
    user = request.user
    tickets = Ticket.objects.filter(user=user)
    return render(request, "LITReviews/post.html", {"tickets": tickets})


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
