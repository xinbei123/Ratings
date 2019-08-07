"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, redirect, flash, session

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')

@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/register', methods=['GET'])
def register_form():
    """Show the registration form."""

    return render_template('register_form.html')


@app.route('/register', methods=['POST'])
def register_process():
    """Process the registration form"""
   
    email = request.form.get('email')
    password = request.form.get('password')
    zipcode = request.form.get('zipcode')
    age = request.form.get('age')

    new_user = User(email=email, password=password, 
                    zipcode=zipcode, age=age)

    # We need to add to the session or it won't ever be stored
    db.session.add(new_user)
    # Once we're done, we should commit our work
    db.session.commit()

    return redirect('/')

@app.route('/login', methods=['GET'])
def login_form():
    """Show login form"""

    return render_template('login_form.html')

@app.route('/login', methods=['POST'])
def login_process():
    """Process login"""

    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email == email).first()
    
    if not user:
        flash('Invalid user')
        return redirect('/login')

    if user.password != password:
        flash('Invalid password')
        return redirect('/login')

    session['user_id'] = user.user_id

    flash('Logged in')
    return redirect(f"users/{user.user_id}")

@app.route('/logout')
def logout_process():
    """logged out"""

    del session['user_id']
    flash('Logged out')
    return redirect('/')

@app.route('/users/<int:user_id>')
def user_detail(user_id):
    """show user details"""

    user = User.query.get(user_id)
    return render_template('user.html', user=user)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
