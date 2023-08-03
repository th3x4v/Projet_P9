from django import template
from LITReviews.models import Review, Ticket

register = template.Library()


@register.filter
def review_exist(ticket, user):
    """checking if this ticket exists"""
    if Review.objects.filter(ticket=ticket, user=user).exists():
        return True
    return False


@register.filter
def stars(value):
    """Returns a list of value for the star rating"""
    rating = []
    for i in range(5):
        if i < int(value):
            rating.append(1)
        else:
            rating.append(0)
    return rating
