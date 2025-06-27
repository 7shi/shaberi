#!/usr/bin/env python3
"""
conv_elyza.py - ELYZA-tasks-100データの単純分割ツール

このスクリプトは、2elyza.jsonからデータを読み込み、
元のJSONの中身を加工せずに単純に個々のファイルに分割出力します。
"""

import json
import os
from pathlib import Path

def main():
    """メイン処理"""
    # 入力ファイルの確認
    input_file = Path("../2elyza.json")
    if not input_file.exists():
        print(f"エラー: {input_file} が見つかりません")
        return
    
    # 出力ディレクトリの作成
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # 2elyza.jsonを読み込み（JSONL形式）
    with open(input_file, 'r', encoding='utf-8') as f:
        tasks = [line.strip() for line in f if line.strip()]
    
    print(f"読み込まれたタスク数: {len(tasks)}")
    
    # 各タスクを個別ファイルに分割
    for i, task_data in enumerate(tasks, 1):
        task_num = f"{i:03d}"
        
        # JSONをパースして文字列内容を個別ファイルに出力
        output_file = output_dir / f"{task_num}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            # JSONをパースして文字列内容を出力
            task_obj = json.loads(task_data)
            f.write(task_obj)
        
        if i % 20 == 0:
            print(f"処理済み: {i}/{len(tasks)}")
    
    print(f"\n完了: {len(tasks)}個のタスクを分割しました")
    print(f"出力先: {output_dir.absolute()}")

if __name__ == "__main__":
    main()