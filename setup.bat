@echo off
chcp 65001 > nul
echo ========================================
echo   pyMEA セットアップ
echo ========================================
echo.

if defined MEA_DATA_PATH (
  echo 現在の設定: %MEA_DATA_PATH%
  echo.
  set /p CHANGE="変更しますか？ (y/n): "
  if /i not "%CHANGE%"=="y" (
    echo 設定はそのままです。
    pause
    exit /b 0
  )
  echo.
)

echo 計測データが保存されているフォルダのパスを入力してください。
echo 例: E:\MEA_data
echo.
set /p NEW_PATH="データフォルダのパス: "

if "%NEW_PATH%"=="" (
  echo.
  echo エラー: パスが入力されていません。
  pause
  exit /b 1
)

if not exist "%NEW_PATH%" (
  echo.
  echo エラー: フォルダが見つかりません。パスを確認してください。
  pause
  exit /b 1
)

setx MEA_DATA_PATH "%NEW_PATH%"
echo.
echo ========================================
echo   設定完了！
echo ========================================
echo.
echo データフォルダ: %NEW_PATH%
echo.
echo コンテナ内からは /data でアクセスできます。
echo 例: read_MEA("/data/sample.hed", ...)
echo.
echo VS Code を再起動してから Dev Container を開いてください。
pause
