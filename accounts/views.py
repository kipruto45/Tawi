from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileForm
from .models import Profile
from django.db import IntegrityError
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.conf import settings
from django.urls import NoReverseMatch, reverse
from django.contrib.auth.models import Group
import logging
from django.contrib import messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import RegisterSerializer, ProfileSerializer
from django.contrib.auth import get_user_model


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class UserViewSet(viewsets.ModelViewSet):
    # DRF router expects a `queryset` attribute to infer a basename. Use
    # `.none()` here to avoid import-time DB access while keeping the
    # attribute present. Actual queryset is provided by get_queryset().
    queryset = User.objects.none()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """Return queryset lazily to avoid creating QuerySet at import time.

        Creating QuerySet objects at module import can accidentally cause
        database access during app import (e.g. in migrations/tests). By
        returning the queryset from get_queryset we ensure it is only
        evaluated when the view is actually used.
        """
        return User.objects.all()


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        pform = ProfileForm(request.POST, request.FILES)
        if form.is_valid() and pform.is_valid():
            user = form.save()
            # Avoid duplicate Profile creation: a post_save signal may already
            # have created a Profile for this user. Use get_or_create and then
            # save the submitted ProfileForm into that instance.
            try:
                profile_obj, created = Profile.objects.get_or_create(user=user)
                pform = ProfileForm(request.POST, request.FILES, instance=profile_obj)
                if pform.is_valid():
                    pform.save()
            except IntegrityError:
                # If a race or DB issue occurs, fall back to best-effort save
                try:
                    profile = pform.save(commit=False)
                    profile.user = user
                    profile.save()
                except Exception:
                    pass

            # Prepare a human-friendly role label for the confirmation page.
            try:
                if hasattr(user, 'get_role_display') and callable(user.get_role_display):
                    try:
                        role_display = user.get_role_display()
                    except Exception:
                        role_display = getattr(user, 'role', '')
                else:
                    role_display = getattr(user, 'role', '')
            except Exception:
                role_display = getattr(user, 'role', '')

            # Add a success message that includes the assigned role and
            # redirect straight to the login page. The login template
            # renders messages so users will see immediate confirmation.
            try:
                messages.success(request, f"Registration complete. Role: {role_display}")
            except Exception:
                # fall back to a simpler message if formatting fails
                try:
                    messages.success(request, 'Registration complete. Please sign in.')
                except Exception:
                    pass
            # After successful registration, redirect to the login page and
            # include a query param so the login page can show a success
            # message and pre-select the assigned role in the login form.
            try:
                login_url = reverse('accounts:login')
            except Exception:
                # fallback to non-namespaced name if reverse fails
                try:
                    login_url = reverse('login')
                except Exception:
                    login_url = '/accounts/login/'

            try:
                # include role in the querystring so the login page can pre-select it
                return redirect(f"{login_url}?registered=1&role={user.role}")
            except Exception:
                return redirect(login_url)
        else:
            # Collect errors from both forms and add them to messages so the
            # template (which renders messages) can display them prominently.
            try:
                # user form errors
                for field, errs in form.errors.items():
                    # errs is a list-like object
                    for e in errs:
                        messages.error(request, f"{field}: {e}")
                # profile form errors
                for field, errs in pform.errors.items():
                    for e in errs:
                        messages.error(request, f"{field}: {e}")
                # non-field errors
                for e in form.non_field_errors():
                    messages.error(request, e)
                for e in pform.non_field_errors():
                    messages.error(request, e)
            except Exception:
                # If something unexpected happens formatting errors, fall
                # back to a generic message so users know registration failed.
                try:
                    messages.error(request, 'Registration failed due to invalid input. Please check the form and try again.')
                except Exception:
                    pass
    else:
        form = UserRegisterForm()
        pform = ProfileForm()

    # provide an initial_role context value so templates don't access
    # request.GET/POST directly (which can raise during template resolution)
    try:
        initial_role = request.GET.get('role') or request.POST.get('role')
    except Exception:
        initial_role = None

    return render(request, 'accounts/register.html', {'form': form, 'pform': pform, 'initial_role': initial_role})

@login_required
def profile_view(request):
    """Display the user's profile (read-only).

    The edit form is served by `profile_edit_view` to keep display and edit concerns separate.
    """
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    """Edit the authenticated user's profile.

    GET: render `accounts/profile_edit.html` with a ProfileForm.
    POST: validate and save, then redirect to the read-only profile view.
    """
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            try:
                messages.success(request, 'Profile updated.')
            except Exception:
                pass
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'profile': profile, 'form': form})

def user_list(request):
    users = User.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users})

def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'accounts/user_detail.html', {'user_obj': user})

def role_management(request):
    groups = Group.objects.all()
    # Only staff users should be able to change roles via this view
    if request.method == 'POST':
        try:
            if not (request.user.is_authenticated and (request.user.has_perm('accounts.manage_roles') or 'Admins' in set(request.user.groups.values_list('name', flat=True)))):
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect('role_management')
        except Exception:
            if not request.user.is_authenticated or not request.user.is_staff:
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect('role_management')

        email = request.POST.get('email') or request.POST.get('username')
        new_role = request.POST.get('role')
        UserModel = get_user_model()
        if not email or not new_role:
            messages.error(request, 'Email and role are required.')
            return redirect('role_management')

        # find user by email first, then by username
        try:
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(username__iexact=email)
            except UserModel.DoesNotExist:
                user = None

        if not user:
            messages.error(request, 'User not found.')
            return redirect('role_management')

        # validate role
        allowed = None
        try:
            allowed = [c[0] for c in UserModel.ROLE_CHOICES]
        except Exception:
            allowed = None

        if allowed is not None and new_role not in allowed:
            messages.error(request, 'Invalid role selected.')
            return redirect('role_management')

        old_role = getattr(user, 'role', None)
        user.role = new_role
        user.save()

        # audit log
        logger = logging.getLogger('accounts.role_changes')
        try:
            changer = getattr(request.user, 'username', 'anonymous')
            logger.info('role_change', extra={
                'changer': changer,
                'target_user': user.username,
                'old_role': old_role,
                'new_role': new_role,
                'ip': request.META.get('REMOTE_ADDR')
            })
        except Exception:
            pass

        messages.success(request, f"Updated role for {user.username} from {old_role} to {new_role}.")
        return redirect('role_management')

    return render(request, 'accounts/role_management.html', {'groups': groups})


def guest_dashboard(request):
    # redirect to the guest-specific dashboard route which renders
    # `dashboard/dashboard_guest.html` so the UX matches the 'Continue as Guest' link.
    return redirect('guest_dashboard')


def provider_login_shim(request, provider_name):
    """Shim view that tries to delegate to django-allauth's social login. If allauth
    is not installed, redirects back to the login page with an info message.
    """
    try:
        # allauth usually registers 'socialaccount_login'
        target = reverse('socialaccount_login', args=(provider_name,))
        return redirect(target)
    except NoReverseMatch:
        # not configured: return to login with an informational message
        try:
            messages.info(request, 'Social login for %s is not configured on this site.' % provider_name)
        except Exception:
            pass
        return redirect('login')


class CustomLoginView(DjangoLoginView):
    """Custom LoginView that respects a 'role' POST field and a 'remember' checkbox.

    - If 'remember' is present, session expiry is set to 2 weeks; otherwise use session cookie expiry.
    - If 'role' is provided it redirects to a role-specific dashboard name when possible.
    """
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        """Add a safe 'initial_role' value to the template context.

        We compute this server-side using QueryDict.get() so templates don't
        attempt to index into request.GET/POST directly (which raises
        MultiValueDictKeyError when the key is missing).
        """
        ctx = super().get_context_data(**kwargs)
        role = None
        try:
            role = self.request.GET.get('role') or self.request.POST.get('role')
        except Exception:
            role = None
        ctx['initial_role'] = role
        # expose an explicit 'registered' flag from the querystring so templates
        # don't need to index into request.GET directly which can raise in
        # template variable resolution in some edge-cases.
        try:
            ctx['registered'] = self.request.GET.get('registered')
        except Exception:
            ctx['registered'] = None
        return ctx
    def form_valid(self, form):
        # apply remember-me behavior
        remember = self.request.POST.get('remember')
        if remember:
            # configurable expiry (default 2 weeks)
            expiry = getattr(settings, 'LOGIN_REMEMBER_SECONDS', 1209600)
            self.request.session.set_expiry(int(expiry))
        else:
            # browser-length session
            self.request.session.set_expiry(0)

        # call parent to log the user in and get default response
        response = super().form_valid(form)

        # If the login flow included a `next` parameter (user originally
        # attempted to access a protected page), respect that explicit
        # destination and return it immediately. Otherwise proceed to
        # role-based redirect logic below.
        try:
            next_url = self.get_redirect_url()
        except Exception:
            next_url = None

        if next_url:
            return redirect(next_url)

        # role-based redirect based on authenticated user.role
        # account model stores roles like 'admin', 'field_officer', 'volunteer', 'beneficiary'
        # Normalize legacy alias keys to canonical keys before mapping so stored
        # values like 'field' or 'partner_institution' still resolve correctly.
        user_role = getattr(self.request.user, 'role', None)
        alias_map = {
            'field': 'field_officer',
            'partner_institution': 'partner',
        }
        norm_role = alias_map.get(user_role, user_role)

        # Use top-level compatibility names where many templates and tests
        # expect un-namespaced reverses (for historical reasons). These
        # aliases are defined in `tawi_project/urls.py` and map to the
        # canonical dashboard views.
        role_map = {
            'admin': 'admin_dashboard',
            'field_officer': 'dashboard_field',
            'volunteer': 'dashboard_volunteer',
            'beneficiary': 'dashboard:dashboard',
            # canonical partner key
            'partner': 'dashboard_partner',
            'guest': 'guest_dashboard',
            'community': 'dashboard_community',
            'project_manager': 'dashboard_project',
        }
        target = role_map.get(norm_role)

        # initialize logger
        logger = logging.getLogger('accounts.login')

        # If no mapping from role, fall back to permissions/groups
        if not target:
            # permission checks (more granular): check specific permissions first
            try:
                if self.request.user.has_perm('accounts.can_view_admin') or getattr(self.request.user, 'is_superuser', False):
                    target = 'admin_dashboard'
                elif self.request.user.has_perm('accounts.can_view_field_dashboard'):
                    target = 'dashboard_field'
                elif self.request.user.has_perm('accounts.can_view_partner_dashboard'):
                    target = 'dashboard_partner'
            except Exception:
                # some auth backends may raise; ignore and fallback to groups
                pass

            if not target:
                # check groups as another fallback
                user_groups = set(self.request.user.groups.values_list('name', flat=True))
                if 'Admins' in user_groups:
                    target = 'admin_dashboard'
                elif 'Field Officers' in user_groups:
                    target = 'dashboard_field'
                elif 'Partners' in user_groups:
                    target = 'dashboard_partner'
                elif 'Project Managers' in user_groups:
                    target = 'dashboard_project'
                elif 'Volunteers' in user_groups:
                    target = 'dashboard_volunteer'
                elif 'Guests' in user_groups:
                    target = 'guest_dashboard'

        # Log redirect decision for analytics/auditing
        try:
            logger.info(
                'login_redirect',
                extra={
                    'username': getattr(self.request.user, 'username', None),
                    'role': user_role,
                    'target': target,
                    'method': 'role' if user_role else 'group/perm',
                    'ip': self.request.META.get('REMOTE_ADDR')
                }
            )
        except Exception:
            # don't let logging interfere with login
            pass

        # Log redirect decision (no sensitive data). Session key may be None
        # until the session is saved; include it when available to help
        # diagnose session persistence issues in environments where cookies
        # are lost.
        try:
            logger = logging.getLogger('accounts.login')
            session_key = getattr(self.request.session, 'session_key', None)
            logger.info('login_redirect_decision', extra={
                'username': getattr(self.request.user, 'username', None),
                'role': getattr(self.request.user, 'role', None),
                'target': target,
                'next_url': next_url,
                'session_key': session_key,
            })
        except Exception:
            # Don't let logging interfere with login flow
            pass

        if target:
            try:
                return redirect(target)
            except NoReverseMatch:
                # target not defined; fall back to default response
                return response

        return response


def post_login_redirect(request):
    """Central post-login redirect that other auth flows can use.

    This inspects the authenticated user's role and redirects to a role-specific
    dashboard. It mirrors the mapping logic used in CustomLoginView.form_valid to
    ensure consistent behavior for social auth or other login flows that rely on
    LOGIN_REDIRECT_URL.
    """
    # If user is not authenticated, send them to the generic dashboard landing (namespaced)
    if not request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    user_role = getattr(request.user, 'role', None)
    alias_map = {
        'field': 'field_officer',
        'partner_institution': 'partner',
    }
    norm_role = alias_map.get(user_role, user_role)

    role_map = {
        'admin': 'admin_dashboard',
        'field_officer': 'dashboard_field',
        'volunteer': 'dashboard_volunteer',
        'beneficiary': 'dashboard:dashboard',
        'partner': 'dashboard_partner',
        'guest': 'guest_dashboard',
        'community': 'dashboard_community',
        'project_manager': 'dashboard_project',
    }

    target = role_map.get(norm_role)

    # Fallback permission/group checks (keep in sync with CustomLoginView)
    try:
        if not target:
            if request.user.has_perm('accounts.can_view_admin') or getattr(request.user, 'is_superuser', False):
                target = 'admin_dashboard'
            elif request.user.has_perm('accounts.can_view_field_dashboard'):
                target = 'dashboard_field'
            elif request.user.has_perm('accounts.can_view_partner_dashboard'):
                target = 'dashboard_partner'
    except Exception:
        pass

    if not target:
        user_groups = set(request.user.groups.values_list('name', flat=True))
        if 'Admins' in user_groups:
            target = 'admin_dashboard'
        elif 'Field Officers' in user_groups:
            target = 'dashboard_field'
        elif 'Partners' in user_groups:
            target = 'dashboard_partner'
        elif 'Project Managers' in user_groups:
            target = 'dashboard_project'
        elif 'Volunteers' in user_groups:
            target = 'dashboard_volunteer'
        elif 'Guests' in user_groups:
            target = 'guest_dashboard'

    # Final fallback
    if not target:
        # default to the namespaced landing if no other target available
        target = 'dashboard:dashboard'

    try:
        return redirect(target)
    except NoReverseMatch:
        return redirect('dashboard:dashboard')


def debug_session_info(request):
    """Dev-only endpoint that returns basic session/auth info to help
    diagnose login/session persistence issues.

    Access control: only staff users or when DEBUG=True are allowed to use
    this in order to avoid exposing user info in production.
    """
    from django.http import JsonResponse
    try:
        allowed = getattr(settings, 'DEBUG', False) or (request.user.is_authenticated and getattr(request.user, 'is_staff', False))
    except Exception:
        allowed = getattr(settings, 'DEBUG', False)

    if not allowed:
        return redirect('accounts:login')

    try:
        session_key = getattr(request.session, 'session_key', None)
    except Exception:
        session_key = None

    try:
        username = getattr(request.user, 'username', None)
        role = getattr(request.user, 'role', None)
        is_auth = request.user.is_authenticated
        groups = list(request.user.groups.values_list('name', flat=True)) if is_auth else []
    except Exception:
        username = None
        role = None
        is_auth = False
        groups = []

    data = {
        'is_authenticated': bool(is_auth),
        'username': username,
        'role': role,
        'groups': groups,
        'session_key': session_key,
        'cookies': {k: request.COOKIES.get(k) for k in ('sessionid', settings.SESSION_COOKIE_NAME) if request.COOKIES.get(k)},
    }
    return JsonResponse(data)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_register(request):
    ser = RegisterSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    user = ser.save()
    return Response({'id': user.id, 'username': user.username})


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def api_profile(request):
    # Ensure a Profile exists for the authenticated user; create lazily if missing.
    try:
        profile = getattr(request.user, 'profile', None)
    except Exception:
        profile = None

    if profile is None:
        try:
            from .models import Profile
            profile, _ = Profile.objects.get_or_create(user=request.user)
        except Exception:
            # If creation fails for any reason, return a safe empty response
            return Response({'detail': 'profile unavailable'}, status=503)

    if request.method == 'GET':
        return Response(ProfileSerializer(profile).data)
    else:
        ser = ProfileSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)


# Role-check API: returns whether a user exists and whether their stored role matches the provided role.
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_role_check(request):
    # Be liberal in accepting JSON or form-encoded; handle malformed JSON gracefully
    try:
        if request.content_type == 'application/json':
            payload = request.data
        else:
            # request.data already parses form-encoded; still guard
            payload = request.data
    except Exception:
        return Response({'exists': False, 'matches': False, 'user_role': None})

    username = payload.get('username') if payload else None
    role = payload.get('role') if payload else None
    UserModel = get_user_model()
    if not username:
        return Response({'exists': False, 'matches': False, 'user_role': None})

    user = None
    try:
        user = UserModel.objects.get(username__iexact=username)
    except UserModel.DoesNotExist:
        # try by email as a convenience
        try:
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            return Response({'exists': False, 'matches': False, 'user_role': None})

    user_role = getattr(user, 'role', None)
    # Normalize legacy aliases to canonical role keys before comparing.
    alias_map = {
        'admin': 'admin',
        'field': 'field_officer',
        'partner_institution': 'partner',
        'project_manager': 'project_manager',
        'volunteer': 'volunteer',
        'guest': 'guest',
    }
    norm_user_role = alias_map.get(user_role, user_role)
    norm_role = alias_map.get(role, role)
    matches = (norm_user_role == norm_role)
    return Response({'exists': True, 'matches': matches, 'user_role': user_role})


# Admin-only endpoint to change a user's role safely.
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def api_change_role(request):
    username = request.data.get('username')
    new_role = request.data.get('role')
    UserModel = get_user_model()
    if not username or not new_role:
        return Response({'detail': 'username and role required'}, status=400)

    try:
        user = UserModel.objects.get(username__iexact=username)
    except UserModel.DoesNotExist:
        return Response({'detail': 'user not found'}, status=404)

    # validate role against canonical choices if available (prefer CANONICAL_ROLES)
    choices = getattr(UserModel, 'CANONICAL_ROLES', None) or getattr(UserModel, 'ROLE_CHOICES', [])
    allowed = [c[0] for c in choices]

    if new_role not in allowed:
        return Response({'detail': 'invalid role'}, status=400)

    old_role = getattr(user, 'role', None)
    user.role = new_role
    user.save()

    # Audit logging: who made the change, timestamp, old/new role
    logger = logging.getLogger('accounts.role_changes')
    try:
        changer = getattr(request.user, 'username', 'anonymous')
        logger.info('role_change', extra={
            'changer': changer,
            'target_user': user.username,
            'old_role': old_role,
            'new_role': new_role,
            'ip': request.META.get('REMOTE_ADDR')
        })
    except Exception:
        # swallow logging errors
        pass

    return Response({'ok': True, 'username': user.username, 'role': user.role})
