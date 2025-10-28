from django.shortcuts import render, redirect, get_object_or_404
from beneficiaries.models import PlantingSite
from trees.models import Tree
from django.utils import timezone
from django.db.models import Q, Exists, OuterRef
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import PlantingSiteForm
from django.urls import reverse


def location_map(request):
    """Render locations that have recent or future plantings.

    Recent: trees planted within the last 365 days.
    Future: trees with planting_date in the future (scheduled).
    """
    today = timezone.localdate()
    recent_cutoff = today - timezone.timedelta(days=365)

    # Sites with at least one tree planted recently or scheduled in future.
    # Tree model does not have a direct `site` FK; trees are linked to a Beneficiary,
    # and PlantingSite links to a Beneficiary via `related_name='sites'`.
    # Use the beneficiary->sites reverse relation to check for trees at a site.
    recent_trees = Tree.objects.filter(beneficiary__sites__pk=OuterRef('pk'), planting_date__gte=recent_cutoff)
    future_trees = Tree.objects.filter(beneficiary__sites__pk=OuterRef('pk'), planting_date__gte=today)

    sites = PlantingSite.objects.annotate(
        has_recent=Exists(recent_trees),
        has_future=Exists(future_trees),
    ).filter(Q(has_recent=True) | Q(has_future=True))

    # Render an admin-focused management UI for admins; all other users see
    # a simplified public listing (`user_location.html`). This keeps the same
    # URL (`/locations/`) but adapts the view by role.
    template = 'locations/location_map.html' if _is_admin(request.user) else 'locations/user_location.html'
    return render(request, template, {'all_sites': sites})


def view_site(request, pk):
    """Show a single planting site (public). Admins can still view this page.

    For compatibility with older templates that expect attributes like
    `location`, `trees_needed`, and `status` on the site object, attach
    these attributes derived from the PlantingSite model if they are missing.
    """
    site = get_object_or_404(PlantingSite, pk=pk)

    # Attach compatibility attributes if not present on the model instance.
    if not hasattr(site, 'location'):
        setattr(site, 'location', site.name or site.address or '')
    if not hasattr(site, 'trees_needed'):
        # best-effort: if the site has related trees with a target count we
        # could compute it; for now use 0 as a safe default.
        setattr(site, 'trees_needed', getattr(site, 'trees_needed', 0))
    if not hasattr(site, 'status'):
        setattr(site, 'status', getattr(site, 'status', 'Upcoming'))

    return render(request, 'locations/view_site.html', {'site': site})


def _is_admin(user):
    """Return True if the user has the 'manage_sites' permission on the beneficiaries app.

    This is intentionally permission-based to allow granular control via Django's
    permission system rather than relying on `is_staff` or a `role` string.
    Permission: `beneficiaries.manage_sites`
    """
    try:
        return bool(user and user.is_authenticated and user.has_perm('beneficiaries.manage_sites'))
    except Exception:
        return False


@user_passes_test(_is_admin)
def add_site(request):
    """Add a new PlantingSite (admin only)."""
    if request.method == 'POST':
        form = PlantingSiteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Planting site added.')
            return redirect('locations:location_map')
    else:
        form = PlantingSiteForm()
    return render(request, 'locations/add_site.html', {'form': form})


@user_passes_test(_is_admin)
def edit_site(request, pk):
    site = get_object_or_404(PlantingSite, pk=pk)
    if request.method == 'POST':
        form = PlantingSiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, 'Planting site updated.')
            return redirect('locations:location_map')
    else:
        form = PlantingSiteForm(instance=site)
    return render(request, 'locations/edit_site.html', {'form': form, 'site': site})


@user_passes_test(_is_admin)
@require_POST
def delete_site(request, pk):
    """Delete a PlantingSite. This endpoint only accepts POST to avoid
    accidental deletions via GET links. Templates should submit a small
    inline POST form with CSRF token.
    """
    site = get_object_or_404(PlantingSite, pk=pk)
    try:
        site.delete()
        messages.success(request, 'Planting site deleted.')
    except Exception:
        messages.error(request, 'Could not delete planting site.')
    return redirect('locations:location_map')
