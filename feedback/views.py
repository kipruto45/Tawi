from rest_framework import viewsets, permissions
from .models import Feedback
from .serializers import FeedbackSerializer
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FeedbackForm
from beneficiaries.models import Beneficiary

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def submit_feedback(request):
    """Simple web form for submitting feedback from dashboards."""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            # If no beneficiary provided, try to infer from user profile, else use first
            if not fb.beneficiary:
                beneficiary = None
                if request.user.is_authenticated:
                    profile = getattr(request.user, 'profile', None)
                    if profile and getattr(profile, 'organization', None):
                        beneficiary = Beneficiary.objects.filter(name__iexact=profile.organization).first()
                if not beneficiary:
                    beneficiary = Beneficiary.objects.first()
                fb.beneficiary = beneficiary
            fb.save()
            messages.success(request, 'Thank you — your feedback has been submitted.')
            return redirect('feedback:submit')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['submitted_by'] = request.user.get_full_name() or request.user.username
            initial['email'] = request.user.email
        form = FeedbackForm(initial=initial)
    return render(request, 'feedback/submit_feedback.html', {'form': form})
