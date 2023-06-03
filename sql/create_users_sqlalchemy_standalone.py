# importing the libraries
from datetime import date

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

if "Base" not in locals():
    Base = declarative_base()

engine = create_engine("sqlite:///database/exercise_alchemy_log_test.db")

# Define a Session class
Session = sessionmaker(bind=engine)

# Create a new session
session = Session()


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


# Create instances of the User model
# doing it for only one single user (for now)
usernames = ["Alexander"]
date_of_birth = [1901, 1, 1]
weights = [83]

for username, age, weight in zip(usernames, date_of_birth, weights):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        # If user does not exist, create a new one
        # might be not necessaryt if I use "unique" in the User class
        dob = date(*date_of_birth)
        user = User(username=username, date_of_birth=dob)
        session.add(user)
        session.commit()

    # Create a UserWeight instance linked to the user
    user_weight = UserWeight(user_id=user.id, weight=weight, date_recorded=date.today())
    session.add(user_weight)
    session.commit()


# Close the session
session.close()
