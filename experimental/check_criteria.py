#!/usr/bin/env python3
"""
Criteria Format Checker for Tengu Benchmark
1tengu/の各ファイルで評価項目の形式をチェックするスクリプト
"""
import re
from pathlib import Path

def check_criteria_format(content, filename):
    """評価項目の形式をチェック"""
    
    lines = content.split('\n')
    state = 'search'  # search, reading_criteria, checking_indent, waiting_for_next
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if state == 'search':
            if line == '[評価項目]':
                state = 'reading_criteria'
        
        elif state == 'reading_criteria':
            if line == '':
                state = 'waiting_for_next'
            elif re.match(r'-.+:\d+点$', line):
                # 通常の評価項目
                pass
            elif re.match(r'-.+$', line):
                # 階層の親項目、インデント調査モードに移行
                state = 'checking_indent'
            else:
                return False  # 形式が正しくない
        
        elif state == 'checking_indent':
            if line == '':
                state = 'waiting_for_next'
            elif re.match(r'  -.+:\d+点$', line):
                # インデントされた子項目
                pass
            else:
                # インデントされていない場合はreading_criteriaに戻る
                state = 'reading_criteria'
                continue
        
        elif state == 'waiting_for_next':
            if line == '':
                # 空行はスキップ
                pass
            elif line == '[評価するモデルの回答]':
                return True  # OK
            else:
                return False  # 期待しない内容
        
        i += 1
    
    return False  # [評価項目]が見つからない、または正しく終了しなかった

def main():
    """メイン処理"""
    
    # 1tenguディレクトリの確認
    tengu_dir = Path("1tengu")
    if not tengu_dir.exists():
        print(f"エラー: {tengu_dir} ディレクトリが見つかりません")
        return
    
    # 各ファイルをチェック
    total_files = 0
    valid_files = 0
    
    for md_file in sorted(tengu_dir.glob("*.md")):
        total_files += 1
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if check_criteria_format(content, md_file.name):
                valid_files += 1
            else:
                print(f"✗ {md_file.name}")
        
        except Exception as e:
            print(f"✗ {md_file.name}: {e}")
    
    # 統計
    print(f"\n結果: {valid_files}/{total_files} 件が正常")

if __name__ == "__main__":
    main()
