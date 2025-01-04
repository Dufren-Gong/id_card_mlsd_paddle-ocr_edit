@echo off

set conda_env=%1

call conda activate %conda_env%

pyinstaller main_new.spec

exit /b

exit 0