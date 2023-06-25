# Database testing, here as an gym-database
## requirements / installation
Python >= 3.9<br>
sqlalchemy<br>
eventually dash, currently though only using the commandline.<br>
"old-school text GUI" :D <br>
<br>
You can use the info from the environment folder:
```shell
python -m pip install -r ./environment/requirements.txt
```
Or, for a fresh environmet:<br>
```shell
conda env create -f ./environment/conda.yaml
conda activate py311chemdash
```

## database model & build:<br>
run from sql folder:<br>
`create_db_sqlalchemy_standalone.py` followed by `create_users_sqlalchemy_standalone.py`<br>
Edit the create code manually at this point to add a new user.<br>
Finally, run the `sql_cmd_line_app.py` which contains a GUI to write gym excercising info for a (single) user.<br>
<br>
passwordtest.py is not functional/usable at this stage and might never be? TBD.<br>
After all, it's just for fun and practicing.<br>
(folder "regular_sql_not_alchemy" contains some earlier test scripts using raw sql commands)<br>
## info
with some initial help of chatgpt and a bit with arjancodes https://www.youtube.com/watch?v=x1fCJ7sUXCM<br>
## Updates
Latest Version 2023-06-25<br>
cmd line gui app - currently in a "locked" state. Will focus now on the web-app<br>
sql_web_app.py: weight input & date now functional. started with a version number.<br>
License: MIT

