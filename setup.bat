@REM Run this file to setup the folder after a github clone

@REM Do not track config files
git update-index --assume-unchanged config/.

@REM Create the virtual environment
python -m venv ENV
call ENV/Scripts/activate.bat
pip install -r config/requirements.txt

echo "Successfull setup"