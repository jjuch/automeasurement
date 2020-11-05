@REM Run this file to setup the folder after a github clone

@REM Do not track config files
git update-index --assume-unchanged config/measurement.py
git update-index --assume-unchanged config/secrets.py
git update-index --assume-unchanged config/mail.py
git update-index --assume-unchanged config/sensor.py

@REM Create the virtual environment
python -m venv ENV
call ENV/Scripts/activate.bat
pip install -r config/requirements.txt

echo "Successfull setup"