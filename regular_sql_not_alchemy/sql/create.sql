CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT
);

CREATE TABLE exercise_types (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL UNIQUE
);

CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    exercise_type_id INTEGER NOT NULL,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (exercise_type_id) REFERENCES exercise_types(id)
);

CREATE TABLE exercise_sets (
    id INTEGER PRIMARY KEY,
    exercise_id INTEGER NOT NULL,
    set_number INTEGER NOT NULL,
    repetitions INTEGER NOT NULL,
    weight REAL NOT NULL,
    date_performed DATE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
);

INSERT INTO exercise_types (type) VALUES ('Deadlift');
INSERT INTO exercise_types (type) VALUES ('Squat');
INSERT INTO exercise_types (type) VALUES ('Bench');
INSERT INTO exercise_types (type) VALUES ('Overhead');
INSERT INTO exercise_types (type) VALUES ('Pull-ups');
INSERT INTO exercise_types (type) VALUES ('Other');
