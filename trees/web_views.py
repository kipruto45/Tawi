from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Tree

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


@login_required
@staff_required
def tree_list(request):
    trees = Tree.objects.all().order_by('-planting_date')
    return render(request, 'trees/tree_list.html', {'trees': trees})


@login_required
@staff_required
def tree_detail(request, pk):
    tree = get_object_or_404(Tree, pk=pk)
    return render(request, 'trees/tree_detail.html', {'tree': tree})


@login_required
@staff_required
def tree_add(request):
    # simple redirect to DRF or admin for now; real form not implemented here
    from django.urls import reverse
    return redirect(reverse('admin:trees_tree_add'))


@login_required
@staff_required
def tree_edit(request, pk):
    from django.urls import reverse
    return redirect(reverse('admin:trees_tree_change', args=[pk]))


@login_required
@staff_required
def tree_delete(request, pk):
    from django.urls import reverse
    return redirect(reverse('admin:trees_tree_delete', args=[pk]))


@login_required
@staff_required
def trees_dashboard_view(request):
    trees = Tree.objects.all().order_by('-planting_date')
    return render(request, 'trees/trees_dashboard.html', {'trees': trees})


@login_required
@staff_required
def tree_add_view(request):
    if request.method == 'POST':
        # This placeholder will create a Tree minimally if fields present
        name = request.POST.get('name')
        species = request.POST.get('species')
        planting_date = request.POST.get('planting_date')
        location = request.POST.get('location')
        if name:
            Tree.objects.create(name=name, species=species or '', planting_date=planting_date or None, location=location or '')
            return redirect('trees:tree_list')
    return render(request, 'trees/tree_add.html')


@login_required
@staff_required
def growth_record_add_view(request):
    if request.method == 'POST':
        tree_id = request.POST.get('tree')
        height = request.POST.get('height')
        health_status = request.POST.get('health_status')
        notes = request.POST.get('notes')
        # Minimal placeholder: no GrowthRecord model assumed; redirect back
        return redirect('trees:tree_list')
    trees = Tree.objects.all()
    return render(request, 'trees/growth_record_add.html', {'trees': trees})
