from django import template
from LITReviews.models import Review, Ticket

register = template.Library()
    
    
@register.filter
def review_exist(ticket, user):
    if Review.objects.filter(ticket=ticket, user=user).exists():
        return True
    return False


@register.filter
def check_review_without_ticket(user_posts):
    review_without_ticket = []
    for i in range(len(user_posts)):
        if i + 1 < len(user_posts) and user_posts[i + 1].ticket == user_posts[i].ticket:
            review_without_ticket.append(user_posts[i])
            print(post.user)
    return review_without_ticket
