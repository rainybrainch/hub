# 📅 習慣改善サイクル - セットアップガイド

## 概要

習慣アプリの「作製と改善のサイクルを1分ごとに自動実行」するローカルシステムです。

### 機能

- ✓ **1分ごとの自動実行** ── Windows タスクスケジューラで毎分実行
- ✓ **習慣データ分析** ── localStorage の習慣データを JSON ファイルから読み込み
- ✓ **統計分析** ── 完了数、完了率、7日間の完了パターン
- ✓ **改善提案自動生成** ── 完了率が低い習慣や未完了習慣の最適化
- ✓ **改善ログ記録** ── `habit-improvements.json` に毎回の分析結果を記録
- ✓ **エラーハンドリング** ── 失敗時も自動ログに記録

### ファイル構成

```
C:\tmp\hub\
├── habit.html                      # 習慣アプリ本体
├── export-habit-data.html          # localStorage データエクスポート画面
├── habit-cycle.py                  # 改善サイクル実行スクリプト
├── setup-scheduler.ps1             # タスクスケジューラ設定スクリプト
├── habit-data.json                 # 習慣データ（自動生成）
├── habit-improvements.json         # 改善ログ（毎分更新）
├── logs/                           # 実行ログディレクトリ
│   └── habit-cycle.log             # 詳細ログ
└── HABIT-CYCLE-SETUP.md           # このファイル
```

---

## セットアップ手順

### Step 1: Python 3.8+ をインストール

習慣改善スクリプトは Python で実行されます。

**確認コマンド（PowerShell）:**
```powershell
python --version
```

インストール済みの場合 → 3.8 以上でしたら OK  
未インストール → https://www.python.org/downloads/ からインストール

---

### Step 2: 習慣データの準備

#### 2-1. 習慣を追加

1. `C:\tmp\hub\habit.html` をブラウザで開く
2. 「新しい習慣を追加」セクションで習慣を登録（例：朝ラン、読書）
3. チェックボックスをクリックして本日の完了/未完了を切り替え

#### 2-2. データを JSON ファイルにエクスポート

1. `C:\tmp\hub\export-habit-data.html` をブラウザで開く
2. **「1分ごとに自動エクスポート」ボタン** をクリック
3. **そのタブをブラウザで開き続ける**（habit-data.json を毎分更新するため）

#### 補足

- エクスポート画面を閉じると、自動生成は止まります
- 手動で「🔽 今すぐエクスポート」をクリックしても可
- ブラウザのコンソール（F12）で `localStorage.getItem('habit_data')` で確認可

---

### Step 3: タスクスケジューラを設定

#### 3-1. PowerShell で スクリプト実行許可を変更（初回のみ）

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

プロンプトで `Y` を選択

#### 3-2. セットアップスクリプトを実行

```powershell
cd C:\tmp\hub
.\setup-scheduler.ps1
```

このスクリプトが自動で以下を行います：
- Python の存在確認
- タスクスケジューラへのタスク登録
- 実行ディレクトリの作成
- テスト実行

#### 3-3. 成功確認

```
✓ セットアップ完了！
```

が表示されたら OK です。

---

### Step 4: 動作確認

#### 方法A：タスクスケジューラで確認（推奨）

1. Windows キー + R
2. `taskschd.msc` と入力 → Enter
3. 左パネル：「タスク スケジューラ ライブラリ」を開く
4. 「HabitImprovementCycle」を検索
5. **状態** が「準備完了」となっていることを確認
6. **トリガー** タブで「1分ごと」が設定されていることを確認

#### 方法B：ログファイルで確認

```powershell
# リアルタイム監視
Get-Content -Path "C:\tmp\hub\logs\habit-cycle.log" -Wait

# または PowerShell ISE で開く
notepad C:\tmp\hub\logs\habit-cycle.log
```

実行ログが毎分記録される：
```
[2026-06-19T12:00:00] 習慣改善サイクルスクリプト v1.0 起動
[2026-06-19T12:00:01] ✓ サイクル #1 完了
[2026-06-19T12:01:00] ✓ サイクル #2 完了
```

#### 方法C：改善ログを確認

```powershell
# JSON エディタで開く
code C:\tmp\hub\habit-improvements.json

# または PowerShell で整形表示
Get-Content C:\tmp\hub\habit-improvements.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

改善ログの構造：
```json
{
  "log": [
    {
      "timestamp": "2026-06-19T12:00:01",
      "cycle_number": 1,
      "analysis": {
        "today": "2026-06-19",
        "completed_today": 2,
        "total_habits": 5,
        "completion_rate": 40.0,
        "habit_stats": [...]
      },
      "suggestions": [
        {
          "type": "low_completion_rate",
          "severity": "high",
          "message": "完了率が40.0%と低めです...",
          "action": "reduce_habits_or_simplify"
        }
      ],
      "status": "success"
    }
  ]
}
```

---

## 使用方法

### 日常利用

1. **毎朝**：`habit.html` をブラウザで開く
2. **習慣実施後**：チェックボックスで完了を記録
3. **自動分析**：1分ごとに改善提案が `habit-improvements.json` に記録される
4. **改善実践**：ログの提案に従って習慣を調整

### ログを確認

```powershell
# 最新10件のサイクルを表示
Get-Content C:\tmp\hub\habit-improvements.json | ConvertFrom-Json | % {
    $_.log | Select-Object -Last 10 | ForEach-Object {
        "$($_.timestamp) | Cycle #$($_.cycle_number) | $($_.analysis.completion_rate)% | $($_.status)"
    }
}
```

### データをバックアップ

```powershell
# habit-improvements.json をコピー
Copy-Item C:\tmp\hub\habit-improvements.json `
    -Destination "C:\tmp\hub\habit-improvements.backup.$(Get-Date -Format 'yyyyMMdd-HHmm').json"
```

---

## トラブルシューティング

### Q: スクリプトが実行されない

**原因:** Python が見つからない、またはスクリプト位置が違う

**対策:**
```powershell
# Python の位置を確認
where python

# setup-scheduler.ps1 のスクリプト位置を確認
cd C:\tmp\hub
Get-Item .\habit-cycle.py
```

### Q: "Running script is not allowed" エラー

**原因:** PowerShell の実行ポリシーが制限

**対策:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: habit-data.json が空またはない

**原因:** export-habit-data.html で自動エクスポートが実行されていない

**対策:**
1. `export-habit-data.html` をブラウザで開く
2. 「1分ごとに自動エクスポート」ボタンをクリック
3. **ブラウザのタブを開き続ける**（重要）

### Q: タスクスケジューラで "Last Run Result" が失敗

**原因:** Python スクリプトのパスが違う、またはエラー

**対策:**
```powershell
# タスクを削除して再実行
Unregister-ScheduledTask -TaskName "HabitImprovementCycle" -Confirm:$false
.\setup-scheduler.ps1
```

### Q: ブラウザを閉じたい（自動エクスポートを止めたい）

**対策:** `export-habit-data.html` の「⏹ 自動停止」ボタンをクリック

代わりに以下のいずれかの方法で手動エクスポート：
1. 「🔽 今すぐエクスポート」を定期的にクリック
2. ブラウザの開発者ツール（F12）で手動実行

---

## 分析内容詳細

毎分実行される改善サイクルでは、以下の分析と提案が自動生成されます：

### 1. 本日の完了率分析

| 完了率 | 提案内容 |
|---|---|
| 0-50% | ❌ 低い。習慣を減らすか簡単にする |
| 50-75% | ⚠️ 中程度。あと少しで安定範囲に |
| 75%+ | ✓ 素晴らしい。維持する |

### 2. 完了されていない習慣の検出

7日間で1度も完了していない習慣を特定し、削除を検討するよう提案

### 3. 本日未完了の習慣リスト

「あと X つ頑張りましょう」と励ましメッセージ

### 4. 7日連続達成の祝福

完全な習慣化が成功した習慣を認識

---

## 停止・設定変更

### タスクを一時停止

```powershell
Disable-ScheduledTask -TaskName "HabitImprovementCycle"
```

### タスクを再開

```powershell
Enable-ScheduledTask -TaskName "HabitImprovementCycle"
```

### タスクを削除

```powershell
Unregister-ScheduledTask -TaskName "HabitImprovementCycle" -Confirm:$false
```

### 実行間隔を変更（例：5分ごと）

```powershell
# タスク削除後、setup-scheduler.ps1 を編集
# $trigger.Repetition の RepetitionInterval を変更
# (New-TimeSpan -Minutes 1) → (New-TimeSpan -Minutes 5)
```

---

## データフロー図

```
┌─────────────────────────────────────────────────────────┐
│ ブラウザ: habit.html (localStorage)                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (1分ごと) エクスポート
┌─────────────────────────────────────────────────────────┐
│ ファイル: habit-data.json                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼ (Windows タスクスケジューラ 1分ごと)
┌─────────────────────────────────────────────────────────┐
│ スクリプト: habit-cycle.py                               │
│ ├─ 習慣データを読み込み                                  │
│ ├─ 統計分析（完了率、7日パターン）                       │
│ ├─ 改善提案を生成                                        │
│ └─ ログに記録                                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ファイル: habit-improvements.json                         │
│ （最新20件のサイクルログを保持）                         │
└─────────────────────────────────────────────────────────┘
```

---

## よくある質問

**Q: PCを再起動しても自動実行は続く？**

A: はい。Windows タスクスケジューラはスタートアップで自動復帰します。

**Q: ブラウザを閉じたら？**

A: export-habit-data.html が非表示になるため、自動エクスポートが止まります。
その場合、習慣アプリで追加/更新した内容は改善サイクルに反映されません。

**Q: ログはいつまで保存される？**

A: habit-improvements.json は最新20件のサイクルを保持します。
それ以前のログは自動削除されます。（保存したい場合はバックアップしてください）

**Q: Python スクリプトを編集して機能追加したい**

A: `habit-cycle.py` は自由に編集可能です。
分析ロジックの追加、提案ルールの変更など、カスタマイズ可能です。

**Q: Linux/Mac で実行したい**

A: Python スクリプト自体は OS 非依存です。
Windows タスクスケジューラの代わりに `cron` を使用してください：

```bash
# crontab を編集
crontab -e

# 毎分実行
* * * * * cd /path/to/habit && python habit-cycle.py >> logs/habit-cycle.log 2>&1
```

---

## サポート

このシステムについて質問や改善要望がある場合は、スクリプト内の以下をご参照ください：

- **Python スクリプト**: `habit-cycle.py`
- **セットアップ**: `setup-scheduler.ps1`
- **エクスポート画面**: `export-habit-data.html`

各ファイルには詳細なコメントが記載されています。

---

**バージョン**: v1.0  
**最終更新**: 2026-06-19  
**対応 OS**: Windows 10/11
