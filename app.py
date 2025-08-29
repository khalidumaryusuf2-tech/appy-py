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

# ✅ Styled Order Form HTML
form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mac Dee Order Form</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #fdf6f0;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .form-container {
            background-color: #fff;
            padding: 30px 40px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
        }
        h2 {
            text-align: center;
            color: #d35400;
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            margin-top: 10px;
            display: block;
        }
        input[type="text"],
        input[type="email"],
        input[type="number"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
        }
        button {
            background-color: #d35400;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 8px;
            width: 100%;
            margin-top: 20px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #e67e22;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Mac Dee Order Form</h2>
        <form method="POST" action="/create-checkout-session">
            <label>Name:</label>
            <input type="text" name="name" required>

            <label>Email:</label>
            <input type="email" name="email" required>

            <label>Quantity:</label>
            <input type="number" name="quantity" min="1" required>

            <input type="hidden" name="payment_method" value="transfer">
            <button type="submit">Place Order</button>
        </form>
    </div>
</body>
</html>
'''

# ✅ Receipt Upload HTML
upload_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Upload Receipt</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #fdf6f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .upload-container {
            background-color: #fff;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
        }
        h2 {
            text-align: center;
            color: #d35400;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 15px;
        }
        input[type="file"],
        input[type="email"] {
            width: 100%;
            margin-top: 5px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            margin-top: 20px;
            background-color: #d35400;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 8px;
            width: 100%;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #e67e22;
        }
    </style>
</head>
<body>
    <div class="upload-container">
        <h2>Upload Payment Receipt</h2>
        <form method="POST" action="/upload-receipt" enctype="multipart/form-data">
            <label>Email:</label>
            <input type="email" name="email" required>

            <label>Upload Receipt:</label>
            <input type="file" name="receipt" accept=".jpg,.jpeg,.png,.pdf" required>

            <button type="submit">Submit Receipt</button>
        </form>
    </div>
</body>
</html>
'''

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

    # ✅ Send email notification
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

    # ✅ Redirect to thank-you page
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

    filename = secure_filename(file.filename)
    file_data = file.read()

    msg = EmailMessage()
    msg['Subject'] = 'Payment Receipt Submission'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(f'Receipt submitted by: {email}')
    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=filename)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        return f"❌ Failed to send receipt: {e}"

    return f"✅ Receipt uploaded successfully! We'll confirm your payment shortly."

if __name__ == '__main__':
    app.run(port=8000, debug=True)
