# Heavy Weight (compound excercises) database app (Python, Plotly Dash)
## requirements / installation
Python >= 3.9<br>
sqlalchemy, dash & it's bootstrap<br>
<br>
You can use the info from the environment folder:
```shell
python -m pip install -r ./environment/requirements.txt
```
Or, for a fresh environmet:<br>
```shell
conda env create -f ./environment/conda.yaml
conda activate excercisedb
```

## Database model & build:<br>
run from sql folder:<br>
`create_db_sqlalchemy_standalone.py` followed by `create_users_sqlalchemy_standalone.py`<br>
Edit the create code manually at this point to add a new user.<br>
Finally, run the `sql_cmd_line_app.py` which contains a GUI to write gym excercising info for a (single) user.<br>
<br>
passwordtest.py is not functional/usable at this stage and might never be? TBD.<br>
After all, it's just for fun and practicing.<br>
(folder "regular_sql_not_alchemy" contains some earlier test scripts using raw sql commands)<br>
## How to run
Note: change the database name in the apps accordingly.<br>
If you want to use the plain command line app, then use 
```shell
python sql_cmd_line_app.py
```
For a more persistent, modern(?) usage, run the dash webserver app:
```shell
python sql_web_app.py
```
The webservice is currently at http://localhost:8069 (or http://127.0.0.1:8069).

## Updates
Latest Version 2023-07-04<br>
cmd line gui app - currently in a "locked" state. Will focus now on the web-app<br>
sql_web_app.py: weight input & date now functional. started with a version number.<br>
excercise data can now be entered. table (and body weight) view not dynamic yet.<br>
added a intervall timer to update the view, updated requirements.<br>
License: MIT

## Info
With some initial help of chatgpt and a bit with arjancodes https://www.youtube.com/watch?v=x1fCJ7sUXCM<br>

