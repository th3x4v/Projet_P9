from django.shortcuts import render, redirect
from accounts.models import User
from LITReviews.models import UserFollows, Ticket, Review
from LITReviews.forms import ReviewForm, TicketForm


def home_view(request):
    return render(request, "LITReviews/home.html")


def subscription_view(request):
    user = request.user
    followed_users = UserFollows.objects.filter(user=user.id)
    followers = UserFollows.objects.filter(followed_user=user.id)
    if request.method == "POST":
        search_query = request.POST.get("search")
        search_users = (
            User.objects.filter(username__icontains=search_query)
            .exclude(id__in=followers.values("followed_user"))
            .exclude(id=user.id)
        )
        return render(
            request,
            "LITReviews/subscription.html",
            {
                "search_users": search_users,
                "followers": followers,
                "followed_users": followed_users,
            },
        )

    return render(
        request,
        "LITReviews/subscription.html",
        {"followers": followers, "followed_users": followed_users},
    )


def follow_user(request):
    users = User.objects.all()
    if request.method == "POST":
        user = request.user
        user_id = int(request.POST.get("user_id"))
        try : 
            follow_user = User.object.get(user_id) #ou username pour verifier si le user existe"
        except User.DoesNotExist:
            pass #message d'erreur
        user_follows = UserFollows(user, followed_user)
        user_follows.save() #faire aussi un try si ce user est deja suivi 
        # Redirect back to the subscription page
        return redirect("subscription")


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
