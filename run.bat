@echo off
setlocal enabledelayedexpansion

:menu
cls
echo.
echo === Image Generator Commands ===
echo.
echo 1. Generate 1 random image
echo    Command: python gen_images.py
echo.
echo 2. Generate 5 noise images
echo    Command: python gen_images.py --count 5 --pattern noise
echo.
echo 3. Generate 10 images with default pattern and 5 seconds delay
echo    Command: python gen_images.py --count 10 --delay 5
echo.
echo 4. Generate 100 digit images with 6 seconds delay
echo    Command: python gen_images.py --count 100 --pattern digits --delay 6
echo.
echo 5. Generate 10 gradient images with 2 seconds delay
echo    Command: python gen_images.py --count 10 --pattern gradient --delay 2
echo.
echo 6. Exit
echo.
set /p choice="Masukkan pilihan (1-6): "

if "%choice%"=="1" goto cmd1
if "%choice%"=="2" goto cmd2
if "%choice%"=="3" goto cmd3
if "%choice%"=="4" goto cmd4
if "%choice%"=="5" goto cmd5
if "%choice%"=="6" goto exit
echo Pilihan tidak valid. Coba lagi.
pause
goto menu

:cmd1
    echo Menjalankan: Generate 1 random image
    :repeat_cmd1
    python gen_images.py
    set /p ulang="Apakah ingin ulang command ini? (y/n): "
    if /i "%ulang%"=="y" goto repeat_cmd1
    goto menu

:cmd2
    echo Menjalankan: Generate 5 noise images
    :repeat_cmd2
    python gen_images.py --count 5 --pattern noise
    set /p ulang="Apakah ingin ulang command ini? (y/n): "
    if /i "%ulang%"=="y" goto repeat_cmd2
    goto menu

:cmd3
    echo Menjalankan: Generate 10 images with default pattern and 5 seconds delay
    :repeat_cmd3
    python gen_images.py --count 10 --delay 5
    set /p ulang="Apakah ingin ulang command ini? (y/n): "
    if /i "%ulang%"=="y" goto repeat_cmd3
    goto menu

:cmd4
    echo Menjalankan: Generate 100 digit images dengan 6 seconds delay
    :repeat_cmd4
    python gen_images.py --count 100 --pattern digits --delay 6
    set /p ulang="Apakah ingin ulang command ini? (y/n): "
    if /i "%ulang%"=="y" goto repeat_cmd4
    goto menu

:cmd5
    echo Menjalankan: Generate 10 gradient images dengan 2 seconds delay
    :repeat_cmd5
    python gen_images.py --count 10 --pattern gradient --delay 2
    set /p ulang="Apakah ingin ulang command ini? (y/n): "
    if /i "%ulang%"=="y" goto repeat_cmd5
    goto menu

:exit
echo Terima kasih telah menggunakan Image Generator!
pause
exit
