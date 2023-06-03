# not functional yet, use cmd line app for now
# TODO: fix this

import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html

# Import your models, engine, and session here
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
    desc,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.db_classes import *

# Get the list of users from the database (even if it's only one person)
engine = create_engine("sqlite:///database/exercise_alchemy_log.db")
Session = sessionmaker(bind=engine)
session = Session()
available_users = session.query(User).all()
user = available_users[0]
user_id = user.id
username = user.username
session.close()

# define the dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)


def get_latest_exercises(user_id):
    session = Session()

    # Query the database to get the latest 5 exercise dates for the user
    exercises = (
        session.query(ExerciseSet.date_performed, ExerciseType.type)
        .join(Exercise, ExerciseSet.exercise_id == Exercise.id)
        .join(ExerciseType, Exercise.exercise_type_id == ExerciseType.id)
        .filter(Exercise.user_id == user_id)
        .order_by(desc(ExerciseSet.date_performed))
        .limit(5)
        .all()
    )

    # Close the session
    session.close()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(exercises, columns=["date", "exercise_type"])

    return df


app.layout = html.Div(
    [
        html.H1(f"Exercise Log"),
        html.Hr(),
        # User selection dropdown
        dcc.Dropdown(
            id="user-dropdown",
            options=[
                {"label": user.username, "value": user.id} for user in available_users
            ],
            value=user_id,
            placeholder="Select a user",
        ),
        # Table for displaying the latest 5 exercise dates
        html.Div(id="exercise-table"),
        # Add to the layout
        html.Div(
            [
                html.H2("Enter Exercise Details"),
                html.Hr(),
                # Dropdown to select exercise type
                dcc.Dropdown(
                    id="exercise-dropdown",
                    options=[
                        {"label": exercise.type, "value": exercise.id}
                        for exercise in session.query(ExerciseType).all()
                    ],
                    placeholder="Select an exercise type",
                ),
                dcc.DatePickerSingle(
                    id="date-picker",
                    date=datetime.datetime.now(),
                    display_format="MMMM D, YYYY",
                ),
                html.Div(id="set-details"),
                html.Button("Add set", id="add-set", n_clicks=0),
                html.Div(
                    [
                        dbc.Button(
                            "Confirm",
                            id="confirm-button",
                            color="success",
                            className="m-2",
                        ),
                        dbc.Button(
                            "Cancel",
                            id="cancel-button",
                            color="danger",
                            className="m-2",
                        ),
                    ]
                ),
            ]
        ),
    ]
)


# Callback for updating the exercise table when a user is selected
@app.callback(Output("exercise-table", "children"), [Input("user-dropdown", "value")])
def update_exercise_table(user_id):
    if user_id is not None:
        df = get_latest_exercises(user_id)
        return html.Div(
            [
                dcc.Graph(
                    id="latest-exercises",
                    figure=px.bar(
                        df, x="date", y="exercise_type", text="exercise_type"
                    ),
                )
            ]
        )
    else:
        return None


# Callback for updating the exercise dropdown when a user is selected
@app.callback(
    Output("set-details", "children"),
    [Input("add-set", "n_clicks")],
    [State("set-details", "children")],
)
def add_set(n_clicks, children):
    new_element = html.Div(
        [
            dcc.Input(id=f"set-{n_clicks}", type="number", placeholder="Set number"),
            dcc.Input(id=f"reps-{n_clicks}", type="number", placeholder="Repetitions"),
            dcc.Input(id=f"weight-{n_clicks}", type="number", placeholder="Weight"),
        ]
    )
    children.append(new_element)
    return children


@app.callback(
    [
        Output("set-details", "children"),
        Output("exercise-dropdown", "value"),
        Output("date-picker", "date"),
    ],
    [Input("cancel-button", "n_clicks")],
)
def reset_form(n):
    # This will reset the form
    return [], None, datetime.datetime.now()


@app.callback(
    [
        Output("set-details", "children"),
        Output("exercise-dropdown", "value"),
        Output("date-picker", "date"),
    ],
    [Input("confirm-button", "n_clicks")],
    [
        State("exercise-dropdown", "value"),
        State("date-picker", "date"),
        State("set-details", "children"),
    ],
)
def save_exercise(n, exercise_id, date, set_details):
    if n:
        # Create and commit the new exercise record
        session = Session()
        exercise = Exercise(
            user_id=user_id,
            exercise_type_id=exercise_id,
            date=datetime.datetime.strptime(date, "%Y-%m-%d"),
        )
        session.add(exercise)
        session.commit()

        # Add the sets
        for i in range(len(set_details)):
            set_number = int(set_details[i].children[0].value)
            repetitions = int(set_details[i].children[1].value)
            weight = float(set_details[i].children[2].value)
            exercise_set = ExerciseSet(
                exercise_id=exercise.id,
                set_number=set_number,
                repetitions=repetitions,
                weight=weight,
            )
            session.add(exercise_set)

        session.commit()
        session.close()

        # Reset the form
        return [], None, datetime.datetime.now()

    return dash.no_update  # No update if the button hasn't been clicked


if __name__ == "__main__":
    app.run_server(debug=True, port=8069)
