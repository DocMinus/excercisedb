""" create the db using sqlalchemy
    simpliefied regarding users, although it can be expanded if desired.
    removed password requirement entirely, as it is not needed for this project.
"""
# importing the libraries
from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, create_engine

# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


# the tables for the db
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)


class UserWeight(Base):
    __tablename__ = "user_weights"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    weight = Column(Float, nullable=False)
    date_recorded = Column(Date, nullable=False)

    user = relationship("User")


class ExerciseType(Base):
    __tablename__ = "exercise_types"
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False, unique=True)


class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_type_id = Column(Integer, ForeignKey("exercise_types.id"))
    notes = Column(String)
    date_performed = Column(Date)

    user = relationship("User")
    exercise_type = relationship("ExerciseType")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"
    id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    set_number = Column(Integer, nullable=False)
    repetitions = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)

    exercise = relationship("Exercise")


# creating the db
engine = create_engine("sqlite:///database/exercise_alchemy_log_test.db")
Base.metadata.create_all(engine)

# creating the exercise types
# Define a Session class
Session = sessionmaker(bind=engine)

# Create a new session
session = Session()

# Create instances of the ExerciseType model
exercise_types = [
    ExerciseType(type="Deadlift"),
    ExerciseType(type="Squat"),
    ExerciseType(type="Bench"),
    ExerciseType(type="Overhead"),
    ExerciseType(type="Pull-ups"),
    ExerciseType(type="Other"),
]

# Add the instances to the session
for exercise_type in exercise_types:
    session.add(exercise_type)

# Commit the session to save the changes to the database
session.commit()

# Close the session
session.close()
