@echo off
REM ============================================================================
REM build_exe.bat — 打包 FalloutShelterCN.exe（零依赖单文件）
REM
REM 本脚本是本地与 GitHub Actions 共用的唯一构建入口，两处执行的完全一致：
REM   PyInstaller 默认会把「当前时间」写进 PE 头 TimeDateStamp（源码注释原话是
REM   "增加熵"），并且 base_library.zip 的条目顺序受 str 哈希随机化影响 ——
REM   两处都会导致同一份代码产出的 EXE md5 每次都不同。这里统一固定：
REM     SOURCE_DATE_EPOCH = 当前 commit 时间（PyInstaller 会读取）
REM     PYTHONHASHSEED    = 0（消除模块遍历顺序的随机性）
REM
REM 用法：
REM   双击 / cmd 运行              正常交互式构建（结束停住）
REM   build_exe.bat --ci           CI 模式（不停住、不 pause）
REM   环境变量 PYTHON=...          解释器完整路径（默认 python；路径含空格时请勿用引号包裹外层）
REM
REM 依赖版本见 tools/requirements-exe.txt（全量锁定，含传递依赖）。
REM ============================================================================
chcp 65001 >nul 2>&1
setlocal
title 打包 FalloutShelterCN.exe
cd /d "%~dp0"

set "CI_MODE="
if /I "%~1"=="--ci" set "CI_MODE=1"
if not defined PYTHON set "PYTHON=python"

echo == 检查 Python ^& 依赖 ==
"%PYTHON%" -c "import PyInstaller, UnityPy; print('PyInstaller', PyInstaller.__version__, '| UnityPy', UnityPy.__version__ if hasattr(UnityPy,'__version__') else 'OK')"
if errorlevel 1 (
    echo [错误] 缺 PyInstaller 或 UnityPy。按锁定版本安装:
    echo   %PYTHON% -m pip install -r tools\requirements-exe.txt
    if not defined CI_MODE pause
    exit /b 1
)

echo == 固定可复现构建的环境 ==
set "PYTHONHASHSEED=0"
set "EPOCH="
for /f "delims=" %%i in ('git log -1 "--format=%%ct" 2^>nul') do set "EPOCH=%%i"
if not defined EPOCH (
    set "EPOCH=1735689600"
    echo [提示] 取不到 git commit 时间，回退到固定值 1735689600
)
set "SOURCE_DATE_EPOCH=%EPOCH%"
echo   PYTHONHASHSEED=%PYTHONHASHSEED%  SOURCE_DATE_EPOCH=%SOURCE_DATE_EPOCH%

echo == 打包（build_exe.spec，内嵌 翻译表+EN参考+字体+图标） ==
"%PYTHON%" -m PyInstaller --noconfirm --clean build_exe.spec
if errorlevel 1 ( echo [错误] 打包失败 & if not defined CI_MODE pause & exit /b 1 )

echo.
echo == 产物指纹 ==
set "EXE=%~dp0dist\FalloutShelterCN.exe"
for %%A in ("%EXE%") do echo   路径: %%A  ^(%%~zA 字节^)
for /f "skip=1 tokens=* delims=" %%h in ('certutil -hashfile "%EXE%" MD5') do (
    if not defined MD5 set "MD5=%%h"
)
for /f "skip=1 tokens=* delims=" %%h in ('certutil -hashfile "%EXE%" SHA256') do (
    if not defined SHA set "SHA=%%h"
)
echo   MD5:    %MD5%
echo   SHA256: %SHA%

echo.
echo == 完成 ==
echo EXE: %EXE%
echo 复制给玩家即可（双击即用；34MB 上下，无需 Python）。
if not defined CI_MODE pause
endlocal
