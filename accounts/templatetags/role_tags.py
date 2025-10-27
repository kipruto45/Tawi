from django import template
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model

register = template.Library()


@register.simple_tag(takes_context=False)
def role_options(selected=None):
    """Return HTML <option> elements for canonical roles.

    Templates should call `{% role_options %}` inside a <select> to render
    the same, authoritative list of roles across the UI.
    """
    User = get_user_model()
    # Prefer an explicitly declared canonical list; fall back to ROLE_CHOICES
    choices = getattr(User, 'CANONICAL_ROLES', None) or getattr(User, 'ROLE_CHOICES', [])
    out = []
    seen = set()
    for key, label in choices:
        # skip duplicate keys while preserving order
        if key in seen:
            continue
        seen.add(key)
        sel = ' selected' if selected and str(selected) == str(key) else ''
        # Escape label minimally by relying on Django's choices being trusted
        out.append(f'<option value="{key}"{sel}>{label}</option>')
    return mark_safe('\n'.join(out))
