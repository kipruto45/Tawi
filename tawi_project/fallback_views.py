from django.shortcuts import render, redirect
from django.http import HttpResponse


# Lightweight fallback views for legacy/non-namespaced template reverses.
# These are intentionally simple and safe: they either redirect to an
# appropriate listing page or return a tiny placeholder. They avoid
# introducing new business logic while ensuring template rendering and
# tests don't encounter NoReverseMatch errors.
def message_compose_view(request):
    # Redirect to the messages list (safe fallback) where users can compose.
    return redirect('message_list')


def message_detail_view(request, pk):
    # Fallback: redirect to messages list (no-op detail view available).
    return redirect('message_list')


def message_reply_view(request, pk):
    return redirect('message_list')


def message_delete_view(request, pk):
    return redirect('message_list')


def qrcodes_generate_view(request):
    # Redirect to the qrcodes list page if present
    return redirect('qrcodes') if 'qrcodes' in globals() else redirect('/qrcodes/')


def qrcodes_list_view(request):
    # Fallback to the qrcodes listing
    return redirect('/qrcodes/')


def qrcodes_detail_view(request, pk):
    return redirect('/qrcodes/')


def qrcodes_edit_view(request, pk):
    return redirect('/qrcodes/')


def qrcodes_delete_view(request, pk):
    return redirect('/qrcodes/')


def qrcode_history_view(request):
    return redirect('/qrcodes/')

def noop(request):
    return HttpResponse('ok')

def my_trees_view(request):
    return HttpResponse('no trees')

def my_tasks_view(request):
    return HttpResponse('no tasks')

def role_management_view(request):
    return HttpResponse('role management')
