from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
import re


class Command(BaseCommand):
    help = (
        "Send a 2FA test email token to a user's email using django-otp's EmailDevice."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "identifier",
            nargs="?",
            help="username (positional) or use --username/--email to specify the user",
        )
        parser.add_argument("--username", dest="username", help="username to lookup")
        parser.add_argument("--email", dest="email", help="email to lookup")
        parser.add_argument(
            "--device-name",
            dest="device_name",
            default="default",
            help="email device name (default: default)",
        )
        parser.add_argument(
            "--create",
            action="store_true",
            dest="create",
            help="create an EmailDevice for the user if none exists",
        )
        parser.add_argument(
            "--no-redact",
            action="store_true",
            dest="no_redact",
            help="Do not redact tokens when printing the email body (use with care).",
        )

    def handle(self, *args, **options):
        identifier = options.get("identifier")
        username = options.get("username") or identifier
        email = options.get("email")
        device_name = options.get("device_name")
        create = options.get("create", False)
        no_redact = options.get("no_redact", False)

        if not username and not email:
            raise CommandError("Provide --username or --email or a positional username identifier.")

        User = get_user_model()
        try:
            if username:
                user = User.objects.get(username=username)
            else:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError("User not found")

        try:
            from django_otp.plugins.otp_email.models import EmailDevice
        except Exception as exc:  # pragma: no cover - defensive
            raise CommandError(
                "django-otp/otp_email plugin not available or import failed: %s" % exc
            )

        device = EmailDevice.objects.filter(user=user, name=device_name).first()

        if not device:
            # try any confirmed device
            device = EmailDevice.objects.filter(user=user, confirmed=True).first()

        if not device:
            if create:
                self.stdout.write(
                    "No EmailDevice named %r found for user %s — creating one (confirmed=True)."
                    % (device_name, user)
                )
                device = EmailDevice.objects.create(
                    user=user, name=device_name, confirmed=True, email=user.email
                )
            else:
                raise CommandError(
                    "No EmailDevice found for user. Use --create to create one or create a device in admin."
                )

        self.stdout.write(
            "Using EmailDevice name=%r email=%r; generating token..."
            % (getattr(device, "name", None), device.email or user.email)
        )

        # generate_challenge will check cooldown/throttling and send the email
        try:
            result = device.generate_challenge()
        except Exception as exc:  # pragma: no cover - defensive
            raise CommandError("Failed to generate/send token: %s" % exc)

        self.stdout.write(self.style.SUCCESS("generate_challenge result: %s" % result))

        # Report the configured email backend. For safety, redact numeric
        # tokens when the message was handed to a real delivery backend.
        backend = getattr(settings, "EMAIL_BACKEND", None)
        self.stdout.write("EMAIL_BACKEND=%r" % backend)

        try:
            if hasattr(mail, "outbox"):
                if mail.outbox:
                    msg = mail.outbox[-1]
                    self.stdout.write("--- Captured locmem email ---")
                    self.stdout.write("To: %s" % (getattr(msg, "to", None),))
                    self.stdout.write("Subject: %s" % (getattr(msg, "subject", None),))
                    # prefer body attr; fallback to message string
                    body = getattr(msg, "body", str(msg))

                    backend_name = (backend or "").lower()
                    # If using locmem, show full body. For other backends
                    # (console, smtp, filebased, etc) redact numeric tokens
                    # but display a last-2-digit hint to help correlation.
                    if "locmem" in backend_name:
                        self.stdout.write("Body:\n%s" % body)
                    else:
                        try:
                            # replace tokens with redacted marker but keep last 2 digits
                            def redact_token(m):
                                tok = m.group(1)
                                hint = tok[-2:]
                                return f"[REDACTED TOKEN - last2:{hint}]"

                            redacted = re.sub(r"\b(\d{6,8})\b", redact_token, body)
                        except Exception:
                            redacted = "[REDACTED] (could not parse body)"

                        self.stdout.write("Body (redacted):\n%s" % redacted)
                else:
                    self.stdout.write("No messages in locmem outbox after sending.")
        except Exception:
            # Don't fail the command if we can't inspect the backend
            pass
