
from django.shortcuts import render
from django.shortcuts import redirect
from accounts.models import User
from LITReviews.models import UserFollows


def home_view(request):
    return render(request, 'LITReviews/home.html')

def subscription_view(request):
    user= request.user
    followers = UserFollows.objects.filter(user=user.id)
    if request.method == 'POST':
        search_query = request.POST.get('search')
        #search_users = User.objects.filter(username__icontains=search_query)
        search_users = User.objects.filter(username__icontains=search_query).exclude(id__in=followers.values('followed_user')).exclude(id=user.id)
        return render(request, 'LITReviews/subscription.html', {'search_users': search_users, 'followers': followers})

    return render(request, 'LITReviews/subscription.html', {'followers': followers})

def follow_user(request):
    users = User.objects.all()
    if request.method == 'POST':
        user= request.user
        user_id = int(request.POST.get('user_id'))
        user_follows = UserFollows.objects.create(user=request.user, followed_user=users[user_id-1])
        user_follows.save()
        followers = UserFollows.objects.filter(user=user.id)
        print('debug')
        print(followers)
        # Redirect back to the subscription page or any other desired page
        return redirect('subscription')
