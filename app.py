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
