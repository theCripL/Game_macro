@echo off
chcp 65001 >nul
title Game Macro

cd /d "%~dp0"

net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process cmd -ArgumentList '/k \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

cls
echo ======================================================
echo             НАСТРОЙКА КЛАВИШ МАКРОСА
echo ======================================================
echo.

if exist "%~dp0config.json" (
    python "%~dp0print_settings.py"
    echo ------------------------------------------------------
    echo.
)

echo Допустимые варианты ввода:
echo   - Мышь:       LMB, RMB, MMB
echo   - Клавиатура: e, y, t, 1, 2, q, r, f и др.
echo.

:CHOOSE_COUNT
set /p count="Сколько клавиш удерживать (от 1 до 5)? "
if "%count%"=="" goto CHOOSE_COUNT
if %count% LSS 1 goto CHOOSE_COUNT
if %count% GTR 5 goto CHOOSE_COUNT

echo.
setlocal enabledelayedexpansion
set "KEYS_JSON="

for /l %%i in (1,1,%count%) do (
    :ENTER_KEY
    set /p "k=Клавиша #%%i: "
    if "!k!"=="" goto ENTER_KEY
    
    if /i "!k!"=="LMB" set "k=left"
    if /i "!k!"=="RMB" set "k=right"
    if /i "!k!"=="MMB" set "k=middle"

    if defined KEYS_JSON (
        set "KEYS_JSON=!KEYS_JSON!, "!k!""
    ) else (
        set "KEYS_JSON="!k!""
    )
)

echo.
echo ------------------------------------------------------
echo Клавиша активации (тумблер ВКЛ / ВЫКЛ)
echo Например: F10, F9, F12, Q, Z, X.
echo Нажмите Enter, чтобы оставить [F10].
set /p toggle_btn="Кнопка включения: "
if "%toggle_btn%"=="" set "toggle_btn=F10"

echo.
echo ------------------------------------------------------
echo Задержка в циклах удержания (в секундах)
echo Например: 0.02, 0.01, 0.05.
echo Нажмите Enter, чтобы оставить [0.02].
set /p delay_val="Задержка: "
if "%delay_val%"=="" set "delay_val=0.02"

(
    echo {
    echo   "first_setup_done": true,
    echo   "components_verified": true,
    echo   "toggle_key": "%toggle_btn%",
    echo   "keys": [%KEYS_JSON%],
    echo   "delay": %delay_val%
    echo }
) > "%~dp0config.json"

echo.
echo ======================================================
echo Настройки сохранены!
python "%~dp0print_settings.py"
echo ======================================================
echo.
pause
exit