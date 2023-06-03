# not used in the project, just for testing purposes
# pip install Werkzeug
from werkzeug.security import generate_password_hash

# ... rest of your code ...

# Create instances of the User model
users_data = [
    {"username": "test", "age": 30, "password": "test123"},
    {"username": "alexander", "age": 25, "password": "alex123"},
]

for data in users_data:
    username = data["username"]
    age = data["age"]
    password = data["password"]
    user = session.query(User).filter(User.username == username).first()
    if not user:
        # If user does not exist, create a new one
        hashed_password = generate_password_hash(password)
        user = User(username=username, age=age, password=hashed_password)
        session.add(user)
        session.commit()
    # Create a UserWeight instance linked to the user
    user_weight = UserWeight(user_id=user.id, weight=70, date_recorded=date.today())
    session.add(user_weight)

# Commit the session to save the changes to the database
session.commit()

###########################################################################
from werkzeug.security import check_password_hash


def check_password(username, entered_password):
    user = session.query(User).filter(User.username == username).first()
    if user and check_password_hash(user.password, entered_password):
        return True  # Password is correct
    else:
        return False  # Password is incorrect or user does not exist
