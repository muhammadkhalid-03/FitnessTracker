from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import Workout, Weight
from flask_login import login_required, current_user
import plotly.express as px
import datetime


views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    first_name = current_user.first_name
    return render_template("home.html", user=current_user, first_name=first_name)

@views.route('/sign-up')
def sign_up():
    return render_template("sign_up.html", user=current_user)

@views.route('/login')
def login():
    return render_template("login.html", user=current_user)

@views.route('/workout-log', methods=['GET', 'POST'])
@login_required
def workout_log():
    if request.method == 'POST':
        exercise_name = request.form.get('exerciseName')
        sets = int(request.form.get('sets'))
        reps = int(request.form.get('reps'))
        weight = float(request.form.get('weight'))
        new_workout = Workout(exercise_name=exercise_name, sets=sets, reps=reps, weight=weight, user_id=current_user.id)
        db.session.add(new_workout)
        db.session.commit()
        flash('Exercise successfully logged!', category='success')
    return render_template("workout_log.html", user=current_user)

@views.route('/track-progress', methods=['GET', 'POST'])
@login_required
def track_progress():

    weights = Weight.query.filter_by(user_id=current_user.id).order_by(Weight.date.desc()).all()
    workouts = Workout.query.filter_by(user_id=current_user.id).order_by(Workout.date.desc()).all()

    dates = [weight.date for weight in weights]
    weight_values = [weight.weight for weight in weights]

    # Create a dictionary-like object with the data
    data = {
        'Date': dates,
        'Weight': weight_values
    }

    # Create a DataFrame from the data
    import pandas as pd
    df = pd.DataFrame(data)

    # Create the Plotly Express figure
    fig = px.line(df, x='Date', y='Weight', labels={'Date': 'Date', 'Weight': 'Weight (lbs)'})

    fig.update_layout(
        title='Bodyweight Progress',
        xaxis_title='Date',
        yaxis_title='Bodyweight (lbs)',
        font=dict(family='Arial', size=12),
    )
    fig.update_traces(
        line=dict(width=2),
        marker=dict(size=8, color='blue'),
    )
    chart_div = fig.to_html(full_html=False)

    return render_template("track_progress.html", chart_div=chart_div, user=current_user, workouts=workouts)

@views.route('/log-weight', methods=['GET', 'POST'])
@login_required
def log_weight():
    if request.method == 'POST':
        bodyWeight = float(request.form.get('bodyWeight'))
        new_weight = Weight(weight=bodyWeight, user_id=current_user.id)
        db.session.add(new_weight)  # Add the new_weight object to the session
        db.session.commit()  # Commit the changes to the database
        flash('Weight successfully logged!', category='success')
    return render_template("log_weight.html", user=current_user)


@views.route('/reset-workout')
@login_required
def reset_workout():
    # Add logic to reset workout log for the current user
    # For example:
    Workout.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Workout log reset successfully!', category='success')
    return redirect(url_for('views.track_progress'))

@views.route('/reset-weight')
@login_required
def reset_weight():
    # Add logic to reset weight log for the current user
    # For example:
    Weight.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Weight log reset successfully!', category='success')
    return redirect(url_for('views.track_progress'))