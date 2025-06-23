#!/usr/bin/env python3
"""
JSON to MD Converter for Tengu Benchmark
../1tengu.json から各質問を個別のMDファイルに変換するスクリプト
"""
import json
import re
import os
from pathlib import Path


def main():
    """メイン処理"""
    
    # 入力ファイルの確認
    input_file = Path("../1tengu.json")
    if not input_file.exists():
        print(f"エラー: {input_file} が見つかりません")
        return
    
    # 出力ディレクトリの作成
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    # JSONファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"処理中: {len(lines)}件の評価タスク")
    
    success_count = 0
    error_count = 0
    
    for i, line in enumerate(lines, 1):
        try:
            # JSON行をパース
            md_content = json.loads(line.strip())
            
            # ファイルに出力
            output_file = output_dir / f"{i:03d}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            success_count += 1
            
        except Exception as e:
            print(f"エラー (行 {i}): {e}")
            error_count += 1
    
    print(f"\n変換完了:")
    print(f"  成功: {success_count}件")
    print(f"  エラー: {error_count}件")
    print(f"  出力ディレクトリ: {output_dir}")

if __name__ == "__main__":
    main()
