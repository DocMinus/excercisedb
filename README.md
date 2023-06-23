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
passwordtest.py and dashapp.py are not functional/usable at this stage and might never be? TBD.<br>
After all, it's just for fun and practicing.<br>
(folder "regular_sql_not_alchemy" contains some earlier test scripts using raw sql commands)<br>
## info
with some initial help of chatgpt and a bit with arjancodes https://www.youtube.com/watch?v=x1fCJ7sUXCM<br>
## Updates
Latest Version 2023-06-23<br>
Added some more functions/changed the "GUI", added some documentation to the functions; added a "combined_weight_total_over_time", and more info on installation.<br>
Gald midsommer - with the help of some beer I started on a dash variant, see file sql_web_app.py. It's not really functional with input/write, but it reads at least some stuff.<br>
License: MIT

