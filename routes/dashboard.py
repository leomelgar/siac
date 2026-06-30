from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.colege import Colegio
from utils.db import db

colegio = Blueprint("colegio", __name__)


@colegio.route('/')
def index():
    colegio = Colegio.query.all()
    return render_template('index.html', colegio=colegio)


""" @colegio.route('/new', methods=['POST'])
def add_contact():
    if request.method == 'POST':

        # receive data from the form
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']

        # create a new Contact object
            new_colegio = Colegio(fullname, email, phone)

        # save the object into the database
        db.session.add(new_colegio)
        db.session.commit()

        flash('Colegio added successfully!')

        return redirect(url_for('colegio.index')) """

@colegio.route("/about")
def about():
    return render_template("about.html")
