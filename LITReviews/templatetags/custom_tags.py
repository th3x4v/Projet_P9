from django import template
from LITReviews.models import Review

register = template.Library()
    
    
@register.filter
def review_exist(ticket, user):
    if Review.objects.filter(ticket=ticket, user=user).exists():
        return True
    return False