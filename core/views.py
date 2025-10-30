from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.urls import reverse

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
    """Add a partner via a simple form and persist to the Core Partner model.

    If the Partner model/migrations are not available this will fall back
    to redirecting back to the partner list to keep templates functional.
    """
    try:
        from .forms import PartnerForm
        from .models import Partner
    except Exception:
        return redirect('partner_list')

    if request.method == 'POST':
        form = PartnerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('partner_list')
    else:
        form = PartnerForm()
    return render(request, 'core/partner_add.html', {'form': form})


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


def _is_site_admin(user):
    try:
        if not (user and user.is_authenticated):
            return False
        # superusers or a role string 'admin' are allowed
        if getattr(user, 'is_superuser', False):
            return True
        if getattr(user, 'is_staff', False):
            return True
        # some installs store a role on a related profile
        if getattr(user, 'role', None) == 'admin':
            return True
        try:
            # fallback: group name 'Admins'
            if 'Admins' in set(user.groups.values_list('name', flat=True)):
                return True
        except Exception:
            pass
    except Exception:
        pass
    return False


@user_passes_test(_is_site_admin, login_url='accounts:login')
def message_send(request):
    """Admin-only lightweight message sender.

    This view provides a simple form to send email messages to users.
    Sent messages are stored in the cache (last 50) so admins can review
    recently sent messages via `sent_messages` view. This is intentionally
    lightweight (no new models) so it works without migrations.
    """
    User = get_user_model()
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        body = request.POST.get('body', '').strip()
        recipients_mode = request.POST.get('recipients', 'all')
        recipients = []
        if recipients_mode == 'all':
            recipients = list(User.objects.filter(is_active=True).values_list('email', flat=True))
        else:
            explicit = request.POST.get('emails', '')
            recipients = [e.strip() for e in explicit.split(',') if e.strip()]

        # send mail best-effort; skip empty recipients
        sent_count = 0
        if recipients:
            try:
                send_mail(subject or 'Message from Tawi', body or '', request.user.email or None, recipients, fail_silently=True)
                sent_count = len(recipients)
            except Exception:
                sent_count = 0

        # persist message and recipients to DB (if available) and enqueue async send
        try:
            from .models import MessageSent, MessageRecipient
            preview = ','.join(recipients[:20]) if recipients else ''
            ms = MessageSent.objects.create(
                subject=subject,
                body=body,
                sender=request.user.username,
                recipients_count=len(recipients),
                recipients_preview=preview,
            )
            # create recipient records
            rec_objs = []
            for r in recipients:
                if r:
                    rec_objs.append(MessageRecipient(message=ms, email=r, status='pending'))
            if rec_objs:
                MessageRecipient.objects.bulk_create(rec_objs)

            # enqueue Celery task to send this message (best-effort)
            try:
                from .tasks import send_message_task
                # use delay to enqueue; if Celery not running this will still work when configured
                send_message_task.delay(ms.id)
            except Exception:
                # fallback: attempt synchronous send to avoid losing message
                try:
                    send_mail(subject or 'Message from Tawi', body or '', request.user.email or None, recipients, fail_silently=True)
                except Exception:
                    pass

        except Exception:
            # fallback to cache-based recent list if DB not available
            record = {
                'subject': subject,
                'body': body,
                'recipients_count': len(recipients),
                'recipients_preview': (recipients[:10] if recipients else []),
                'sender': request.user.username,
            }
            cache_key = 'core.recent_sent_messages'
            recent = cache.get(cache_key, [])
            recent.insert(0, record)
            recent = recent[:50]
            cache.set(cache_key, recent, timeout=None)

        django_messages.success(request, f'Message queued to {len(recipients)} recipients (best-effort).')
        return redirect(reverse('core:sent_messages'))

    return render(request, 'core/message_send.html', {})


@user_passes_test(_is_site_admin, login_url='accounts:login')
def sent_messages(request):
    # prefer DB-backed MessageSent entries if available
    try:
        from .models import MessageSent
        recent = list(MessageSent.objects.all().order_by('-created_at')[:50])
    except Exception:
        cache_key = 'core.recent_sent_messages'
        recent = cache.get(cache_key, [])
    return render(request, 'core/sent_messages.html', {'recent': recent})


def contact(request):
    return render(request, 'core/contact.html')

def terms(request):
    return render(request, 'core/terms.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def core_dashboard(request):
    # simple wrapper for admin dashboard
    from reports.views import summary_stats
    # summary_stats is a DRF view; pass the Django request object directly.
    resp = summary_stats(request)
    summary = resp.data if hasattr(resp, 'data') else {}
    return render(request, 'core/core_dashboard.html', {'summary': summary})

def core_analytics(request):
    return render(request, 'core/core_analytics.html')
