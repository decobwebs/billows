import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()


# Admin WhatsApp number
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER")  # Replace with the correct number

# Email credentials (unchanged from original code)
gmail = os.getenv("GMAIL")
receiver = os.getenv("RECEIVER")
password = os.getenv("PASSWORD")
subject = os.getenv("SUBJECT")
secret_key = os.getenv("SECRET_KEY")

names = [
    'Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince',
    'Edward Norton', 'Fiona Green', 'George Martin', 'Hannah Lee',
    'Isaac Newton', 'Jane Austen'
]

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
ckeditor = CKEditor(app)
Bootstrap5(app)

# Forms
class ReviewForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    room = StringField("Room", validators=[DataRequired()])
    table = StringField("Table", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    rate = SelectField("Rate", choices=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], validators=[DataRequired()])
    submit = SubmitField("Send!")


class RateStaffForm(FlaskForm):
    staff_name = StringField("Staff Name", validators=[DataRequired()])
    review = StringField("Review", validators=[DataRequired()])
    rate = SelectField("Rate", choices=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], validators=[DataRequired()])
    submit = SubmitField("Send!")


# Generate WhatsApp URL
def generate_whatsapp_url(data):
    message = (
        f"Hello, Admin!\n\n"
        f"New Room Booking Request:\n\n"
        f"Name: {data.get('name')}\n"
        f"Email: {data.get('email')}\n"
        f"Check-In Date: {data.get('check_in')}\n"
        f"Check-Out Date: {data.get('check_out')}\n"
        f"Guests: {data.get('guests')}\n"
        f"Room Type: {data.get('room_type')}\n"
    )
    encoded_message = urlencode({"text": message})
    return f"https://wa.me/{ADMIN_PHONE_NUMBER}?{encoded_message}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


@app.route("/room")
def room():
    return render_template("room.html")


@app.route("/Special Offer")
def special_offer():
    return render_template("special_offer.html")


@app.route("/outlets")
def outlets():
    return render_template("outlets.html")


@app.route("/beverages")
def beverages():
    return render_template("beverages.html")


@app.route("/review", methods=["GET", "POST"])
def review():
    form = ReviewForm()
    if form.validate_on_submit():
        # Save guest review to CSV
        with open("cafe-data.csv", mode="a", encoding='utf-8') as csv_file:
            csv_file.write(f"\n{form.name.data},{form.email.data},{form.room.data},"
                           f"{form.table.data},{form.review.data},{form.rate.data}")

        # Send guest review via email
        body = (f"Name of guest: {form.name.data}\nEmail: {form.email.data}\n"
                f"Room number: {form.room.data}\nTable number: {form.table.data}\n"
                f"Review: {form.review.data}\nRating: {form.rate.data}\n")
        message = MIMEMultipart()
        message["From"] = gmail
        message["To"] = receiver
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        connection = smtplib.SMTP_SSL("smtp.gmail.com")
        connection.ehlo()
        connection.login(user=gmail, password=password)
        text = message.as_string()
        connection.sendmail(gmail, receiver, text)
        connection.quit()

        return redirect(url_for('home'))
    return render_template("feedback.html", form=form)


@app.route("/rate_staff", methods=["GET", "POST"])
def rate_staff():
    form = RateStaffForm()
    if form.validate_on_submit():
        staff_name = form.staff_name.data
        staff_review = form.review.data
        rate = len(form.rate.data)  # Count stars based on length of the string

        # Save staff rating to CSV
        staff_ratings = {
            staff_name: {'name': staff_name, 'review': staff_review, 'total_ratings': rate}
        }
        with open("rating.csv", mode="a", encoding='utf-8') as csv_file:
            csv_file.write(f"{staff_ratings[staff_name]['name']},"
                           f"{staff_ratings[staff_name]['review']},"
                           f"{staff_ratings[staff_name]['total_ratings']}\n")

        # Send staff rating via email
        body = (f"Name of staff: {form.staff_name.data}\nReview: {form.review.data}\n"
                f"Rating: {form.rate.data}\n")
        message = MIMEMultipart()
        message["From"] = gmail
        message["To"] = receiver
        message["Subject"] = f"Staff Review: {staff_name}"
        message.attach(MIMEText(body, "plain"))

        connection = smtplib.SMTP_SSL("smtp.gmail.com")
        connection.ehlo()
        connection.login(user=gmail, password=password)
        text = message.as_string()
        connection.sendmail(gmail, receiver, text)
        connection.quit()

        return redirect(url_for('home'))
    return render_template("staffrating.html", form=form)


@app.route("/book", methods=["POST"])
def book():
    # Collect form data from the booking form
    form_data = {
        "name": request.form.get("name"),  # Added name field
        "email": request.form.get("email"),
        "check_in": request.form.get("check_in"),
        "check_out": request.form.get("check_out"),
        "guests": request.form.get("guests"),
        "room_type": request.form.get("room_type"),
    }

    # Generate WhatsApp message
    message = (
        f"Hello, Admin!\n\n"
        f"New Room Booking Request:\n\n"
        f"Name: {form_data['name']}\n"  # Include name in message
        f"Email: {form_data['email']}\n"
        f"Check-In Date: {form_data['check_in']}\n"
        f"Check-Out Date: {form_data['check_out']}\n"
        f"Guests: {form_data['guests']}\n"
        f"Room Type: {form_data['room_type']}\n"
    )
    encoded_message = urlencode({"text": message})
    whatsapp_url = f"https://wa.me/2348155114430?{encoded_message}"  # Replace with your WhatsApp number

    # Redirect user to WhatsApp
    return redirect(whatsapp_url)



if __name__ == "__main__":
    app.run(debug=True, port=5001)
