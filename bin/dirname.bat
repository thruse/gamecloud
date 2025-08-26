@echo off
set full_path=%~f1
for %%i in ("%full_path%") do set real_dir=%%~dpi
echo %real_dir:~0,-1%

set full_path=
set real_dir=
