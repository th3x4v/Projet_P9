
from django.shortcuts import render
from django.shortcuts import redirect
from accounts.models import User
from LITReviews.models import UserFollows


def home_view(request):
    return render(request, 'LITReviews/home.html')

def subscription_view(request):
    user= request.user
    followed_users = UserFollows.objects.filter(user=user.id)
    followers = UserFollows.objects.filter(followed_user=user.id)
    if request.method == 'POST':
        search_query = request.POST.get('search')
        search_users = User.objects.filter(username__icontains=search_query).exclude(id__in=followers.values('followed_user')).exclude(id=user.id)
        return render(request, 'LITReviews/subscription.html', {'search_users': search_users,'followers': followers, 'followed_users': followed_users})

    return render(request, 'LITReviews/subscription.html', {'followers': followers, 'followed_users': followed_users})

def follow_user(request):
    users = User.objects.all()
    if request.method == 'POST':
        user= request.user
        user_id = int(request.POST.get('user_id'))
        user_follows = UserFollows.objects.create(user=request.user, followed_user=users[user_id-1])
        user_follows.save()
        # Redirect back to the subscription page
        return redirect('subscription')

def unfollow_user(request):
    if request.method == 'POST':
        user = request.user
        user_id = int(request.POST.get('user_id'))
        UserFollows.objects.filter(user=user, followed_user_id=user_id).delete()
        # Redirect back to the subscription page
        return redirect('subscription')
