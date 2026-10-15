@echo off
title Publication vers GitHub - Arkose Dict'Action

echo ========================================================
echo    PUBLICATION AUTOMATIQUE VERS GITHUB ET STREAMLIT
echo ========================================================
echo.

:: Se positionner dans le dossier du projet
cd /d "%~dp0"

:: Verification de l'acces a Git
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Git n'est pas accessible.
    pause
    exit /b 1
)

:: Verifier s'il y a des modifications en cours
git status --porcelain > "%TEMP%\git_changes.tmp"
for %%A in ("%TEMP%\git_changes.tmp") do (
    if %%~zA==0 (
        echo [INFO] Aucune modification detectee dans le dossier.
        echo Tout est deja a jour sur GitHub !
        del "%TEMP%\git_changes.tmp" 2>nul
        echo.
        pause
        exit /b 0
    )
)
del "%TEMP%\git_changes.tmp" 2>nul

echo Fichiers modifies / nouveaux detectes :
echo --------------------------------------------------------
git status --short
echo --------------------------------------------------------
echo.

:: Demander un message de commit optionnel
set "msg="
set /p "msg=Message pour cette mise a jour (ou appuyez sur ENTREE pour automatique) : "

if "%msg%"=="" (
    set "msg=Mise a jour du %date% a %time:~0,5%"
)

echo.
echo 1/3 - Preparation des fichiers...
git add -A

echo 2/3 - Enregistrement local (commit)...
git commit -m "%msg%"

echo 3/3 - Envoi vers GitHub (push)...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  [SUCCES] Vos modifications sont en ligne sur GitHub !
    echo  Streamlit Cloud va se mettre a jour automatiquement.
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  [ATTENTION] L'envoi a echoue.
    echo  Verifiez votre connexion Internet.
    echo ========================================================
)

echo.
pause
