from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag
def provider_login_url(provider_name, *args, **kwargs):
    """Return a login URL for a social provider. If django-allauth is installed,
    attempt to reverse its provider login URL; otherwise return '#' so templates
    don't error out.
    """
    # If django-allauth is enabled in settings, try to resolve its common URL names.
    from django.conf import settings
    tried = []
    # Try several reverse name / signature combinations used by various setups
    candidates = [
        ('socialaccount_login', (provider_name,)),
        ('socialaccount_login', (), {'provider': provider_name}),
        ('account_social_login', (provider_name,)),
        ('socialaccount_login', (provider_name, '')),  # some setups include trailing segment
        # Provider-specific names used by allauth providers (e.g. 'google_login')
        (f'{provider_name}_login', ()),
        (f'{provider_name}_login', (), {}),
    ]
    for name, a in [(c[0], c[1] if len(c) > 1 else ()) for c in candidates]:
        try:
            # attempt positional args first; if a is a dict it'll be ignored here
            return reverse(name, args=a)
        except NoReverseMatch:
            tried.append(name)

    # Try kwargs forms
    # try resolving with kwargs
    try:
        return reverse('socialaccount_login', kwargs={'provider': provider_name})
    except NoReverseMatch:
        tried.append(('socialaccount_login', 'kwargs'))

    try:
        return reverse('account_social_login', kwargs={'provider': provider_name})
    except NoReverseMatch:
        tried.append(('account_social_login', 'kwargs'))

    # Fallback to common URL paths used by allauth when included under /accounts/
    common_paths = [
        f"/accounts/{provider_name}/login/",
        f"/accounts/{provider_name}/",
        f"/accounts/social/login/{provider_name}/",
        f"/accounts/{provider_name}/login/",
    ]
    # At this point none of the reverses worked. If allauth is enabled return
    # a plausible common path; otherwise return '#' so templates don't break.
    use_allauth = getattr(settings, 'USE_ALLAUTH', False)
    url = '#'
    if use_allauth:
        url = common_paths[0]
    else:
        # last effort: return the first common path (may not function) to keep the UI usable
        url = common_paths[0]

    # If caller supplied a `process` kwarg (e.g. process='login'), append it as a query param
    process = kwargs.get('process')
    if process and url and url != '#':
        sep = '&' if '?' in url else '?'
        url = f"{url}{sep}process={process}"

    return url
