import qrcode
from io import BytesIO
import re

# Define allowed file extensions for security
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}

def allowed_file(filename, allowed_extensions):
    """Checks if the file's extension is in the allowed set."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_and_prepare_data(form_data, files):
    """
    Validates user input based on qr_type and prepares the data string for QR generation.
    Returns (data_for_qr, error_message).
    """
    qr_type = form_data.get('qr_type')
    
    if not qr_type:
        return None, "QR Code type not specified."

    # --- Text-based QR Code Types ---
    if qr_type == 'url':
        url = form_data.get('url_data', '').strip()
        if not re.match(r'^https?://', url):
            return None, "Invalid URL. Please start with http:// or https://"
        return url, None

    elif qr_type == 'phone':
        phone = form_data.get('phone_data', '').strip()
        if not phone.isdigit():
            return None, "Invalid phone number. Please use digits only."
        return f"tel:{phone}", None

    elif qr_type == 'sms':
        phone = form_data.get('sms_phone', '').strip()
        message = form_data.get('sms_message', '').strip()
        if not phone.isdigit():
            return None, "Invalid phone number for SMS. Please use digits only."
        if not message:
            return None, "SMS message cannot be empty."
        return f"smsto:{phone}:{message}", None

    elif qr_type == 'email':
        to = form_data.get('email_to', '').strip()
        subject = form_data.get('email_subject', '').strip()
        body = form_data.get('email_body', '').strip()
        if not re.match(r'[^@]+@[^@]+\.[^@]+', to):
            return None, "Invalid 'To' email address."
        return f"mailto:{to}?subject={subject}&body={body}", None

    elif qr_type == 'text':
        text = form_data.get('text_data', '')
        if not text.strip():
            return None, "Text content cannot be empty."
        return text, None

    # --- File-based QR Code Types ---
    elif qr_type == 'pdf':
        if 'pdf_file' not in files or not files['pdf_file'].filename:
            return None, "No PDF file selected."
        file = files['pdf_file']
        if not allowed_file(file.filename, ALLOWED_PDF_EXTENSIONS):
            return None, "Invalid file type. Please upload a PDF."
        # Encoding raw file data. Note: QR codes have a size limit!
        # This is suitable for very small files.
        file_data = file.read()
        return file_data, None
        
    elif qr_type == 'image':
        if 'image_file' not in files or not files['image_file'].filename:
            return None, "No image file selected."
        file = files['image_file']
        if not allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            return None, "Invalid file type. Please upload a PNG, JPG, JPEG, or GIF."
        # Encoding raw file data.
        file_data = file.read()
        return file_data, None

    return None, "Invalid QR code type."


def generate_qr_code_image(data):
    """
    Generates a QR code image from the given data and returns it as a BytesIO buffer.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image to a memory buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0) # Rewind the buffer to the beginning
    
    return buffer