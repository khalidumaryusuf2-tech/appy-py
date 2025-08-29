from flask import Flask, render_template_string, request, redirect
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import csv
from datetime import datetime

# ✅ Load environment variables
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

app = Flask(__name__)

# ✅ HTML form (Bank Transfer only)
form_html = '''
<h2>Mac Dee Order Form</h2>
<form method="POST" action="/create-checkout-session">
    <label>Name:</label><br>
    <input type="text" name="name" required><br><br>
    <label>Email:</label><br>
    <input type="email" name="email" required><br><br>
    <label>Quantity:</label><br>
    <input type="number" name="quantity" min="1" required><br><br>
    <input type="hidden" name="payment_method" value="transfer">
    <button type="submit">Place Order</button>
</form>
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
    After payment, reply to the confirmation email with your proof of payment.<br><br>
    Thank you for choosing Mac Dee!
    """

if __name__ == '__main__':
    app.run(port=8000, debug=True)
