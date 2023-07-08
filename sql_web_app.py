"""V0.1.2"""

import datetime

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker

from src.db_classes import *

# Initialize the database #
# TODO could eventually be moved, but ok for now
# engine = create_engine("sqlite:///database/exercise_main.db")
engine = create_engine("sqlite:///database/exercise_testing.db")
Session = sessionmaker(bind=engine)

# Get the list of users from the database
# and in this case a fixed user is used
session = Session()
available_users = session.query(User).all()
user = available_users[0]
user_id = user.id
user_name = user.username
session.close()
###########################


def get_latest_exercises(user_id: int) -> pd.DataFrame:
    """
    Retrieves the 5 most recent exercise sessions for a given user from the database.
    """

    session = Session()

    # Query the database to get the latest 5 exercise dates for the user
    exercises = (
        session.query(Exercise.date_performed, ExerciseType.type)
        .join(ExerciseType, Exercise.exercise_type_id == ExerciseType.id)
        .filter(Exercise.user_id == user_id)
        .order_by(desc(Exercise.date_performed))
        .limit(5)
        .all()
    )

    # Close the session
    session.close()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(exercises, columns=["Date", "Exercise Type"])

    return df


def save_exercise(exercise_id, notes, date, set_details) -> None:
    """
    Saves a new exercise session, including all sets, to the database.
    """

    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    # Create and commit the new exercise record
    session = Session()
    exercise = Exercise(
        user_id=user_id,
        exercise_type_id=exercise_id,
        notes=notes,
        date_performed=date,
    )
    session.add(exercise)
    session.commit()

    # Add the sets
    for set_number in range(len(set_details)):
        repetitions = int(set_details[set_number][0])
        weight = float(set_details[set_number][1])
        print(set_number + 1, " ", repetitions, " ", weight)
        exercise_set = ExerciseSet(
            exercise_id=exercise.id,
            set_number=set_number + 1,
            repetitions=repetitions,
            weight=weight,
        )
        session.add(exercise_set)

    session.commit()
    session.close()


def get_exercise_types() -> list:
    """
    Retrieves all exercise types available in the database.
    """

    session = Session()
    exercise_types = session.query(ExerciseType).all()
    session.close()
    # # Convert the result to a pandas DataFrame
    # df = pd.DataFrame(exercise_types, columns=["id", "type"])

    return exercise_types


def write_user_weight(
    user_id: int, weight: float, date_recorded: datetime.date.today()
) -> None:
    """
    Write a new weight for an existing user to the database.

    Parameters:
    user_id (int): The id of the user whose weight is being recorded.
    weight (float): The user's weight.
    date_recorded (datetime.date): The date when the weight was recorded.

    Returns:
    None
    """

    # of note: decided against overwriting weights on same day.
    # aside from dumb entries, one might want to have multiple weights on same day after all

    # Create a new session
    session = Session()

    # Create a UserWeight instance linked to the user
    user_weight = UserWeight(
        user_id=user_id, weight=weight, date_recorded=date_recorded
    )

    # Add the new weight record to the database
    session.add(user_weight)
    session.commit()
    session.close()


def modify_user_weight(
    weight_id: int, new_weight: float, new_date_recorded: datetime.date.today()
) -> None:
    """
    Modify an existing weight record in the database.

    Parameters:
    weight_id (int): The id of the weight record that needs to be modified.
    new_weight (float): The new weight.
    new_date_recorded (datetime.date): The new date when the weight was recorded.

    Returns:
    None
    """
    # Create a new session
    session = Session()

    # Fetch the weight entry you want to modify
    user_weight = session.get(UserWeight, weight_id)

    # Modify the weight and the date when it was recorded
    user_weight.weight = new_weight
    user_weight.date_recorded = new_date_recorded

    # Commit the changes to the database
    session.commit()
    session.close()


def delete_user_weight(weight_id: int) -> None:
    """
    Deletes a user's weight entry in the database using the provided weight entry ID.
    """

    # Create a new session
    session = Session()

    # Fetch the weight entry you want to delete
    user_weight = session.get(UserWeight, weight_id)

    if user_weight is None:
        print("No weight entry found with the given id.")
        return None

    # Delete the entry
    session.delete(user_weight)

    # Commit the changes
    session.commit()

    print(f"Deleted weight id {weight_id}")
    session.close()


def update_username(username_new: str, username_current: str) -> None:
    """
    Updates a user's username in the database using the provided new username.
    """

    session = Session()

    # Fetch the user entry you want to update
    user = session.query(User).filter_by(username=username_current).first()

    if user is None:
        print("No user found with the given username.")
        return None

    # Update the username
    user.username = username_new

    # Commit the changes
    session.commit()


def get_personal_best(user_id: int) -> pd.DataFrame:
    """
    Returns a DataFrame containing personal best (max weight) for specified exercises for a given user.
    """

    session = Session()

    # Define the exercise types we're interested in
    exercise_types = ["Deadlift", "Squat", "Bench", "Overhead", "Pull-ups"]

    # Query the database to get the maximum weight for each exercise type
    personal_bests = (
        session.query(
            ExerciseType.type, func.max(ExerciseSet.weight), Exercise.date_performed
        )
        .join(Exercise, ExerciseSet.exercise_id == Exercise.id)
        .join(ExerciseType, Exercise.exercise_type_id == ExerciseType.id)
        .filter(Exercise.user_id == user_id)
        .filter(ExerciseType.type.in_(exercise_types))
        .group_by(ExerciseType.type)
        .all()
    )

    # Close the session
    session.close()

    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(personal_bests, columns=["exercise_type", "max_weight", "date"])

    return df


def get_latest_weight(user_id: int) -> float:
    """
    Retrieve the latest weight record for a given user from the database.\n

    Parameters:
    user_id (int): The id of the user whose latest weight is to be fetched.

    Returns:
    float: The latest weight of the user.
    """
    # Create a new session
    session = Session()

    # Query the database to get the latest weight for the user
    latest_weight_entry = (
        session.query(UserWeight)
        .filter(UserWeight.user_id == user_id)
        .order_by(desc(UserWeight.date_recorded))
        .first()
    )

    # Close the session
    session.close()

    # If there's a weight entry, return the weight, else return None
    if latest_weight_entry is not None:
        return f"Your latest weight entry {latest_weight_entry.weight} kg was recorded on {latest_weight_entry.date_recorded}."
    else:
        return None


def combined_weight_total_over_time(user_id: int) -> str:
    """sum of all weights lifted by a user since first entry"""

    session = Session()

    # Calculate the total weight lifted
    total_weight = (
        session.query(func.sum(ExerciseSet.repetitions * ExerciseSet.weight))
        .join(Exercise, ExerciseSet.exercise_id == Exercise.id)
        .filter(Exercise.user_id == user_id)
        .scalar()
    )

    # Find the date of the first entry
    first_date = (
        session.query(func.min(Exercise.date_performed))
        .filter(Exercise.user_id == user_id)
        .scalar()
    )

    # Close the session
    session.close()
    if total_weight > 1000:
        total_weight = round(total_weight / 1000, 2)
        return f"Fun fact: Since {first_date}, you lifted a combined total of {total_weight} tons!"
    else:
        return f"Fun fact: Since {first_date}, you lifted a combined total of {total_weight} kg!"


def create_excercise_day(excercise_id: int) -> bool:
    """
    Interactively collects exercise data from the user and writes it to the database. \n
    Returns:
    Boolean (True if an exercise was added, False otherwise)
    """

    if (
        excercise_id == 0
    ):  # now we don't acutally receive 0 so actually not necessary. but doesn't hurt.
        return False

    notes = input("Enter any notes: ")
    date = input("Enter the date (YYYY-MM-DD) (empty=today): ")
    if date == "":
        date = datetime.date.today()
    set_details = []
    set_number = 1
    while True:
        print("Enter details for set number: ", set_number)
        repetitions = input("Enter the number of repetitions (0=end of rep): ")
        if repetitions == "0" or repetitions == "":
            break
        weight = input("Enter the weight (kg): ")
        set_details.append([repetitions, weight])
        set_number += 1

    if set_number == 1:
        print("No sets entered, exiting.")
        return False
    else:
        print("Saving Excercise to db.")
        save_exercise(excercise_id, notes, date, set_details)
        return True


#################################################################################################################
# Dash App
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)

app.layout = html.Div(
    [
        dcc.Interval(
            id="interval-component",
            interval=10 * 1000,  # 10 ms should suffice
            n_intervals=0,  # in milliseconds
        ),
        html.H1(f"Welcome {user_name}!"),
        html.H3(id="current-datetime"),
        html.H4(id="combined-weight-total"),
        html.H4(id="latest-weight"),
        html.Hr(),
        html.Div(
            [
                html.Label("Update Weight (kg)"),
                dcc.Input(id="weight-input", type="number", value=""),
                html.Label("Date"),
                dcc.DatePickerSingle(
                    id="weightdate-input",
                    min_date_allowed=datetime.datetime(1999, 9, 9),
                    max_date_allowed=datetime.datetime.today(),
                    initial_visible_month=datetime.datetime.now(),
                ),
                html.Button("Submit", id="update-weight-button"),
            ]
        ),
        html.Hr(),
        html.Div(
            [
                html.H4("Your 5 Latest Exercises"),
                dash_table.DataTable(
                    id="exercise-table",
                ),
            ],
            style={
                "width": "30%",
                "margin": "0 auto",  # centers the div
            },
        ),
        html.Hr(),
        html.Div(
            [
                html.Div(id="exercise-data"),
                # Dropdown menu for exercise selection
                dcc.Dropdown(
                    id="exercise-dropdown",
                    options=[
                        {"label": i.type, "value": i.id} for i in get_exercise_types()
                    ],
                    placeholder="Select an exercise to add data for...",
                ),
            ],
            style={
                "width": "30%",
                "margin": "0 auto",  # centers the div
            },
        ),
    ]
)


# Intervall Update current date/time
@app.callback(
    Output("current-datetime", "children"), Input("interval-component", "n_intervals")
)
def update_current_datetime(n):
    return f"Current Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}."


# Intervall Update combined weight total
@app.callback(
    Output("combined-weight-total", "children"),
    Input("interval-component", "n_intervals"),
)
def update_combined_weight_total(n):
    return combined_weight_total_over_time(user_id)


# Intervall Update latest weight
@app.callback(
    Output("latest-weight", "children"), Input("interval-component", "n_intervals")
)
def update_latest_weight(n):
    # return f"Your latest weight (by date): {get_latest_weight(user_id)} kg."
    return get_latest_weight(user_id)


# Intervall Update latest exercises
@app.callback(
    Output("exercise-table", "data"),
    Output("exercise-table", "columns"),
    Input("interval-component", "n_intervals"),
)
def update_latest_exercises(n):
    df = get_latest_exercises(user_id)
    return df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]


@app.callback(
    Output("update-weight-button", "n_clicks"),
    Input("update-weight-button", "n_clicks"),
    State("weight-input", "value"),
    State("weightdate-input", "date"),
)
def update_weight(n_clicks, new_weight, new_weight_date):
    n_clicks = n_clicks if n_clicks is not None else 0
    if n_clicks < 1:
        raise PreventUpdate

    # if weightdate-input is empty, use today's date
    if new_weight_date is None:
        new_weight_date = datetime.date.today()
    else:
        new_weight_date = datetime.datetime.strptime(new_weight_date, "%Y-%m-%d").date()

    if new_weight is None or new_weight == 0:
        print("No weight input")
        raise PreventUpdate
    else:
        print(f"Updating weight {new_weight} kg on date {new_weight_date}")
        write_user_weight(user_id, new_weight, new_weight_date)

    raise PreventUpdate


@app.callback(
    Output("exercise-data", "children"),
    Input("exercise-dropdown", "value"),
)
def input_exercise_data(selected_exercise_id):
    if selected_exercise_id is None:
        raise dash.exceptions.PreventUpdate
    else:
        return html.Div(
            [
                html.H5(f"You selected exercise ID: {selected_exercise_id}"),
                html.Label("Enter the date of exercise (leave blank for today):"),
                dcc.DatePickerSingle(
                    id="date-input",
                    min_date_allowed=datetime.datetime(1999, 9, 9),
                    max_date_allowed=datetime.datetime.today(),
                    initial_visible_month=datetime.datetime.now(),
                ),
                html.Label("Enter any notes you have for this exercise session:"),
                dcc.Input(id="notes-input", type="text"),
                html.Label(
                    "Enter the number of reps for each set, separated by commas:"
                ),
                dcc.Input(id="reps-input", type="text"),
                html.Label("Enter the weight used for each set, separated by commas:"),
                dcc.Input(id="weight-input", type="text"),
                html.Button("Submit exercise data", id="submit-exercise-button"),
            ]
        )


@app.callback(
    [
        Output("date-input", "date"),
        Output("notes-input", "value"),
        Output("reps-input", "value"),
        Output("weight-input", "value"),
    ],
    Input("submit-exercise-button", "n_clicks"),
    State("exercise-dropdown", "value"),
    State("date-input", "date"),
    State("notes-input", "value"),
    State("reps-input", "value"),
    State("weight-input", "value"),
)
def process_exercise_data(n_clicks, selected_exercise_id, date, notes, reps, weights):
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate
    else:
        # if date is empty, use today's date
        if not date:
            date = datetime.date.today()

        # make sure reps and weights are not None
        if reps is None or weights is None:
            return None, None, None, None

        # parse the reps and weights
        try:
            reps = [int(rep) for rep in reps.split(",")]
            weights = [float(weight) for weight in weights.split(",")]
        except ValueError:
            return None, None, None, None

        # make sure the number of reps matches the number of weights
        if len(reps) != len(weights):
            return None, None, None, None

        # create set_details
        set_details = list(zip(reps, weights))

        # call your function to store exercise data in the database
        save_exercise(selected_exercise_id, notes, date, set_details)

        # clear the inputs and return the success message
        return None, "", "", ""


if __name__ == "__main__":
    app.run_server(debug=True, port=8069)
