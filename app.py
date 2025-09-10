from flask import Flask, render_template, request, send_file, flash
from qr_generator.qr_utils import validate_and_prepare_data, generate_qr_code_image
import os
import base64

app = Flask(__name__)
# A secret key is needed for flashing messages
app.secret_key = os.urandom(24) 
# Set a maximum content length for file uploads (e.g., 2 MB) for security
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Pass form data and files to the validation utility
            data_for_qr, error = validate_and_prepare_data(request.form, request.files)

            if error:
                # If there's a validation error, flash it and re-render the page
                flash(error, 'error')
                return render_template('index.html')

            # If validation is successful, generate the QR code
            qr_buffer = generate_qr_code_image(data_for_qr)

            # Send the image file back to the user for download
            # return send_file(
            #     qr_buffer,
            #     mimetype='image/png',
            #     as_attachment=True,
            #     download_name='qrcode.png'
            # )
            # Convert QR image to base64 for display
            img_base64 = base64.b64encode(qr_buffer.getvalue()).decode('utf-8')
            img_data_url = f"data:image/png;base64,{img_base64}"
            return render_template('index.html', qr_image=img_data_url)

        except Exception as e:
            # Catch potential errors like file too large
            flash(f"An error occurred: {str(e)}", 'error')
            return render_template('index.html')

    # For GET requests, just show the main page
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)