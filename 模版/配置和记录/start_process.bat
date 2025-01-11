@echo off

set conda_env=%1

call conda activate %conda_env%

python main.py