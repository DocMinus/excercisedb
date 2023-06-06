# Database testing, here as an gym-database
## requirements
Python >= 3.9<br>
sqlalchemy<br>
eventually dash, currently though only using the commandline.<br>
"old-school text GUI" :D <br>

##
database model & build:<br>
run from sql folder:<br>
`create_db_sqlalchemy_standalone.py` followed by `create_users_sqlalchemy_standalone.py`<br>
edit the create code manually at this point to add a new user.<br>
Finally, run the `sql_cmd_line_app.py` which has some read/write options for a current (single user).<br>
<br>
passwordtest.py and dashapp.py are not functional/usable at this stage and might never be? TBD.<br>
After all, it's just for fun and practicing.<br>
(folder "regular_sql_not_alchemy" contains some earlier test scripts using raw sql commands)<br>
## info
with some initial help of chatgpt and a bit with arjancodes https://www.youtube.com/watch?v=x1fCJ7sUXCM<br>
## Updates
Latest Version 2023-06-06<br>
Added some more functions/changed the "GUI", added some documentation to the functions<br>
License: MIT

