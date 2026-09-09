@echo off
REM build_exe.bat — 在 Windows 侧打包 FalloutShelterCN.exe（零依赖单文件）
REM 用法: 双击（或 cmd 运行）。需已装 Python 3.12 + pyinstaller + unitypy。
chcp 65001 >nul 2>&1
setlocal
title 打包 FalloutShelterCN.exe
cd /d "%~dp0"

echo == 检查 Python & 依赖 ==
python -c "import PyInstaller, UnityPy; print('PyInstaller', PyInstaller.__version__, '| UnityPy OK')" >nul 2>&1
if errorlevel 1 (
    echo [错误] 缺 PyInstaller 或 UnityPy。本机 Python 上安装:
    echo   py -3.12 -m pip install unitypy==1.25.3 pyinstaller
    pause & exit /b 1
)

echo == 打包（build_exe.spec，内嵌 翻译表+EN参考+字体+图标） ==
python -m PyInstaller --noconfirm --clean build_exe.spec
if errorlevel 1 ( echo [错误] 打包失败 & pause & exit /b 1 )

echo.
echo == 完成 ==
echo EXE: %~dp0dist\FalloutShelterCN.exe
echo 复制给玩家即可（双击即用；34MB 上下，无需 Python）。
pause
endlocal
