@echo off

set conda_env=%1

conda activate %conda_env%

pyinstaller main_new.spec

exit 0