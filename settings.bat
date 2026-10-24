@echo off
chcp 65001 >nul
title Настройка макроса AION 2

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
    python -c "import json, os; p=os.path.join(r'%~dp0', 'config.json'); f=open(p, 'r', encoding='utf-8'); d=json.load(f); f.close(); km={'left':'LMB','right':'RMB','middle':'MMB'}; keys=', '.join([km.get(k.lower(), k.upper()) for k in d.get('keys', [])]); print('Текущие настройки:\n  Кнопка включения: ' + str(d.get('toggle_key', 'F10')) + '\n  Клавиши:          ' + keys)" 2>nul
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
        set "KEYS_JSON=!KEYS_JSON!, \"!k!\""
    ) else (
        set "KEYS_JSON=\"!k!\""
    )
)

echo.
echo ------------------------------------------------------
echo Клавиша активации (тумблер ВКЛ / ВЫКЛ)
echo Например: F10, F9, F12, Q, Z, X.
echo Нажмите Enter, чтобы оставить [F10].
set /p toggle_btn="Кнопка включения: "
if "%toggle_btn%"=="" set "toggle_btn=F10"

(
    echo {
    echo   "first_setup_done": true,
    echo   "components_verified": true,
    echo   "toggle_key": "%toggle_btn%",
    echo   "keys": [!KEYS_JSON!]
    echo }
) > "%~dp0config.json"

echo.
echo ======================================================
echo Настройки сохранены!
python -c "import json, os; p=os.path.join(r'%~dp0', 'config.json'); f=open(p, 'r', encoding='utf-8'); d=json.load(f); f.close(); km={'left':'LMB','right':'RMB','middle':'MMB'}; keys=', '.join([km.get(k.lower(), k.upper()) for k in d.get('keys', [])]); print('  Кнопка включения: ' + str(d.get('toggle_key', 'F10')) + '\n  Клавиши:          ' + keys)" 2>nul
echo ======================================================
echo.
pause
exit