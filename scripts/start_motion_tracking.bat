:: This script will only show errors on the console
:: the actual data is being logged into the logfiles


:: we need to be at the directory of the script because every python filepath is recorded regarding the main script location
cd ..


:: Live DEV: start all minimized
@REM start /min py motion_tracking_v1.py nole1
@REM start /min py motion_tracking_v1.py nole2
@REM start /min py motion_tracking_v1.py nole3
@REM start /min py motion_tracking_v1.py nole4
@REM start /min py motion_tracking_v1.py nole5
@REM start /min py motion_tracking_v1.py nole6
@REM start /min py motion_tracking_v1.py nole7
@REM start /min py motion_tracking_v1.py nole8
@REM start /min py motion_tracking_v1.py nole9
@REM start /min py motion_tracking_v1.py nole10
@REM start /min py motion_tracking_v1.py nole11
@REM start /min py motion_tracking_v1.py dawara

:: DEV: start all minimized and log output
start /min cmd /C "py motion_tracking_v1.py nole1  >>  logs\motion_tracking\log_nole1.log"
start /min cmd /C "py motion_tracking_v1.py nole2  >>  logs\motion_tracking\log_nole2.log"
start /min cmd /C "py motion_tracking_v1.py nole3  >>  logs\motion_tracking\log_nole3.log"
start /min cmd /C "py motion_tracking_v1.py nole4  >>  logs\motion_tracking\log_nole4.log"
start /min cmd /C "py motion_tracking_v1.py nole5  >>  logs\motion_tracking\log_nole5.log"
start /min cmd /C "py motion_tracking_v1.py nole6  >>  logs\motion_tracking\log_nole6.log"
start /min cmd /C "py motion_tracking_v1.py nole7  >>  logs\motion_tracking\log_nole7.log"
start /min cmd /C "py motion_tracking_v1.py nole8  >>  logs\motion_tracking\log_nole8.log"
start /min cmd /C "py motion_tracking_v1.py nole9  >>  logs\motion_tracking\log_nole9.log"
start /min cmd /C "py motion_tracking_v1.py nole10 >> logs\motion_tracking\log_nole10.log"
start /min cmd /C "py motion_tracking_v1.py nole11 >> logs\motion_tracking\log_nole11.log"
start /min cmd /C "py motion_tracking_v1.py dawara >> logs\motion_tracking\log_dawara.log"


:: Prod: to start them hidden
@REM pythonw motion_tracking_v1.py nole1 
@REM pythonw motion_tracking_v1.py nole2 
@REM pythonw motion_tracking_v1.py nole3 
@REM pythonw motion_tracking_v1.py nole4 
@REM pythonw motion_tracking_v1.py nole5 
@REM pythonw motion_tracking_v1.py nole6 
@REM pythonw motion_tracking_v1.py nole7 
@REM pythonw motion_tracking_v1.py nole8 
@REM pythonw motion_tracking_v1.py nole9 
@REM pythonw motion_tracking_v1.py nole10
@REM pythonw motion_tracking_v1.py nole11
@REM pythonw motion_tracking_v1.py dawara


:: to auto start create shortcut at C:\Users\Mohab\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
:: to auto start create shortcut at C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp




:: Prod: Using pm2 through pm2 start ecosystem.config.js