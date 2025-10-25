from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model


class TOTPDeviceTest(TestCase):
    @override_settings(USE_2FA=True)
    def test_totp_device_generates_and_verifies_token(self):
        User = get_user_model()
        user = User.objects.create_user(username='totpuser', password='pass')

        # Import models inside the test so Django settings are configured
        from django_otp.plugins.otp_totp.models import TOTPDevice
        import base64
        import pyotp

        # Create a TOTP device for the user. The device will generate a key
        # automatically if not provided. Mark it confirmed so it's usable.
        device = TOTPDevice.objects.create(user=user, name='test-device', confirmed=True)

        # device.bin_key is a bytes secret; pyotp expects base32, so encode it.
        b32 = base64.b32encode(device.bin_key).decode()
        totp = pyotp.TOTP(b32)
        token = totp.now()

        # Verify that the device accepts the generated token
        self.assertTrue(device.verify_token(token), 'TOTPDevice failed to verify a valid token')
