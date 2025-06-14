import pyotp
import qrcode
import io
import base64

def generate_otp_secret():
    return pyotp.random_base32()

def get_qr_code_image(secret, username, issuer='MyApp'):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)
    qr = qrcode.make(uri)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str  # You can embed this in frontend as <img src="data:image/png;base64,{{ qr_code }}" />
