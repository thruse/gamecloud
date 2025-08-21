@echo off

set GAMECLOUD_PATH=%~f0
for %%i in ("%GAMECLOUD_PATH%") do set GAMECLOUD_PATH=%%~dpi
set GAMECLOUD_PATH=%GAMECLOUD_PATH:~0,-1%\gamecloud.py

call python %GAMECLOUD_PATH% %*

set GAMECLOUD_PATH=
