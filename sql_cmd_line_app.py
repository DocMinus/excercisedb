import datetime

import pandas as pd
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.db_classes import *

# Initialize the database
engine = create_engine("sqlite:///database/exercise_alchemy_log_test.db")
Session = sessionmaker(bind=engine)

# Get the list of users from the database
# and in this case a fixed user is used
session = Session()
available_users = session.query(User).all()
user = available_users[0]
user_id = user.id
user_name = user.username
session.close()


def get_latest_exercises(user_id: int) -> pd.DataFrame:
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


def save_exercise(exercise_id, notes, date, set_details):
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

    return None


def get_exercise_types() -> list:
    # Get the list of exercise types from the database
    session = Session()
    exercise_types = session.query(ExerciseType).all()
    session.close()
    # # Convert the result to a pandas DataFrame
    # df = pd.DataFrame(exercise_types, columns=["id", "type"])

    return exercise_types


def write_user_weight(user_id: int, weight: float, date_recorded=None):
    if date_recorded is None:
        date_recorded = datetime.date.today()
    # Create a new session
    session = Session()
    # read latest weight entry from database
    latest_weight = (
        session.query(UserWeight).order_by(UserWeight.date_recorded.desc()).first()
    )
    print(
        f"{user_name}'s latest recorded weight: {latest_weight.weight}kg on {latest_weight.date_recorded}"
    )
    # Create a UserWeight instance linked to the user
    user_weight = UserWeight(
        user_id=user_id, weight=weight, date_recorded=date_recorded
    )
    print(user_weight)
    session.add(user_weight)
    session.commit()
    session.close()
    return None


def update_user_weight(weight_id: int, new_weight: float, new_date_recorded=None):
    # update the weight entry with the given id
    # date could be updated as well, but for now it is not (see further below)
    if new_date_recorded is None:
        new_date_recorded = datetime.date.today()

    session = Session()

    # Fetch the weight entry you want to update
    user_weight = session.get(UserWeight, weight_id)
    if user_weight is None:
        print("No weight entry found with the given id.")
        return None
    # Update the fields
    user_weight.weight = new_weight
    user_weight.date_recorded = new_date_recorded
    session.commit()

    print(
        f"Updated weight id {weight_id} with new weight {new_weight}kg on {new_date_recorded}"
    )
    session.close()
    return None


def delete_user_weight(weight_id: int):
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
    return None


def update_username(username_new: str, username_current: str):
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

    return None


def get_personal_best(user_id: int) -> pd.DataFrame:
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


def create_excercise_day():
    excercise_id = int(input("\nEnter the id of the exercise type (0 to quit): "))
    if excercise_id == 0:
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

    print("Saving the following details:")
    save_exercise(excercise_id, notes, date, set_details)
    return True


def main():
    print("\n-------------------\n")
    print(f"Welcome {user_name}!")
    print(f"Current Date/Time: {datetime.datetime.now()}")
    print("\n-------------------\n")

    ###########################################
    # some manual function calls for now only:
    #
    # date_specific = datetime.datetime.strptime("2023-05-28", "%Y-%m-%d").date()
    # write_user_weight(user_id, 82.0, date_specific)  # datetime.date.today())
    # update_user_weight(1, 83.0, date_specific)  # update the weight entry with id 1
    # update_username("Alexander", "alexander")
    #
    ###########################################
    print("your latest exercises:")
    print(get_latest_exercises(user_id))
    print("\n-------------------\n")
    print("your PBs:")
    print(get_personal_best(user_id))
    print("\n-------------------\n")

    print("The following excerise types are available:")
    print("id\ttype")
    excercises = get_exercise_types()
    for i in excercises:
        print(i.id, "\t", i.type)
    print("\n-------------------\n")

    while True:
        status = create_excercise_day()
        if status is False:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
