from django.shortcuts import render
from beneficiaries.models import PlantingSite
from trees.models import Tree
from django.utils import timezone
from django.db.models import Q, Exists, OuterRef


def location_map(request):
    """Render locations that have recent or future plantings.

    Recent: trees planted within the last 365 days.
    Future: trees with planting_date in the future (scheduled).
    """
    today = timezone.localdate()
    recent_cutoff = today - timezone.timedelta(days=365)

    # Sites with at least one tree planted recently or scheduled in future
    recent_trees = Tree.objects.filter(site=OuterRef('pk'), planting_date__gte=recent_cutoff)
    future_trees = Tree.objects.filter(site=OuterRef('pk'), planting_date__gte=today)

    sites = PlantingSite.objects.annotate(
        has_recent=Exists(recent_trees),
        has_future=Exists(future_trees),
    ).filter(Q(has_recent=True) | Q(has_future=True))

    return render(request, 'locations/location_map.html', {'all_sites': sites})
