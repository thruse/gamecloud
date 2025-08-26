@echo off

for /f "usebackq tokens=*" %%i in (`dirname %~f0`) do set bin_dir=%%i
for /f "usebackq tokens=*" %%i in (`dirname %bin_dir%`) do set gamecloud_dir=%%i

call python "%gamecloud_dir%\code\gamecloud.py" %*

set gamecloud_py=
set bin_dir=