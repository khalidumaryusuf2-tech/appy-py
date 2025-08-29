from flask import Flask, render_template_string, request, redirect
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import csv
from datetime import datetime
from werkzeug.utils import secure_filename

# ✅ Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

app = Flask(__name__)
UPLOAD_FOLDER = 'receipts'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Order Form HTML
form_html = '''...'''  # (Use your existing form_html here)

# ✅ Receipt Upload HTML
upload_html = '''...'''  # (Use your existing upload_html here)

@app.route('/')
def index():
    return render_template_string(form_html)

@app.route('/create-checkout-session', methods=['POST'])
def checkout():
    name = request.form['name']
    email = request.form['email']
    quantity = int(request.form['quantity'])
    unit_price = 200000  # ₦2000.00 in kobo

    if quantity * unit_price < 80000:
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
        return f"❌ Failed to send email: {e}"

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
        return render_template_string(upload_html)

    email = request.form['email']
    file = request.files['receipt']

    if not file:
        return "❌ No file uploaded."

    filename = secure
