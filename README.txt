INSTRUCTIONS

Preface: Don't worry if you don't have a secret_tokens.py file yet -- it will be generated on the first run of the server
Once you've opened your terminal, cd to SpeedSense

Prerequisite: run 'python -m pip install -r requirements.txt'

First, run 'python manage.py makemigrations WebApp'
then, 'python manage.py migrate'
then, 'python manage.py runserver'
and the server will be running and accessible on http://localhost:8000 by default!

To tunnel with pagekite:
Download 'pagekite.py' from pagekite
Add your credentials to your pagekite installation (see pagekite documentation)
Modify 'host.bat' to point to the location of your 'pagekite.py' file
Run 'host.bat' to make the server accessible at 'speedsense.pagekite.me'
