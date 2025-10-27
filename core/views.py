from django.shortcuts import render, redirect

def landing(request):
    """Site landing page.

    If the visitor is anonymous, redirect them to the guest dashboard so they
    immediately see the public-facing dashboard experience. Authenticated users
    still see the normal landing page.
    """
    # Always show the marketing landing page at the site root. Guests can
    # navigate to the Guest Dashboard separately. This makes starting the
    # app locally show the landing page immediately.
    return render(request, 'core/landing.html')

def about(request):
    return render(request, 'core/about.html')


def learn_more(request):
    """Simple informational 'learn more' page used by marketing links.

    Provide a minimal template so the top-level /learn-more/ route returns
    a friendly page rather than a 404.
    """
    return render(request, 'core/learn_more.html')

def profile(request):
    return render(request, 'core/profile.html')


def partner_list(request):
    # simple partners list stub - in future this can query a Partner model
    partners = [
        {'name': 'Green Kenya Initiative', 'location': 'Nairobi'},
        {'name': 'Coast Conservation Group', 'location': 'Mombasa'},
        {'name': 'Rift Valley Reforesters', 'location': 'Eldoret'},
    ]
    return render(request, 'core/partner_list.html', {'partners': partners})


def partner_add(request):
    """Placeholder view for adding a partner.

    Currently redirects back to the partner list. This ensures templates
    that reverse 'core:partner_add' will succeed. Implement a proper
    create form here in a follow-up task if desired.
    """
    return redirect('partner_list')


def partner_detail(request, pk):
    """Placeholder partner detail view that currently reuses partner_list.

    This exists so templates that call `core:partner_detail` will reverse
    and not raise NoReverseMatch. If a Partner model is added later, this
    should be replaced with a real detail page.
    """
    return redirect('partner_list')


def partner_edit(request, pk):
    return redirect('partner_list')


def partner_delete(request, pk):
    return redirect('partner_list')


def message_list(request):
    # stub messages list; replace with real message model or notifications integration
    messages = [
        {'subject': 'Welcome to Tawi', 'from': 'Team', 'date': '2025-01-01'},
    ]
    return render(request, 'core/message_list.html', {'messages': messages})


def contact(request):
    return render(request, 'core/contact.html')

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def core_dashboard(request):
    # simple wrapper for admin dashboard
    from reports.views import summary_stats
    resp = summary_stats(request._request)
    summary = resp.data if hasattr(resp, 'data') else {}
    return render(request, 'core/core_dashboard.html', {'summary': summary})

def core_analytics(request):
    return render(request, 'core/core_analytics.html')
