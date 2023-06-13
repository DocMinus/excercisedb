import datetime

import pandas as pd
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker

from src.db_classes import *

# Initialize the database #
# TODO this would have to be moved eventually but ok for now
# engine = create_engine("sqlite:///database/exercise_main.db")
engine = create_engine("sqlite:///database/exercise_main.db")
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


def combined_weight_total_over_time(user_id: int) -> None:
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
    print(f"Since {first_date}, you lifted a combined total of {total_weight} kg!")

    return None


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


def gui_main() -> int:
    """
    The main "GUI" function that runs the program.\n

    Returns: None
    """
    print("\n-------------------\n")
    print(f"Welcome {user_name}!")
    print(f"Current Date/Time: {datetime.datetime.now()}")
    print(f"Latest recorded Weight: {get_latest_weight(user_id)}")
    combined_weight_total_over_time(user_id)
    print("\n-------------------\n")

    print("your latest exercises:")
    print(get_latest_exercises(user_id))
    print("\n-------------------\n")
    print("your PBs:")
    print(get_personal_best(user_id))
    print("\n-------------------\n")

    print("Please choose excercise by ID or 0/9 to exit or upate your weight:")
    print("id\ttype")
    excercises = get_exercise_types()
    print("0\tExit")
    for i in excercises:
        print(i.id, "\t", i.type)
    print("9\tUpdate your weight")
    print("\n-------------------\n")

    menu_selection_id = int(input("\nEnter a number: "))
    return menu_selection_id


def gui_weight() -> None:
    """
    Prompts the user to input their weight and the date the weight was recorded.
    Then write to the db via the write_user_weight function. \n

    Returns: None
    """
    user_weight = float(input("\nEnter your weight: "))
    new_weight_date = input("Enter the date (YYYY-MM-DD) (empty=today): ")
    if new_weight_date == "":
        new_weight_date = datetime.date.today()
    write_user_weight(user_id, user_weight, new_weight_date)


def main():
    # yes, global not good pracice, but for this testing purpose deemed ok
    global user_id
    while True:
        menu_selection_id = gui_main()
        if menu_selection_id == 9:
            gui_weight()
        if menu_selection_id == 0:
            print("Exiting...")
            break
        elif menu_selection_id > 0 and menu_selection_id < 7:
            create_excercise_day(menu_selection_id)


if __name__ == "__main__":
    ###########################################
    # some manual function calls for now only:
    #
    # date_specific = datetime.datetime.strptime("2023-05-28", "%Y-%m-%d").date()
    # modify_user_weight(1, 83.0, date_specific)  # update the weight entry with id 1
    # update_username("Alexander", "alexander")
    #
    ###########################################
    main()
