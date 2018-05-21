@echo off
if exist start.exe if exist vDosPlus-checkinstall.exe goto startup
echo Error: Executable not found.
goto :EOF
:startup
if exist %temp%\vDosPlus-checkinstall.exe del /f %temp%\vDosPlus-checkinstall.exe >nul 2>nul
if not exist %temp%\vDosPlus-checkinstall.exe goto cleancopy
copy /y vDosPlus-checkinstall.exe %temp% >nul 2>nul
fc.exe vDosPlus-checkinstall.exe %temp%\vDosPlus-checkinstall.exe >nul 2>nul
if errorlevel 1 (.\start.exe /max vDosPlus-checkinstall.exe) else .\start.exe /max %temp%\vDosPlus-checkinstall.exe
goto :EOF
:cleancopy
copy /y vDosPlus-checkinstall.exe %temp% >nul 2>nul
if exist %temp%\vDosPlus-checkinstall.exe (.\start.exe /max %temp%\vDosPlus-checkinstall.exe) else .\start.exe /max vDosPlus-checkinstall.exe
