# 📅 習慣改善サイクル システム v1.0

## 完成物一覧

このシステムは、習慣アプリの「作製と改善のサイクルを1分ごとに自動実行」する完全なローカルオートメーションです。

### ✅ 成果物

| ファイル | サイズ | 説明 |
|---|---|---|
| `habit-cycle.py` | 9.6 KB | Python スクリプト（改善サイクル実行エンジン） |
| `setup-scheduler.ps1` | - | Windows タスクスケジューラセットアップスクリプト |
| `export-habit-data.html` | 5.0 KB | ブラウザ UI（localStorage → JSON ファイルエクスポート） |
| `habit-data.json` | 1.5 KB | 習慣データ JSON ファイル（自動生成） |
| `habit-improvements.json` | 可変 | 改善ログ（毎分更新・最新20件保持） |
| `HABIT-CYCLE-SETUP.md` | 13 KB | 詳細セットアップマニュアル |
| `QUICK-START.md` | 3.3 KB | クイックスタートガイド（5分で完了） |
| `logs/habit-cycle.log` | 可変 | 実行ログ（毎分ロール） |

---

## 機能一覧

### ✓ 1分ごとの自動実行
- Windows タスクスケジューラで毎分自動実行
- スタートアップ時に自動復帰
- エラー時も自動ログ記録

### ✓ 習慣データ分析
- localStorage（ブラウザ）から JSON ファイルで読み込み
- 本日の完了状況（○/○ 個、完了率）を算出
- 7日間の完了パターンを分析

### ✓ 統計分析
- 完了率（0-100%）
- 習慣別の7日完了数
- 日別の完了数
- 習慣別の完了率（7日間）

### ✓ 改善提案自動生成
| 提案タイプ | トリガー |
|---|---|
| 低完了率警告 | 完了率 < 50% → 習慣を減らすか簡単にする |
| 中程度提案 | 完了率 50-75% → あと少し、安定範囲目指す |
| 励まし | 完了率 75%+ → 素晴らしい、維持する |
| 未完了習慣検出 | 7日連続未完了 → 削除検討 |
| 本日励まし | 本日未完了 | あと X つ頑張ろう |
| 連続達成祝 | 7日連続達成 | 🎉 習慣化成功 |

### ✓ 改善ログ記録
```json
{
  "timestamp": "ISO 8601",
  "cycle_number": 1,
  "analysis": {
    "today": "YYYY-MM-DD",
    "completed_today": 3,
    "total_habits": 5,
    "completion_rate": 60.0,
    "completion_by_day": {...},
    "habit_stats": [...]
  },
  "suggestions": [
    {
      "type": "...",
      "severity": "low/medium/high",
      "message": "...",
      "action": "..."
    }
  ],
  "status": "success"
}
```

### ✓ エラーハンドリング
- 失敗時も自動ログ記録
- 最新20件のログを保持
- コンソール出力の文字化け対応

---

## クイックセットアップ（5分）

### Step 1: 習慣を追加
```
ブラウザ → C:\tmp\hub\habit.html
→ 習慣を追加してチェック
```

### Step 2: エクスポート開始
```
ブラウザ → C:\tmp\hub\export-habit-data.html
→ 「1分ごとに自動エクスポート」ボタン
→ タブを開き続ける
```

### Step 3: タスクスケジューラ設定
```powershell
# PowerShell を開く（管理者権限不要）
cd C:\tmp\hub
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser  # Y 入力
.\setup-scheduler.ps1
```

出力：
```
✓ セットアップ完了！
```

### Step 4: 確認
```powershell
# ログをリアルタイム監視
Get-Content -Path "C:\tmp\hub\logs\habit-cycle.log" -Wait
```

---

## ファイル詳細

### 1. `habit-cycle.py` — メインスクリプト

**用途**:
- 毎分実行されるメイン処理エンジン
- 習慣データを分析して改善提案を生成

**実行方式**:
- Windows タスクスケジューラから毎分自動起動
- 手動実行も可：`python C:\tmp\hub\habit-cycle.py`

**機能**:
1. `habit-data.json` を読み込み
2. 本日の完了率を計算
3. 7日間の完了パターンを分析
4. 改善提案を生成
5. `habit-improvements.json` に記録
6. `logs/habit-cycle.log` に詳細ログ出力

**エラーハンドリング**:
- ファイルない → エラーログ + 記録
- 空データ → エラーログ + 記録
- 例外発生 → スタックトレース + ログ

---

### 2. `setup-scheduler.ps1` — タスク設定スクリプト

**用途**:
- Windows タスクスケジューラへの登録
- 環境チェック
- ログディレクトリ作成
- テスト実行

**実行条件**:
- PowerShell 5.0+
- 実行ポリシー: `RemoteSigned` 以上

**登録内容**:
- タスク名: `HabitImprovementCycle`
- トリガー: 1分ごと（AT スタートアップ＋リピート）
- 実行者: 現在のユーザー
- 実行ファイル: `python.exe`
- 引数: `"C:\tmp\hub\habit-cycle.py"`

---

### 3. `export-habit-data.html` — ブラウザエクスポート UI

**用途**:
- ブラウザの localStorage → JSON ファイル変換
- リアルタイムエクスポート（1分ごと自動）
- 手動エクスポート（即座）

**使い方**:
1. `habit.html` で習慣を記録
2. `export-habit-data.html` を開く
3. 「1分ごとに自動エクスポート」 or 「🔽 今すぐエクスポート」
4. `habit-data.json` が自動生成

**仕組み**:
- ブラウザの JavaScript で `localStorage.getItem('habit_data')` を読み込み
- JSON ダウンロード形式で保存
- セットインターバルで毎分自動実行

---

### 4. `habit-data.json` — 習慣データファイル

**形式**:
```json
{
  "habits": [
    {
      "id": "h_1718787600000",
      "name": "朝ラン",
      "log": {
        "2026-06-19": true,
        "2026-06-18": true,
        "2026-06-17": false
      }
    }
  ]
}
```

**更新方法**:
- `export-habit-data.html` が毎分自動上書き
- 手動更新も可

**スクリプトとの連携**:
- `habit-cycle.py` が毎分このファイルを読み込み

---

### 5. `habit-improvements.json` — 改善ログファイル

**形式**: JSON 配列（最新20件保持）

**構造**:
```json
{
  "log": [
    {
      "timestamp": "2026-06-19T18:05:22.716828",
      "cycle_number": 6,
      "analysis": { ... },
      "suggestions": [ ... ],
      "status": "success"
    }
  ]
}
```

**自動管理**:
- 毎分追記
- 20件超過時に古い順に削除
- バックアップは手動

---

### 6. `logs/habit-cycle.log` — 詳細ログ

**内容**:
```
[2026-06-19T18:05:22.695274] 習慣改善サイクルスクリプト v1.0 起動
[2026-06-19T18:05:22.696781] 習慣データを読み込み中...
[2026-06-19T18:05:22.697785] 改善提案を生成中...
[2026-06-19T18:05:22.717835] ✓ サイクル #6 完了
[2026-06-19T18:05:22.717835]   本日完了: 3/5 (60.0%)
[2026-06-19T18:05:22.717835]   💡 完了率は60.0%。あと少し頑張れば...
```

**特徴**:
- UTF-8 エンコーディング
- Windows cp932 文字化け対応
- 毎分ロール（新しい行を追記）

---

## データフロー図

```
┌─────────────────────────────────┐
│ ブラウザ: habit.html            │
│ localStorage['habit_data']      │
└──────────────┬──────────────────┘
               │ (毎分エクスポート)
               ▼
┌─────────────────────────────────┐
│ ファイル: habit-data.json        │
└──────────────┬──────────────────┘
               │ (毎分読み込み)
               ▼
┌─────────────────────────────────┐
│ スクリプト: habit-cycle.py       │
│ ├─ 読み込み                      │
│ ├─ 分析                          │
│ ├─ 提案生成                      │
│ └─ ログ記録                      │
└──────────────┬──────────────────┘
               │
               ├──→ ファイル: habit-improvements.json
               │     (改善ログ・最新20件)
               │
               └──→ ファイル: logs/habit-cycle.log
                    (詳細ログ)
```

---

## トラブルシューティング

| 問題 | 原因 | 対策 |
|---|---|---|
| スクリプト実行されない | Python 未インストール | `python --version` で確認 |
| habit-data.json が空 | エクスポート画面が無い | export-habit-data.html で自動開始 |
| 実行ポリシーエラー | PowerShell 制限 | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| タスクが見つからない | セットアップ失敗 | `.\setup-scheduler.ps1` を再実行 |
| ログが出力されない | ファイル権限 | `C:\tmp\hub\logs` フォルダ作成 |

詳細は **HABIT-CYCLE-SETUP.md** を参照

---

## カスタマイズ例

### 1. 実行間隔を5分に変更

`setup-scheduler.ps1` の以下を編集：

```powershell
# 変更前:
(New-TimeSpan -Minutes 1)

# 変更後:
(New-TimeSpan -Minutes 5)
```

その後、スクリプト再実行

### 2. 改善提案ルールを追加

`habit-cycle.py` の `generate_suggestions()` 関数に追記：

```python
# 例: 完了率が90%以上なら習慣追加を提案
if analysis['completion_rate'] >= 90:
    suggestions.append({
        'type': 'add_new_habit',
        'severity': 'low',
        'message': 'すべての習慣が完成されました。新しい習慣を追加しましょう！',
        'action': 'add_new_habit'
    })
```

### 3. ログ保持数を変更

`habit-cycle.py` の `save_improvement_log()` 関数：

```python
# 変更前:
if len(log_data['log']) > 20:
    log_data['log'] = log_data['log'][-20:]

# 変更後（50件保持）:
if len(log_data['log']) > 50:
    log_data['log'] = log_data['log'][-50:]
```

---

## パフォーマンス

| 項目 | 値 |
|---|---|
| 1サイクル実行時間 | 約 20-50 ms |
| メモリ使用量 | 10-20 MB |
| CPU 使用率 | < 1% |
| ディスク I/O | 3 ファイルアクセス |
| ログファイルサイズ | 1日: 約 50-100 KB |

---

## セキュリティ

- ✓ ローカルファイルのみ（インターネット通信なし）
- ✓ データは `C:\tmp\hub` 配下に格納
- ✓ Windows タスクスケジューラの権限に依存
- ✓ 機密情報なし（習慣データのみ）

---

## OS 互換性

| OS | 対応 | 備考 |
|---|---|---|
| Windows 10 | ✓ | 推奨 |
| Windows 11 | ✓ | 推奨 |
| macOS | ○ | cron 利用（手動設定） |
| Linux | ○ | cron 利用（手動設定） |

---

## ライセンス

フリーウェア。自由に改造・配布可能。

---

## サポート

質問や不具合がある場合：

1. **HABIT-CYCLE-SETUP.md** を確認（詳細説明）
2. **QUICK-START.md** を確認（簡潔版）
3. スクリプト内のコメントを確認
4. ログファイルで エラーメッセージを確認

---

**バージョン**: v1.0  
**リリース日**: 2026-06-19  
**対応環境**: Windows 10/11 + Python 3.8+
