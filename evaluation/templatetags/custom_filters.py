from django import template

register = template.Library()

@register.filter
def get_value_at_index(value, index):
    """Returns the value at the specified index in a list."""
    try:
        return value[int(index)]
    except (IndexError, ValueError):
        return None  # Return None if index is out of range or not valid
