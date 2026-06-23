#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
習慣改善サイクル自動実行スクリプト
1分ごとに実行し、習慣データを分析＆改善提案を生成
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
HABIT_DATA_FILE = SCRIPT_DIR / "habit-data.json"  # localStorage export file
IMPROVEMENT_LOG_FILE = SCRIPT_DIR / "habit-improvements.json"
HABIT_HTML = SCRIPT_DIR / "habit.html"

# ============================================================================
# Utility Functions
# ============================================================================

def log_info(message):
    """File logging only (Windows console encoding issues)"""
    timestamp = datetime.now().isoformat()
    log_message = f"[{timestamp}] {message}"

    # ログファイルに書き込み
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "habit-cycle.log"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        pass

def log_error(message):
    """Error logging"""
    timestamp = datetime.now().isoformat()
    log_message = f"[{timestamp}] ERROR: {message}"

    # ログファイルに書き込み
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "habit-cycle.log"

    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    except Exception as e:
        pass

def export_habit_data_from_browser():
    """
    ブラウザの localStorage から習慣データをエクスポート
    （実装注：実際の運用では Node.js + Puppeteer や Selenium で自動化推奨）
    ここでは事前に JSON ファイルが存在すると仮定
    """
    # TODO: ブラウザ自動化が必要な場合は Playwright/Selenium 導入
    if not HABIT_DATA_FILE.exists():
        return None

    try:
        with open(HABIT_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to load habit data: {e}")
        return None

def analyze_habits(data):
    """習慣データを分析"""
    if not data or 'habits' not in data or len(data['habits']) == 0:
        return None

    today = datetime.now().strftime('%Y-%m-%d')
    habits = data['habits']

    # 本日の完了状況
    completed_today = sum(1 for h in habits if h.get('log', {}).get(today, False))
    total = len(habits)
    completion_rate = (completed_today / total * 100) if total > 0 else 0

    # 7日間の完了パターン分析
    completion_by_day = {}
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        count = sum(1 for h in habits if h.get('log', {}).get(d, False))
        completion_by_day[d] = count

    # 習慣別の完了頻度（7日間）
    habit_stats = []
    for habit in habits:
        completed_count = sum(
            1 for i in range(7)
            if habit.get('log', {}).get(
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                False
            )
        )
        habit_stats.append({
            'id': habit['id'],
            'name': habit['name'],
            'completed_7days': completed_count,
            'completion_rate_7days': (completed_count / 7 * 100)
        })

    return {
        'today': today,
        'completed_today': completed_today,
        'total_habits': total,
        'completion_rate': round(completion_rate, 1),
        'completion_by_day': completion_by_day,
        'habit_stats': sorted(habit_stats, key=lambda x: x['completed_7days'])
    }

def generate_suggestions(analysis):
    """分析結果から改善提案を生成"""
    suggestions = []

    if not analysis:
        return suggestions

    # 提案1: 完了率が低い場合
    if analysis['completion_rate'] < 50:
        suggestions.append({
            'type': 'low_completion_rate',
            'severity': 'high',
            'message': f"完了率が{analysis['completion_rate']}%と低めです。習慣の数を減らすか、より簡単にしてみてください。",
            'action': 'reduce_habits_or_simplify'
        })
    elif analysis['completion_rate'] < 75:
        suggestions.append({
            'type': 'medium_completion_rate',
            'severity': 'medium',
            'message': f"完了率は{analysis['completion_rate']}%。あと少し頑張れば安定範囲（80%以上）に到達できます。",
            'action': 'maintain_and_push'
        })
    else:
        suggestions.append({
            'type': 'high_completion_rate',
            'severity': 'low',
            'message': f"素晴らしい！完了率{analysis['completion_rate']}%を維持しましょう。",
            'action': 'maintain'
        })

    # 提案2: 完了されていない習慣を特定
    unfinished = [h for h in analysis['habit_stats'] if h['completed_7days'] == 0]
    if unfinished:
        habits_str = ', '.join([h['name'] for h in unfinished])
        suggestions.append({
            'type': 'unfinished_habits',
            'severity': 'medium',
            'message': f"完成されていない習慣: {habits_str}。これらは本当に必要ですか？",
            'action': 'review_or_delete'
        })

    # 提案3: 本日未完了の習慣
    today = analysis['today']
    if analysis['completed_today'] < analysis['total_habits']:
        suggestions.append({
            'type': 'incomplete_today',
            'severity': 'medium',
            'message': f"本日は {analysis['completed_today']}/{analysis['total_habits']} の習慣が完了。あと {analysis['total_habits'] - analysis['completed_today']} つ頑張りましょう！",
            'action': 'finish_today'
        })

    # 提案4: 7日継続した習慣を祝う
    excellent = [h for h in analysis['habit_stats'] if h['completed_7days'] == 7]
    if excellent:
        habits_str = ', '.join([h['name'] for h in excellent])
        suggestions.append({
            'type': 'habit_streak',
            'severity': 'low',
            'message': f"🎉 素晴らしい！7日連続達成: {habits_str}。これらは確実に習慣化されました！",
            'action': 'celebrate'
        })

    return suggestions

def load_improvement_log():
    """既存のログを読み込む"""
    if not IMPROVEMENT_LOG_FILE.exists():
        return {'log': []}

    try:
        with open(IMPROVEMENT_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to load improvement log: {e}")
        return {'log': []}

def save_improvement_log(log_data):
    """ログを保存（最新20件のみ保持）"""
    if len(log_data['log']) > 20:
        log_data['log'] = log_data['log'][-20:]

    try:
        with open(IMPROVEMENT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log_error(f"Failed to save improvement log: {e}")

def run_cycle():
    """改善サイクルを1回実行"""
    try:
        # Step 1: 習慣データを読み込み
        log_info("習慣データを読み込み中...")
        habit_data = export_habit_data_from_browser()

        if not habit_data:
            log_error("習慣データが見つかりません。habit-data.json を確認してください。")
            return False

        # Step 2: 分析を実行
        log_info("習慣データを分析中...")
        analysis = analyze_habits(habit_data)

        if not analysis:
            log_error("習慣データが空です。習慣を追加してください。")
            return False

        # Step 3: 改善提案を生成
        log_info("改善提案を生成中...")
        suggestions = generate_suggestions(analysis)

        # Step 4: ログに記録
        log_data = load_improvement_log()
        cycle_entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle_number': len(log_data['log']) + 1,
            'analysis': analysis,
            'suggestions': suggestions,
            'status': 'success'
        }

        log_data['log'].append(cycle_entry)
        save_improvement_log(log_data)

        # Step 5: コンソールに結果を出力
        log_info(f"✓ サイクル #{cycle_entry['cycle_number']} 完了")
        log_info(f"  本日完了: {analysis['completed_today']}/{analysis['total_habits']} ({analysis['completion_rate']}%)")
        for suggestion in suggestions:
            log_info(f"  💡 {suggestion['message']}")

        return True

    except Exception as e:
        log_error(f"サイクル実行中にエラーが発生: {e}")

        # エラーログを記録
        log_data = load_improvement_log()
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle_number': len(log_data['log']) + 1,
            'error': str(e),
            'status': 'error'
        }
        log_data['log'].append(error_entry)
        save_improvement_log(log_data)

        return False

# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    log_info(f"習慣改善サイクルスクリプト v1.0 起動")
    success = run_cycle()
    sys.exit(0 if success else 1)
