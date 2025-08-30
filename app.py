from flask import Flask, render_template, request, redirect
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid

# ✅ Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

app = Flask(__name__)
UPLOAD_FOLDER = 'receipts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/create-checkout-session', methods=['POST'])
def checkout():
    name = request.form['name']
    email = request.form['email']
    quantity = int(request.form['quantity'])
    unit_price = 200000  # ₦2000.00 in kobo

    if quantity * unit_price < 200000:
        return "❌ Minimum order amount must be ₦2000.00"

    total_amount = quantity * unit_price / 100  # Convert to naira

    # ✅ Send admin email
    msg = EmailMessage()
    msg['Subject'] = 'New Mac Dee Order'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(
        f'Name: {name}\nEmail: {email}\nQuantity: {quantity}\nTotal: ₦{total_amount:.2f}\nPayment Method: Bank Transfer'
    )

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")
        return "❌ Something went wrong while sending your order. Please try again later."

    # ✅ Log order to CSV
    with open('orders.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), name, email, quantity, f"₦{total_amount:.2f}", "Bank Transfer"])

    return redirect(f'/thank-you?name={name}&amount={total_amount:.2f}')

@app.route('/thank-you')
def thank_you():
    name = request.args.get('name', 'Customer')
    amount = request.args.get('amount', '0.00')
    return f"""
    ✅ Order received, {name}!<br><br>
    Please make a bank transfer of <strong>₦{amount}</strong> to:<br><br>
    <strong>Account Name:</strong> Khalid Umar<br>
    <strong>Account Number:</strong> 7084937381<br>
    <strong>Bank:</strong> Opay Bank<br><br>
    After payment, <a href="/upload-receipt">click here to upload your receipt</a>.<br><br>
    Thank you for choosing Mac Dee!
    """

@app.route('/upload-receipt', methods=['GET', 'POST'])
def upload_receipt():
    if request.method == 'GET':
        return render_template('upload.html')

    email = request.form['email']
    file = request.files['receipt']

    if not file or not allowed_file(file.filename):
        return "❌ Invalid or missing file. Only PNG, JPG, JPEG, or PDF allowed."

    filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # ✅ Send admin email with attachment
    msg = EmailMessage()
    msg['Subject'] = 'Payment Receipt Submission'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(f'Receipt submitted by: {email}')
    with open(filepath, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=filename)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)

            # ✅ Send confirmation to customer
            confirmation = EmailMessage()
            confirmation['Subject'] = 'Mac Dee Receipt Received'
            confirmation['From'] = EMAIL_ADDRESS
            confirmation['To'] = email
            confirmation.set_content(
                f"✅ Hi {email}, we've received your payment receipt. We'll review it and confirm your order shortly.\n\nThank you for choosing Mac Dee!"
            )
            smtp.send_message(confirmation)

    except Exception as e:
        print(f"Receipt email error: {e}")
        return "❌ Failed to send receipt. Please try again later."

    return "✅ Receipt received and will be confirmed shortly."

if __name__ == '__main__':
    app.run(port=8000, debug=True)
