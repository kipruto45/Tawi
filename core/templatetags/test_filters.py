from django import template

register = template.Library()


@register.filter(name='int')
def to_int(value):
    """A simple int filter used only for tests to emulate templates that call `|int`.

    This is intentionally minimal and forgiving.
    """
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return 0
