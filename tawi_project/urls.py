from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views
from rest_framework import routers
from accounts.views import UserViewSet
from accounts.views import register as accounts_register, guest_dashboard as accounts_guest_dashboard, profile_view as accounts_profile, profile_edit_view as accounts_profile_edit
from accounts.views import api_role_check as accounts_api_role_check, api_change_role as accounts_api_change_role
from accounts.views import api_register as accounts_api_register, api_profile as accounts_api_profile
from beneficiaries.views import BeneficiaryViewSet, PlantingSiteViewSet
from trees.views import TreeViewSet, TreeUpdateViewSet, TreeSpeciesViewSet
from monitoring.views import FollowUpViewSet
from monitoring.views import MonitoringReportViewSet
from feedback.views import FeedbackViewSet
from reports.views import summary_stats
from reports import views as reports_views
from reports.views_api import GeneratedReportViewSet
from dashboard.views import dashboard, dashboard_admin, dashboard_field, dashboard_partner, dashboard_community, dashboard_analytics, dashboard_map, dashboard_guest, assigned_tasks, my_contributions, my_hours
from core.views import core_dashboard, core_analytics
from core.views_api import PostViewSet, SiteConfigViewSet
from monitoring import views as monitoring_views
from events import views as events_views
from trees import web_public_views as trees_public_views
from notifications import views as notifications_views
from .fallback_views import noop, my_trees_view, my_tasks_view, role_management_view
import tawi_project.fallback_views as fallback_views
from accounts import views as accounts_views
try:
    from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
except Exception:
    TokenObtainPairView = None
    TokenRefreshView = None
router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'site-config', SiteConfigViewSet)
router.register(r'users', UserViewSet)
router.register(r'beneficiaries', BeneficiaryViewSet)
router.register(r'planting-sites', PlantingSiteViewSet)
router.register(r'trees', TreeViewSet)
router.register(r'tree-updates', TreeUpdateViewSet)
router.register(r'tree-species', TreeSpeciesViewSet)
router.register(r'followups', FollowUpViewSet)
router.register(r'monitoring', MonitoringReportViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'reports/generated', GeneratedReportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/media/', include('media_app.urls')),
    path('api/qrcodes/', include('qrcodes.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/reports/summary/', summary_stats, name='reports-summary'),
    # Include the dashboard app with an explicit namespace so templates
    # that use the 'dashboard:' namespaced reverses resolve correctly.
    path('dashboard/', include(('dashboard.urls', 'dashboard'), namespace='dashboard')),
    # Events app (public listing for guests)
    path('events/', include(('events.urls', 'events'), namespace='events')),
    # Top-level aliases used by templates (non-namespaced)
    path('upcoming-events/', events_views.upcoming_events, name='upcoming_events'),
    path('trees/', include(('trees.urls', 'trees'), namespace='trees')),
    # non-namespaced alias for templates that use {% url 'trees' %}
    path('trees/all/', trees_public_views.trees_planted_public, name='trees'),
    path('trees/planted/', trees_public_views.trees_planted_public, name='trees_planted_public'),
    # Note: templates should use the 'trees:' namespace (e.g. {% url 'trees:tree_list' %})
    # Expose a few accounts names at the top-level name registry so legacy template
    # and tests that call reverse('register') or reverse('guest_dashboard') will
    # resolve successfully. Place these before including core.urls so they take
    # precedence over any similarly-named routes defined in included apps.
    path('accounts/register/', accounts_register, name='register'),
    path('guest/', dashboard_guest, name='guest_dashboard'),
    path('volunteer-signup/', accounts_register, name='volunteer_sign_up'),
    path('profile/', accounts_profile, name='profile'),
    path('profile/edit/', accounts_profile_edit, name='profile_edit'),
    path('', include(('core.urls', 'core'), namespace='core')),
    # Media app public gallery at top-level so templates can use reverse('media_list')
    # and templates that reference the media_app namespace (e.g. {% url 'media_app:media_list' %})
    # will resolve. We include with an explicit namespace.
    path('media/', include(('media_app.urls', 'media_app'), namespace='media_app')),
    path('core/dashboard/', core_dashboard, name='core_dashboard'),
    path('core/analytics/', core_analytics, name='core_analytics'),
    # Include the accounts app under the 'accounts' namespace to avoid
    # name collisions with top-level aliases we expose below. This keeps
    # legacy template reverses working while allowing explicit top-level
    # aliases (e.g. 'guest_dashboard') to resolve to the routes we want
    # during tests and in templates.
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    # fallback aliases used by templates in tests
    path('role-management/', role_management_view, name='role_management'),
    path('my/tasks/simple/', my_tasks_view, name='my_tasks'),
    path('my/trees/simple/', my_trees_view, name='my_trees'),
    # Top-level aliases used by templates
    path('users/', accounts_views.user_list, name='user_list'),
    path('my/hours/', my_hours, name='my_hours'),
    path('feedback/', include(('feedback.urls', 'feedback'), namespace='feedback')),
    # (top-level aliases moved earlier in the file)
    path('accounts/api/role_check/', accounts_api_role_check, name='api_role_check'),
    path('accounts/api/change_role/', accounts_api_change_role, name='api_change_role'),
    path('accounts/api/register/', accounts_api_register, name='api_register'),
    path('accounts/api/profile/', accounts_api_profile, name='api_profile'),
    path('donations/', include(('donations.urls', 'donations'), namespace='donations')),
    path('locations/', include(('locations.urls', 'locations'), namespace='locations')),
    # Convenience route for the monitoring web dashboard used by the admin sidebar
    path('monitoring/dashboard/', monitoring_views.monitoring_dashboard_view, name='monitoring_dashboard'),
    # Explicitly wire the password reset flow to use the provided templates in templates/accounts
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    # django built-in auth views (login/logout and other auth helpers)
    path('accounts/', include('django.contrib.auth.urls')),
    path('notifications/', include('notifications.urls')),
    # public notifications alias for guests
    path('notifications/public/', notifications_views.notifications_public, name='notifications_public'),
    path('qrcodes/', include('qrcodes.urls')),
    # top-level aliases for legacy template reverses (messages & qrcodes)
    path('messages/compose/', fallback_views.message_compose_view, name='message_compose'),
    path('messages/<int:pk>/', fallback_views.message_detail_view, name='message_detail'),
    path('messages/<int:pk>/reply/', fallback_views.message_reply_view, name='message_reply'),
    path('messages/<int:pk>/delete/', fallback_views.message_delete_view, name='message_delete'),
    # qrcodes top-level aliases used by older templates
    path('qrcodes/generate/', fallback_views.qrcodes_generate_view, name='qrcodes_generate'),
    path('qrcodes/list/', fallback_views.qrcodes_list_view, name='qrcodes_list'),
    path('qrcodes/<int:pk>/', fallback_views.qrcodes_detail_view, name='qrcodes_detail'),
    # Additional fallback aliases to satisfy legacy template reverses
    path('qrcodes/<int:pk>/edit/', fallback_views.qrcodes_edit_view, name='qrcodes_edit'),
    path('qrcodes/<int:pk>/delete/', fallback_views.qrcodes_delete_view, name='qrcodes_delete'),
    path('qrcodes/history/', fallback_views.qrcode_history_view, name='qrcode_history'),
    # Include reports app with namespace so templates using 'reports:' resolve
    path('reports/', include(('reports.urls', 'reports'), namespace='reports'),
    ),
    # Provide a simple non-namespaced alias used by some dashboard templates.
    # Templates refer to the name 'reports' so expose it here to avoid
    # NoReverseMatch during template rendering in tests.
    path('reports/', reports_views.report_list_view, name='reports'),
    # Top-level alias for template reverses used in dashboard templates
    path('my/tasks/', assigned_tasks, name='my_tasks'),
    # JWT token endpoints (optional; requires djangorestframework-simplejwt)
]

# Lightweight fallbacks for a small set of template names that are referenced
# by archived/legacy templates but not implemented as full features. These
# avoid NoReverseMatch when rendering templates in tests or when older UI
# fragments are still present.
urlpatterns += [
    path('projects/list/', fallback_views.noop, name='project_list'),
    path('projects/progress/', fallback_views.noop, name='project_progress'),
    path('projects/volunteers/', fallback_views.noop, name='project_volunteers'),

    path('contributions/<int:pk>/', fallback_views.noop, name='contribution_detail'),
    path('contributions/<int:pk>/delete/', fallback_views.noop, name='contribution_delete'),

    path('locations/<int:pk>/delete/', fallback_views.noop, name='delete_site'),
    path('locations/<int:pk>/edit/', fallback_views.noop, name='edit_site'),

    path('notifications/dropdown/', lambda r: __import__('django.shortcuts').shortcuts.render(r, 'notifications/notifications_dropdown.html', {'notifications': r.user.notifications.all() if r.user.is_authenticated else []}), name='notifications_dropdown'),
    path('notifications/detail/<int:pk>/', notifications_views.notifications_page, name='notifications_detail'),
    path('notifications/mark_read/<int:pk>/', notifications_views.notifications_mark, name='mark_read'),
]

# If django-allauth is installed, include its URLs so the provider login endpoints
# are available at /accounts/. This is done after the main urlpatterns list to
# avoid syntax issues when allauth is not installed in the environment.
try:
    import allauth  # noqa: F401 - presence check
    urlpatterns += [path('accounts/', include('allauth.urls'))]
except Exception:
    # allauth not installed; skip adding its URLs
    pass

if TokenObtainPairView and TokenRefreshView:
    urlpatterns += [
        path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]

# Optional two-factor authentication support
# Only mount the two_factor URL patterns when USE_2FA is explicitly enabled
# via settings. This avoids introducing similarly-named routes (for example
# a top-level 'login' name) into the global URL namespace during tests or
# when the feature is not enabled.
if getattr(settings, 'USE_2FA', False):
    try:
        import importlib.util
        if importlib.util.find_spec('two_factor') is not None:
            # Include two_factor urls under the 'two_factor' namespace to avoid
            # clobbering globally-named URL patterns (for example 'login') which
            # could change the behavior of existing tests and templates that
            # expect the non-2FA login endpoint. Using include with a namespace
            # keeps the two-factor names scoped and prevents reverse('login')
            # from resolving to the two-factor login unless explicitly namespaced.
            urlpatterns += [path('', include('two_factor.urls', namespace='two_factor'))]
    except Exception:
        # two_factor not installed or not configured; continue without 2FA routes
        pass

