@echo off
cls

REM Default action
set action=run

REM Check for command line arguments
if "%1" == "-c" (
    if not "%2" == "" (
        set action=run
        if "%2%" == "b" (
            set action=build
        )
    )
)

if "%action%"=="build" (
    echo Building project...
    pyinstaller --onefile --noconsole --icon=icon.ico --upx-dir=UPX mover.py
    set result=Build
) else (
    echo Running project...
    start cmd /c py .\mover.py
    set result=Run
)

echo You chose to %result% the project.
