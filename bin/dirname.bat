@echo off
set full_path=%~f1
for %%i in ("%full_path%") do set dir_name=%%~dpi
echo %dir_name:~0,-1%

set full_path=
set dir_name=
