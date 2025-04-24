from django import template

register = template.Library()


@register.filter
def is_image_file(url):
    if not url:
        return False
    return url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
