from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Event


def upcoming_events(request):
    today = timezone.localdate()
    events = Event.objects.filter(date__gte=today).order_by('date')
    return render(request, 'events/upcoming_list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def participate(request, pk):
    # Minimal participate action: redirect to event detail with a success flag
    # Real participation model can be added later.
    return redirect(reverse('upcoming_event_detail', args=[pk]) + '?joined=1')
