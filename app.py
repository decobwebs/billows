import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_bootstrap import Bootstrap
from flask_bootstrap4 import Bootstrap

from flask_ckeditor import CKEditor

from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from info import gmail, receiver, password, subject, secret_key
from names import names



from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, EmailField
from wtforms.validators import DataRequired


gmail = "decobweb@gmail.com"
receiver = "cobwebb784@gmail.com"
password = "dqaarqodqpwgrajb"
subject = "Guest Feedback"
secret_key = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

names = [
    'Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince',
    'Edward Norton', 'Fiona Green', 'George Martin', 'Hannah Lee',
    'Isaac Newton', 'Jane Austen'
]

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
ckeditor = CKEditor(app)
Bootstrap(app)


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")


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


if __name__ == "__main__":

    app.run(debug=True, port=5001)

    app.run(debug=False, port=5001)

