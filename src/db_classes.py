# double check that the model is the same as in the sql creation, there is auto double check for now

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

if "Base" not in locals():
    Base = declarative_base()


# Existing database model
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
