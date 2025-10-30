from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True)
def send_message_task(self, message_id):
    """Task to send a MessageSent identified by id.

    The task loads the MessageSent and its MessageRecipient records and sends
    the email to recipients in a best-effort way, updating recipient status.
    """
    try:
        from .models import MessageSent, MessageRecipient
        ms = MessageSent.objects.filter(id=message_id).first()
        if not ms:
            return {'status': 'missing'}
        recipients = list(ms.recipients.all())
        emails = [r.email for r in recipients]
        if not emails:
            return {'status': 'no_recipients'}

        # send mail; for large recipients list this should be chunked or use a proper mail service
        try:
            send_mail(ms.subject or 'Message from Tawi', ms.body or '', None, emails, fail_silently=False)
            # mark recipients as sent
            MessageRecipient.objects.filter(message=ms).update(status='sent', error='')
            return {'status': 'sent', 'count': len(emails)}
        except Exception as exc:
            # mark recipients as failed with error
            msg = str(exc)
            for r in recipients:
                try:
                    r.status = 'failed'
                    r.error = msg
                    r.save(update_fields=['status', 'error'])
                except Exception:
                    pass
            return {'status': 'failed', 'error': msg}
    except Exception as exc:
        return {'status': 'error', 'error': str(exc)}
