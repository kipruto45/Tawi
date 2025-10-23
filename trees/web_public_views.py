from django.shortcuts import render
from .models import Tree


def trees_planted_public(request):
    # Public listing of planted trees (non-destructive)
    trees = Tree.objects.select_related('species').all().order_by('-planting_date')[:200]
    return render(request, 'trees/trees_public_list.html', {'trees': trees})
