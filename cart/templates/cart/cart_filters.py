from django import template
register = template.Library()

@register.filter(name='get_quantity')
def get_quantity(cart, movie_id):
    # cart keys are strings in session
    return cart.get(str(movie_id), 0)
