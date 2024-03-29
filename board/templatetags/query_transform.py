from django import template
from django.http import HttpRequest

register = template.Library()


@register.simple_tag
def update_query_params(request: HttpRequest, **kwargs) -> str:
    query_params = request.GET.copy()

    for key, value in kwargs.items():
        query_params[key] = value

    return query_params.urlencode()
