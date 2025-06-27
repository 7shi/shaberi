#!/usr/bin/env python3
"""
問題固有の採点基準を抽出するツール

ELYZA-tasks-100の各タスクファイル（data/*.md）から
「問題固有の採点基準」～「# 回答」の間の内容を抽出して表示する。
"""

import os
import glob
from pathlib import Path


def extract_criteria(file_path):
    """
    指定されたファイルから問題固有の採点基準を抽出する。
    
    Args:
        file_path (str): 読み込むファイルのパス
        
    Returns:
        list: 抽出された行のリスト
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    s = text.find("問題固有の採点基準")
    if s < 0:
        raise ValueError('"問題固有の採点基準" が見付かりません。')
    
    e = text.find("# 回答")
    if e < 0:
        raise ValueError('"# 回答" が見付かりません。')
    
    return text[s+9:e].strip().splitlines()


def main():
    """メイン処理"""
    # 現在のディレクトリからdata/*.mdファイルを検索
    data_pattern = "data/*.md"
    md_files = sorted(glob.glob(data_pattern))
    
    if not md_files:
        print(f"ファイルが見つかりません: {data_pattern}")
        return
    
    for i, file_path in enumerate(md_files):
        # 問題固有の採点基準を抽出
        criteria = extract_criteria(file_path)
        if not criteria:
            raise ValueError("問題固有の採点基準なし")
        
        if i:
            print()
        
        # ファイル名から番号を抽出
        file_name = Path(file_path).stem
        print("#", file_name)
        print()
        
        for line in criteria:
            print(line)


if __name__ == "__main__":
    main()
