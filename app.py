import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
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


app = Flask(__name__)



app.config['SECRET_KEY'] = secret_key
ckeditor = CKEditor(app)
Bootstrap5(app)


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
        with open("cafe-data.csv", mode="a", encoding='utf-8') as csv_file:
            csv_file.write(f"\n{form.name.data},"
                           f"{form.email.data},"
                           f"{form.room.data},"
                           f"{form.table.data},"
                           f"{form.review.data},"
                           f"{form.rate.data}")

        body = f"Name of guest: {form.name.data}\nEmail: {form.email.data}\nRoom number: {form.room.data}\nTable number: {form.table.data}\nReview: {form.review.data}\nRating: {form.rate.data}\n  "
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


@app.route("/Rate staff", methods=["GET", "POST"])
def rate_staff():
    form = RateStaffForm()
    if form.validate_on_submit():
        with open("cafe-data.csv", mode="a", encoding='utf-8') as csv_file:
            csv_file.write(f"{form.staff_name.data},"
                           f"{form.rate.data},"
                           f"{form.review.data}")
            staff_name = form.staff_name.data
        rates = len(form.rate.data)
        rate = int(rates)
        staff_review = form.review.data
        print(rate)


        body = f"Name of staff {form.staff_name.data}\nReview: {form.review.data}\nRating: {form.rate.data}\n"
        message = MIMEMultipart()

        for name in names:
            if name == staff_name:
                staff_ratings = {
                    name: {'name': name, 'review': staff_review, 'total_ratings': rate}
                }

                staff_name = form.staff_name.data

                # Print the updated staff ratings
                with open("rating.csv", mode="a", encoding='utf-8') as csv_file:
                    csv_file.write(f"{staff_ratings[name]["name"]},"
                                   f"{staff_ratings[name]['review']},"
                                   f"{staff_ratings[name]['total_ratings']}\n"
                                   )

        return redirect(url_for('home'))
    return render_template("staffrating.html", form=form)





if __name__ == "__main__":
    app.run(debug=True, port=5001)