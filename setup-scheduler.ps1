# =============================================================================
# Windows タスクスケジューラ セットアップスクリプト
# 習慣改善サイクルを1分ごとに自動実行
# =============================================================================

# 実行ポリシーの確認
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "⚠️  実行ポリシーが制限されています。以下のコマンドを実行してください：" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    exit 1
}

# =============================================================================
# Configuration
# =============================================================================

$TASK_NAME = "HabitImprovementCycle"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PYTHON_SCRIPT = Join-Path $SCRIPT_DIR "habit-cycle.py"
$LOG_DIR = Join-Path $SCRIPT_DIR "logs"
$LOG_FILE = Join-Path $LOG_DIR "habit-cycle.log"

Write-Host "
╔════════════════════════════════════════════════════════════════╗
║  習慣改善サイクル - Windows タスクスケジューラ設定            ║
╚════════════════════════════════════════════════════════════════╝
" -ForegroundColor Cyan

Write-Host "📁 スクリプト位置: $SCRIPT_DIR" -ForegroundColor Green
Write-Host "📄 Python スクリプト: $PYTHON_SCRIPT" -ForegroundColor Green
Write-Host "📋 タスク名: $TASK_NAME" -ForegroundColor Green

# =============================================================================
# Step 1: Python スクリプトの存在確認
# =============================================================================

if (-not (Test-Path $PYTHON_SCRIPT)) {
    Write-Host "❌ エラー: Python スクリプトが見つかりません" -ForegroundColor Red
    Write-Host "   パス: $PYTHON_SCRIPT" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python スクリプトが見つかりました" -ForegroundColor Green

# =============================================================================
# Step 2: ログディレクトリを作成
# =============================================================================

if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null
    Write-Host "✓ ログディレクトリを作成しました: $LOG_DIR" -ForegroundColor Green
}

# =============================================================================
# Step 3: Python が利用可能か確認
# =============================================================================

try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python がインストールされています: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python が見つかりません。Python 3.8+ をインストールしてください。" -ForegroundColor Red
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Cyan
    exit 1
}

# =============================================================================
# Step 4: 既存タスクを削除（あれば）
# =============================================================================

$existingTask = Get-ScheduledTask -TaskName $TASK_NAME -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "⚠️  既存のタスク '$TASK_NAME' が見つかります。置き換えます..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false
    Write-Host "✓ 既存タスクを削除しました" -ForegroundColor Green
}

# =============================================================================
# Step 5: タスク実行用の PowerShell コマンドを生成
# =============================================================================

$taskAction = New-ScheduledTaskAction `
    -Execute "python.exe" `
    -Argument "`"$PYTHON_SCRIPT`"" `
    -WorkingDirectory $SCRIPT_DIR

# =============================================================================
# Step 6: トリガーを設定（1分ごとに実行）
# =============================================================================

$trigger = New-ScheduledTaskTrigger `
    -AtStartup

# 1分ごとの実行に変更
$trigger.Repetition = New-ScheduledTaskRepetition `
    -Duration ([timespan]::MaxValue) `
    -RepetitionInterval (New-TimeSpan -Minutes 1)

# =============================================================================
# Step 7: タスクプリンシパルを設定（現在のユーザーで実行）
# =============================================================================

$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# =============================================================================
# Step 8: タスク設定を定義
# =============================================================================

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 0 `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

# =============================================================================
# Step 9: タスクを登録
# =============================================================================

try {
    $task = Register-ScheduledTask `
        -TaskName $TASK_NAME `
        -Action $taskAction `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description "習慣改善サイクル自動実行 - 1分ごとに習慣データを分析して改善提案を生成" `
        -Force

    Write-Host "✓ タスクを登録しました！" -ForegroundColor Green
    Write-Host "  タスク名: $TASK_NAME" -ForegroundColor Green
    Write-Host "  実行頻度: 1分ごと" -ForegroundColor Green
    Write-Host "  ログファイル: $LOG_FILE" -ForegroundColor Green
} catch {
    Write-Host "❌ タスク登録エラー: $_" -ForegroundColor Red
    exit 1
}

# =============================================================================
# Step 10: 確認とテスト実行
# =============================================================================

Write-Host "`n📋 タスクスケジューラの設定を確認" -ForegroundColor Cyan
$registeredTask = Get-ScheduledTask -TaskName $TASK_NAME
Write-Host "  状態: $($registeredTask.State)" -ForegroundColor Green
Write-Host "  次実行予定: $($registeredTask.Triggers[0].StartBoundary)" -ForegroundColor Green

Write-Host "`n📌 テスト実行中..." -ForegroundColor Yellow
try {
    Start-ScheduledTask -TaskName $TASK_NAME
    Start-Sleep -Seconds 3
    Write-Host "✓ テスト実行を開始しました" -ForegroundColor Green
} catch {
    Write-Host "⚠️  テスト実行エラー（スケジューラが後で実行します）: $_" -ForegroundColor Yellow
}

# =============================================================================
# Step 11: 確認メッセージ
# =============================================================================

Write-Host "`n
╔════════════════════════════════════════════════════════════════╗
║  ✓ セットアップ完了！                                        ║
╚════════════════════════════════════════════════════════════════╝
" -ForegroundColor Green

Write-Host "📌 次のステップ：

1. 習慣データの準備（必須）
   - $SCRIPT_DIR\habit.html をブラウザで開く
   - 習慣を追加
   - $SCRIPT_DIR\export-habit-data.html を開く
   - 『1分ごとに自動エクスポート』ボタンをクリック
   - そのタブをブラウザで開き続ける

2. タスクスケジューラで確認
   - Win + R → taskschd.msc → Enter
   - タスク スケジューラ ライブラリ で '$TASK_NAME' を検索
   - 次実行予定時刻を確認

3. ログファイルで実行確認
   - $LOG_FILE で毎分の実行ログを確認

4. 改善提案の確認
   - $SCRIPT_DIR\habit-improvements.json で分析結果を確認
   - JSON エディタまたは 'code habit-improvements.json' で表示

🛑 停止する場合：
   - タスクスケジューラで '$TASK_NAME' を右クリック → 無効化
   - または PowerShell で: Unregister-ScheduledTask -TaskName '$TASK_NAME' -Confirm:$false

" -ForegroundColor Cyan

Write-Host "💡 注意：Windows 標準の実行ユーザーアカウントのみ対応
   管理者権限は不要（-RunLevel HighestにはなりますがUAC回避）" -ForegroundColor Yellow

# =============================================================================
# 実行完了
# =============================================================================

Write-Host "
✓ セットアップスクリプトが完了しました。
  タスクスケジューラでの自動実行が開始されます。
" -ForegroundColor Green
