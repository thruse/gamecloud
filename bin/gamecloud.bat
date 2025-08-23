@echo off

set gamecloud_py=%~f0
for %%i in ("%gamecloud_py%") set gamecloud_py=%%~dpi
set gamecloud_py=%gamecloud_py:~0,-1%\..\gamecloud.py
for %%i in ("%gamecloud_py%") set gamecloud_py=%%~fi

call python %gamecloud_py% %*

set gamecloud_py=
