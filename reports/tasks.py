from celery import shared_task
from django.utils import timezone
from .models import GeneratedReport
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings


@shared_task
def scheduled_generate_report(name, report_type='summary', filters=None):
    # lightweight scheduled generation using the API's generate logic
    from django.test import RequestFactory
    rf = RequestFactory()
    req = rf.post('/api/reports/generated/generate/', data={'name': name, 'report_type': report_type, 'filters': filters or {}})
    # simulate a user is necessary — in production pass a system user id
    # here we just create a report entry
    rpt = GeneratedReport.objects.create(name=name, report_type=report_type, filters=filters or {})
    rpt.summary_text = f"Scheduled report generated at {timezone.now().isoformat()}"
    rpt.save()
    return {'id': str(rpt.id), 'name': name}


@shared_task
def email_report(report_id, recipient_email):
    try:
        rpt = GeneratedReport.objects.get(pk=report_id)
    except GeneratedReport.DoesNotExist:
        return {'error': 'report not found'}
    subject = f"Report {rpt.name}"
    body = rpt.summary_text or 'Please find attached report.'
    # attempt to attach file if present
    try:
        if rpt.file:
            # build email with attachment
            email = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient_email])
            rpt.file.open('rb')
            email.attach(rpt.file.name.split('/')[-1], rpt.file.read(), rpt.file_type or 'application/octet-stream')
            email.send(fail_silently=False)
            rpt.delivery_status = {'last_sent': timezone.now().isoformat(), 'recipient': recipient_email}
            rpt.save(update_fields=['delivery_status'])
            return {'status': 'sent', 'attached': True}
        else:
            send_mail(subject, body + '\n\n' + (rpt.file.url if rpt.file else ''), settings.DEFAULT_FROM_EMAIL, [recipient_email])
            rpt.delivery_status = {'last_sent': timezone.now().isoformat(), 'recipient': recipient_email}
            rpt.save(update_fields=['delivery_status'])
            return {'status': 'sent', 'attached': False}
    except Exception as exc:
        rpt.delivery_status = {'error': str(exc)}
        rpt.save(update_fields=['delivery_status'])
        return {'status': 'error', 'error': str(exc)}
