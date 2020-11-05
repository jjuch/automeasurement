@REM Get current path
SET full_path=%~dp0
@REM Activate environment
call %full_path%\ENV\Scripts\activate.bat
@REM Run src/main_files/main
%full_path%\ENV\Scripts\python.exe -m src.main_files.main