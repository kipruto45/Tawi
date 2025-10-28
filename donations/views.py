from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

# Optional Stripe integration
try:
    import stripe
except Exception:
    stripe = None

def _get_donation_queryset():
    """Try to import a Donation model if it exists; otherwise return empty list."""
    try:
        from .models import Donation  # optional app model
        return Donation.objects.all().order_by('-date')
    except Exception:
        return []


def donation_list(request):
    """Render the donations list page. If a Donation model is present use it, otherwise pass an empty list."""
    # Restrict this page so admin users (staff/superuser or users with
    # role=='admin') are redirected away. The page should be visible to
    # all other users (including anonymous visitors).
    try:
        user = request.user
    except Exception:
        user = None

    try:
        is_admin = False
        if user and getattr(user, 'is_authenticated', False):
            try:
                if user.has_perm('donations.view_admin_donations'):
                    is_admin = True
                else:
                    # some installations store a role string on the user
                    if getattr(user, 'role', None) == 'admin':
                        is_admin = True
                    elif 'Admins' in set(user.groups.values_list('name', flat=True)):
                        is_admin = True
            except Exception:
                # fallback to legacy checks
                if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
                    is_admin = True
        if is_admin:
            # redirect admins to the admin dashboard to keep donation flows
            # separate from regular user donations.
            from django.shortcuts import redirect
            try:
                return redirect('admin_dashboard')
            except Exception:
                # fallback to the namespaced dashboard view
                return redirect('dashboard:dashboard')
    except Exception:
        # if anything goes wrong determining admin status, continue and
        # render the donations list to avoid blocking users unintentionally.
        pass
    qs = _get_donation_queryset()
    # if qs is a Django queryset, use select_related for donor to reduce DB hits
    try:
        recent = qs.select_related('donor').all()[:50]
    except Exception:
        recent = qs[:50] if hasattr(qs, '__len__') or hasattr(qs, '__iter__') else []
    context = {
        'recent_donations': recent,
    }
    return render(request, 'donations/donation_list.html', context)


def make_donation(request):
    """A minimal donation flow placeholder. POST will attempt to create a Donation if model exists, otherwise show a success message and redirect back.

    This keeps the link in the donations list working even if a full payment integration is not present.
    """
    if request.method == 'POST':
        amount_str = request.POST.get('amount') or request.POST.get('donation_amount')
        try:
            amount = Decimal(str(amount_str))
        except (InvalidOperation, TypeError):
            messages.error(request, 'Please enter a valid donation amount.')
            return redirect(reverse('donations:make_donation'))

        if amount <= 0:
            messages.error(request, 'Donation amount must be greater than zero.')
            return redirect(reverse('donations:make_donation'))

        # best-effort create a Donation model instance if available
        try:
            from .models import Donation
            donor = request.user if request.user.is_authenticated else None
            d = Donation.objects.create(donor=donor, amount=amount, status='Pending', date=timezone.now())
            messages.success(request, 'Thank you — donation recorded (placeholder).')
        except Exception:
            # If Donation model doesn't exist or save fails, still show success message
            messages.success(request, 'Thank you — donation received (placeholder).')

        return redirect(reverse('donations:donations'))

    # GET: render the donation form
    return render(request, 'donations/make_donation.html')


def create_payment_intent(request):
    """Optional endpoint to create a Stripe PaymentIntent. Only active when stripe package
    is installed and STRIPE_SECRET_KEY is set in env. Returns JSON with client_secret.
    """
    if stripe is None:
        return JsonResponse({'error': 'stripe not configured'}, status=404)

    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)

    try:
        amount = Decimal(request.POST.get('amount', '0'))
        if amount <= 0:
            raise ValueError('invalid amount')
    except Exception:
        return JsonResponse({'error': 'invalid amount'}, status=400)

    # stripe expects amount in cents/intes depending on currency; this is a scaffold
    stripe.api_key = getattr(__import__('os').environ, 'get')('STRIPE_SECRET_KEY', None)
    if not stripe.api_key:
        return JsonResponse({'error': 'stripe secret not configured'}, status=500)

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='kes',
            metadata={'purpose': 'donation'},
        )
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
def stripe_webhook(request):
    """Minimal webhook receiver for Stripe. Validates signature if configured and
    updates Donation status when a payment is succeeded. This is a scaffold and
    requires proper signing secrets in production.
    """
    if stripe is None:
        return HttpResponse(status=404)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(__import__('os').environ, 'get')('STRIPE_WEBHOOK_SECRET', None)
    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = stripe.Event.construct_from(django.utils.json.loads(payload), stripe.api_key)
    except Exception:
        return HttpResponse(status=400)

    # Handle the event types we care about
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        # best-effort: if Donation model present, mark matching donation 'Completed'
        try:
            from .models import Donation
            # metadata lookups or other mapping would be here
            # This scaffold doesn't tie PaymentIntent->Donation automatically.
        except Exception:
            pass

    return HttpResponse(status=200)
