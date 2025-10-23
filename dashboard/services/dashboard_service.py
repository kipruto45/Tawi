from datetime import date
from collections import defaultdict
from typing import Dict, List, Any
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from trees.models import Tree, TreeSpecies
from beneficiaries.models import PlantingSite, Beneficiary
from monitoring.models import FollowUp


def _month_label(d):
    return d.strftime('%b')


def get_dashboard_summary(user=None) -> Dict[str, Any]:
    """Aggregate key dashboard metrics.

    Returns a dict with total_trees, avg_survival_rate, total_sites, total_beneficiaries,
    monthly_trends, species_distribution, top_regions.
    Applies simple role-based filtering when `user` is provided (field officers see their county).
    """
    qs = Tree.objects.select_related('species', 'beneficiary')

    # role-based filtering (simple): if user is field_officer, filter by profile.county
    if user is not None and hasattr(user, 'role') and user.role == 'field_officer':
        county = getattr(getattr(user, 'profile', None), 'county', None)
        if county:
            qs = qs.filter(beneficiary__address__icontains=county)

    total_trees = qs.aggregate(total=Sum('number_of_seedlings'))['total'] or 0

    # survival from latest TreeUpdate status if available, otherwise tree.status
    alive = qs.filter(status='alive').aggregate(total=Sum('number_of_seedlings'))['total'] or 0
    dead = qs.filter(status='dead').aggregate(total=Sum('number_of_seedlings'))['total'] or 0
    avg_survival_rate = 0.0
    if total_trees:
        avg_survival_rate = round((alive / total_trees) * 100, 2)

    total_sites = PlantingSite.objects.count()
    total_beneficiaries = Beneficiary.objects.count()

    # monthly planting trends (last 12 months)
    trends_qs = (
        qs.annotate(month=TruncMonth('planting_date'))
        .values('month')
        .annotate(count=Sum('number_of_seedlings'))
        .order_by('month')
    )
    monthly_trends: List[Dict[str, Any]] = []
    for row in trends_qs:
        monthly_trends.append({'month': _month_label(row['month']), 'count': row['count'] or 0})

    # species distribution
    species_qs = (
        qs.values('species__name')
        .annotate(count=Sum('number_of_seedlings'))
        .order_by('-count')
    )
    species_distribution = [
        {'species': r['species__name'] or 'Unknown', 'count': r['count'] or 0} for r in species_qs
    ]

    # top regions: heuristically use beneficiary.address -> county
    regions_qs = (
        qs.values('beneficiary__address')
        .annotate(count=Sum('number_of_seedlings'))
        .order_by('-count')[:5]
    )
    top_regions = [{'region': r['beneficiary__address'] or 'Unknown', 'count': r['count'] or 0} for r in regions_qs]

    return {
        'total_trees': total_trees,
        'alive': alive,
        'dead': dead,
        'avg_survival_rate': avg_survival_rate,
        'total_sites': total_sites,
        'total_beneficiaries': total_beneficiaries,
        'monthly_trends': monthly_trends,
        'species_distribution': species_distribution,
        'top_regions': top_regions,
    }
