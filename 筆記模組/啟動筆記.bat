@echo off
chcp 65001 >nul
rem 雙擊這個檔案：啟動本機小伺服器並打開瀏覽器（http://localhost:8765）。關掉這個視窗就會停止。
cd /d "%~dp0"
where py >nul 2>nul && (py -3 serve.py %* & goto :end)
where python >nul 2>nul && (python serve.py %* & goto :end)
echo 找不到 Python。請到 https://www.python.org/downloads/ 安裝（勾選 Add python.exe to PATH）。
pause
:end
