from django import template
from LITReviews.models import Review, Ticket

register = template.Library()


@register.filter
def review_exist(ticket, user):
    if Review.objects.filter(ticket=ticket, user=user).exists():
        return True
    return False

@register.filter
def stars(value):
    rating = []
    for i in range(5):
        if i < int(value):
            rating.append(1)
        else:
            rating.append(0)
    return rating
