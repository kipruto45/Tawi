from django.shortcuts import render
from django.core.cache import cache
from .services.dashboard_service import get_dashboard_summary
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def dashboard(request):
    """Generic dashboard landing (redirects to admin view for now)."""
    return dashboard_admin(request)


def dashboard_admin(request):
    """Render admin dashboard using aggregated metrics from the service layer.

    Uses caching to avoid repeated heavy queries.
    """
    cache_key = f"dashboard_summary_view_{request.user.id if request.user.is_authenticated else 'anon'}"
    summary = cache.get(cache_key)
    if summary is None:
        summary = get_dashboard_summary(user=request.user if request.user.is_authenticated else None)
        cache.set(cache_key, summary, 60 * 5)

    return render(request, 'dashboard/dashboard_admin.html', {'summary': summary})


def dashboard_field(request):
    # Build context using the common dashboard summary service so field officers
    # see counts scoped to their role where applicable.
    try:
        summary = get_dashboard_summary(user=request.user if request.user.is_authenticated else None)
    except Exception:
        summary = {}

    # Helper to read both dict-like and object-like summary
    def _get(k, default=0):
        if not summary:
            return default
        if isinstance(summary, dict):
            return summary.get(k, default)
        return getattr(summary, k, default)

    # Try to load notifications if the app is present; fail safe to empty list.
    notifications_preview = []
    try:
        from notifications.models import Notification
        notifications_qs = Notification.objects.all().order_by('-created_at')[:5]
        notifications_preview = list(notifications_qs)
    except Exception:
        notifications_preview = []

    unread_notifications_count = sum(1 for n in notifications_preview if getattr(n, 'unread', False))

    # Tasks: try to use the local Task model if available
    tasks = []
    try:
        from .models import Task
        if request.user.is_authenticated:
            tasks = list(Task.objects.filter(assigned_to=request.user).order_by('-deadline')[:10])
        else:
            tasks = list(Task.objects.all().order_by('-deadline')[:10])
    except Exception:
        tasks = []

    context = {
        'assigned_trees': _get('total_trees', 0),
        'volunteers': _get('total_volunteers', 0),
        'locations': _get('total_sites', 0),
        'completed_activities': _get('alive', 0),
        'tasks': tasks,
        'notifications_preview': notifications_preview,
        'unread_notifications_count': unread_notifications_count,
    }

    # augment with helper-provided data
    context['tasks'] = _get_tasks_for_user(request.user)
    context['notifications_preview'] = _get_notifications_for_user(request.user)
    context['unread_notifications_count'] = sum(1 for n in context['notifications_preview'] if getattr(n, 'unread', False))

    return render(request, 'dashboard/dashboard_field.html', context)


def _build_summary_context(request):
    """Return a small, template-friendly context dict using get_dashboard_summary.

    This centralizes how dashboards consume summary metrics so templates get
    consistent variable names like `total_trees` and `total_volunteers`.
    """
    cache_key = f"dashboard_summary_view_{request.user.id if request.user.is_authenticated else 'anon'}"
    summary = cache.get(cache_key)
    if summary is None:
        try:
            summary = get_dashboard_summary(user=request.user if request.user.is_authenticated else None)
        except Exception:
            summary = {}
        cache.set(cache_key, summary, 60 * 5)

    def _get(k, default=0):
        if not summary:
            return default
        if isinstance(summary, dict):
            return summary.get(k, default)
        return getattr(summary, k, default)

    return {
        'total_trees': _get('total_trees', 0),
        'total_volunteers': _get('total_volunteers', 0),
        'total_sites': _get('total_sites', 0),
        'alive': _get('alive', 0),
        'summary': summary,
    }


def _get_tasks_for_user(user, limit=10):
    try:
        from .models import Task
        if user and user.is_authenticated:
            return list(Task.objects.filter(assigned_to=user).order_by('-deadline')[:limit])
        return list(Task.objects.all().order_by('-deadline')[:limit])
    except Exception:
        return []


def _get_notifications_for_user(user, limit=5):
    try:
        from notifications.models import Notification
        if user and user.is_authenticated:
            qs = Notification.objects.filter(recipient=user).order_by('-created_at')[:limit]
        else:
            qs = Notification.objects.all().order_by('-created_at')[:limit]
        return list(qs)
    except Exception:
        return []


def assigned_tasks(request):
    """Simple page that lists tasks/assignments for the current user or all tasks for staff."""
    try:
        from .models import Task
        if request.user.is_authenticated:
            qs = Task.objects.filter(assigned_to=request.user).order_by('-deadline')
        else:
            qs = Task.objects.none()
    except Exception:
        qs = []

    return render(request, 'dashboard/assigned_tasks.html', {'tasks': qs})


def volunteers_list(request):
    """List volunteers - minimal implementation used by dashboard sidebar links."""
    try:
        User = get_user_model()
        volunteers = User.objects.filter(role__in=('volunteer',)).order_by('username')[:200]
    except Exception:
        volunteers = []
    return render(request, 'dashboard/volunteers_list.html', {'volunteers': volunteers})


def my_contributions(request):
    """Minimal contributions view used by partner dashboard sidebar link in templates/tests."""
    # In a real implementation this would query partner-specific donations/contributions.
    contributions = []
    return render(request, 'dashboard/my_contributions.html', {'contributions': contributions})


def my_hours(request):
    """Minimal my_hours view used by volunteer dashboard sidebar link in templates/tests."""
    hours = []
    return render(request, 'dashboard/my_hours.html', {'hours': hours})


def dashboard_partner(request):
    ctx = _build_summary_context(request)
    ctx['tasks'] = _get_tasks_for_user(request.user)
    ctx['notifications_preview'] = _get_notifications_for_user(request.user)
    ctx['unread_notifications_count'] = sum(1 for n in ctx['notifications_preview'] if getattr(n, 'unread', False))
    return render(request, 'dashboard/dashboard_partner.html', ctx)


def dashboard_community(request):
    ctx = _build_summary_context(request)
    return render(request, 'dashboard/dashboard_community.html', ctx)


def dashboard_analytics(request):
    return render(request, 'dashboard/dashboard_analytics.html')


def dashboard_map(request):
    return render(request, 'dashboard/dashboard_map.html')


def dashboard_guest(request):
    """Render a lightweight guest dashboard with summary counts and previews.

    Provides safe defaults so the template can be rendered for anonymous users
    or when optional models (Event, Notification) are not present.
    """
    cache_key = f"dashboard_guest_view_{request.user.id if request.user.is_authenticated else 'anon'}"
    summary = cache.get(cache_key)
    if summary is None:
        try:
            summary = get_dashboard_summary(user=request.user if request.user.is_authenticated else None)
        except Exception:
            summary = {}
        cache.set(cache_key, summary, 60 * 2)

    # Helper to read both dict-like and object-like summary
    def get_summary_field(key, default=0):
        if not summary:
            return default
        if isinstance(summary, dict):
            return summary.get(key, default)
        return getattr(summary, key, default)

    # Try to fetch upcoming events and notifications if models exist. Fail safe to empty lists.
    upcoming_events = []
    notifications_preview = []
    try:
        # Import locally to avoid hard dependency if the app isn't present
        from monitoring.models import Event
        now = timezone.now()
        upcoming_events = list(Event.objects.filter(date__gte=now).order_by('date')[:3])
    except Exception:
        upcoming_events = []

    try:
        # Notifications app may provide a Notification model
        from notifications.models import Notification
        notifications_qs = Notification.objects.all().order_by('-created_at')[:5]
        notifications_preview = list(notifications_qs)
    except Exception:
        notifications_preview = []

    context = {
        'total_users': get_summary_field('total_users', getattr(User, 'objects', None) and User.objects.count() or 0),
        'total_trees': get_summary_field('total_trees', 0),
        'total_volunteers': get_summary_field('total_volunteers', 0),
        'upcoming_events': upcoming_events,
        'upcoming_events_count': len(upcoming_events),
        'notifications_preview': notifications_preview,
        'unread_notifications_count': sum(1 for n in notifications_preview if getattr(n, 'unread', False)),
    }

    return render(request, 'dashboard/dashboard_guest.html', context)


def dashboard_volunteer(request):
    """Render a volunteer-specific dashboard view with summary context.

    There is a dedicated template at `templates/dashboard/dashboard_volunteer.html`.
    """
    ctx = _build_summary_context(request)
    ctx['tasks'] = _get_tasks_for_user(request.user)
    ctx['notifications_preview'] = _get_notifications_for_user(request.user)
    ctx['unread_notifications_count'] = sum(1 for n in ctx['notifications_preview'] if getattr(n, 'unread', False))
    return render(request, 'dashboard/dashboard_volunteer.html', ctx)


def dashboard_project(request):
    ctx = _build_summary_context(request)
    # Render the project manager specific dashboard template
    return render(request, 'dashboard/dashboard_projectmanager.html', ctx)


def insights_dashboard(request):
    """Render the Insights page. Use the existing dashboard summary service when available
    to provide sensible defaults for the template variables.
    """
    cache_key = f"insights_summary_view_{request.user.id if request.user.is_authenticated else 'anon'}"
    summary = cache.get(cache_key)
    if summary is None:
        try:
            summary = get_dashboard_summary(user=request.user if request.user.is_authenticated else None)
        except Exception:
            summary = {}
        cache.set(cache_key, summary, 60 * 5)

    # Provide template-friendly defaults
    context = {
        'total_trees': getattr(summary, 'total_trees', summary.get('total_trees') if isinstance(summary, dict) else 0) if summary else 0,
        'total_volunteers': getattr(summary, 'total_volunteers', summary.get('total_volunteers') if isinstance(summary, dict) else 0) if summary else 0,
        'total_projects': getattr(summary, 'total_projects', summary.get('total_projects') if isinstance(summary, dict) else 0) if summary else 0,
        'total_donations': getattr(summary, 'total_donations', summary.get('total_donations') if isinstance(summary, dict) else 0) if summary else 0,
        'recent_insights': getattr(summary, 'recent_insights', summary.get('recent_insights') if isinstance(summary, dict) else []) if summary else [],
    }
    return render(request, 'insights/insights_dashboard.html', context)
