"""V0.0.2"""

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
# TODO this would have to be moved eventually but ok for now
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
    df = pd.DataFrame(exercises, columns=["date", "exercise_type"])

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
        return latest_weight_entry.weight
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

    # Print the total weight lifted and the date since when
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
        html.H1(f"Welcome {user_name}!"),
        html.H3(
            f"Current Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ; press F5 to refresh."
        ),
        html.H4(combined_weight_total_over_time(user_id)),
        html.H4(f"Your latest weight (by date): {get_latest_weight(user_id)}"),
        html.Hr(),
        html.Div(
            [
                html.Label("Update Weight (kg)"),
                dcc.Input(id="weight-input", type="number", value=""),
                html.Label("Date"),
                dcc.DatePickerSingle(
                    id="weightdate-input",
                    min_date_allowed=datetime.datetime(1999, 9, 9),
                    max_date_allowed=datetime.datetime.now(),
                    initial_visible_month=datetime.datetime.now(),
                ),
                html.Button("Submit", id="update-weight-button"),
            ]
        ),
        html.Hr(),
        html.H2("Your 5 Latest Exercises"),
        dash_table.DataTable(
            id="exercise-table",
            columns=[
                {"name": i, "id": i} for i in get_latest_exercises(user_id).columns
            ],
            data=get_latest_exercises(user_id).to_dict("records"),
        ),
        html.Hr(),
        # TODO work on this portion. For now not yet functional.
        # Placeholder for displaying exercise data
        html.Div(id="exercise-data"),
        # Dropdown menu for exercise selection
        dcc.Dropdown(
            id="exercise-dropdown",
            options=[{"label": i.type, "value": i.id} for i in get_exercise_types()],
            placeholder="Select an exercise to add data for...",
        ),
    ]
)


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


# Defining a callback for updating exercise data when a new exercise is selected
@app.callback(
    Output("exercise-data", "children"),
    Input("exercise-dropdown", "value"),
)
def update_exercise_data(selected_exercise_id):
    # Fetch the exercise data for the selected exercise
    exercise_data = get_exercise_data(selected_exercise_id)

    # Convert the data into a table using Dash's DataTable component
    exercise_table = dcc.DataTable(
        data=exercise_data.to_dict("records"),
        columns=[{"name": i, "id": i} for i in exercise_data.columns],
    )

    return exercise_table


if __name__ == "__main__":
    app.run_server(debug=True, port=8069)
