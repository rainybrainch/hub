# 🚀 習慣改善サイクル - クイックスタート（5分で完了）

## 前提条件

- Windows 10/11
- Python 3.8+ インストール済み
- PowerShell 実行権限

## 実行手順

### 1️⃣ 習慣を追加（2分）

```
ブラウザ → C:\tmp\hub\habit.html を開く
↓
「新しい習慣を追加」で習慣登録（例：朝ラン、読書）
↓
チェックボックスで本日の完了/未完了を記録
```

### 2️⃣ データエクスポートを開始（1分）

```
ブラウザ → C:\tmp\hub\export-habit-data.html を開く
↓
「1分ごとに自動エクスポート」ボタンクリック
↓
⚠️ ブラウザのタブを開き続ける（重要！）
```

### 3️⃣ タスクスケジューラを設定（2分）

PowerShell を**管理者以外**で開く：

```powershell
# Step A: 実行ポリシー設定（初回のみ）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Y を入力

# Step B: セットアップスクリプト実行
cd C:\tmp\hub
.\setup-scheduler.ps1
```

出力：
```
✓ セットアップ完了！
```

### ✅ 完了！

自動実行が開始されました。以下で確認：

```powershell
# ログをリアルタイム監視
Get-Content -Path "C:\tmp\hub\logs\habit-cycle.log" -Wait

# または改善ログを確認
notepad C:\tmp\hub\habit-improvements.json
```

---

## 動作確認

### 方法A: ログを確認（最速）

```powershell
# 毎分これが出力されたら成功
cat C:\tmp\hub\logs\habit-cycle.log | tail -5
```

期待出力：
```
[2026-06-19T12:00:00] 習慣改善サイクルスクリプト v1.0 起動
[2026-06-19T12:00:01] ✓ サイクル #1 完了
  本日完了: 2/5 (40.0%)
```

### 方法B: タスクスケジューラで確認

```
Win + R → taskschd.msc
↓
「HabitImprovementCycle」を検索
↓
状態が「準備完了」、トリガーが「1分ごと」なら OK
```

### 方法C: JSON ログで確認

```powershell
code C:\tmp\hub\habit-improvements.json
```

最新のサイクル結果が JSON で記録されている

---

## 日常使用

毎日のワークフロー：

```
1️⃣ 朝: habit.html を開く
   ↓
2️⃣ 習慣実施後: チェックボックスをクリック
   ↓
3️⃣ 夜: ログを確認して改善を実践
   ↓
4️⃣ 明日: 繰り返し
```

---

## よくある失敗（回避方法）

| 失敗 | 原因 | 対策 |
|---|---|---|
| スクリプトが実行されない | Python が見つからない | `python --version` で確認 |
| habit-data.json が空 | エクスポート画面を閉じた | export-habit-data.html で「自動エクスポート」再開 |
| 実行ポリシーエラー | PowerShell 設定が制限 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| タスクがリストに無い | セットアップ失敗 | `.\setup-scheduler.ps1` を再実行 |

---

## 停止方法

一時的に停止：
```powershell
Disable-ScheduledTask -TaskName "HabitImprovementCycle"
```

完全に削除：
```powershell
Unregister-ScheduledTask -TaskName "HabitImprovementCycle" -Confirm:$false
```

---

## 詳細マニュアル

詳しい設定・トラブルシューティングは **HABIT-CYCLE-SETUP.md** を参照

```powershell
notepad C:\tmp\hub\HABIT-CYCLE-SETUP.md
```

---

**🎉 準備完了！**
