#!/usr/bin/env python3
"""
rubrics/*.mdファイルからPythonコードを抽出し、コメントを削除して.pyファイルに変換するスクリプト
"""

import argparse
import os
import re
from pathlib import Path


def extract_python_code(content: str) -> str:
    """
    Markdownファイルから```python～```の部分を抽出
    
    Args:
        content: Markdownファイルの内容
        
    Returns:
        str: 抽出されたPythonコード
    """
    # ```python～```パターンを探す
    match = re.search(r'```python\s*\n(.*?)\n```', content, re.DOTALL)
    if match:
        return match.group(1)
    
    # 全体がPythonコードの場合（rubrics/001.mdのような形式）
    return content


def remove_comments(code: str) -> str:
    """
    Pythonコードからコメントを削除
    
    Args:
        code: Pythonコード
        
    Returns:
        str: コメントを削除したPythonコード
    """
    lines = code.split('\n')
    result_lines = []
    
    for line in lines:
        # コメント行（#で始まる行）を削除
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue
        
        # 行末のコメントを削除（文字列内の#は保持）
        # 簡単な実装：文字列内のチェックは省略
        comment_pos = line.find('#')
        if comment_pos != -1:
            line = line[:comment_pos].rstrip()
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def extract_criteria(file_path):
    """
    指定されたファイルから問題固有の採点基準を抽出する（check_criteria.pyと同じ処理）
    
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


def add_source_reference(code: str, task_number: int) -> str:
    """
    関数の先頭に元ファイルの引用を追加
    
    Args:
        code: Pythonコード
        task_number: タスク番号
        
    Returns:
        str: 引用を追加したPythonコード
    """
    # data/XXX.mdから評価基準を取得
    task_id = f"{task_number:03d}"
    data_file = f"data/{task_id}.md"
    criteria_lines = extract_criteria(data_file)
    
    lines = code.split('\n')
    result_lines = []
    
    for i, line in enumerate(lines):
        if line.strip().startswith('def '):
            # 関数定義の直後に評価基準を引用として追加
            result_lines.append(line)
            for criteria_line in criteria_lines:
                result_lines.append(f'    # {criteria_line}')
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def convert_md_to_py(input_file: Path, output_file: Path, task_number: int) -> bool:
    """
    .mdファイルを.pyファイルに変換
    
    Args:
        input_file: 入力ファイル
        output_file: 出力ファイル
        task_number: タスク番号
        
    Returns:
        bool: 変換成功の場合True
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pythonコードを抽出
        python_code = extract_python_code(content)
        
        # コメントを削除
        code_without_comments = remove_comments(python_code)
        
        # 元ファイルの引用を追加
        final_code = add_source_reference(code_without_comments, task_number)
        
        # 出力ファイルに書き込み
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_code)
        
        return True
        
    except Exception as e:
        print(f"エラー: {input_file} の変換に失敗しました - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="rubrics/*.mdファイルからPythonコードを抽出して.pyファイルに変換",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python conv_rubrics.py --all                    # 001-100全て変換
  python conv_rubrics.py --start 3 --end 10       # 003-010を変換
  python conv_rubrics.py --tasks 5 7 12           # 005,007,012のみ変換
  python conv_rubrics.py --start 3 --end 5 -o py  # 出力ディレクトリ指定
"""
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--start", type=int, help="開始タスク番号")
    group.add_argument("--tasks", type=int, nargs="+", help="変換するタスク番号のリスト")
    group.add_argument("--all", action="store_true", help="001-100の全タスクを変換")
    
    parser.add_argument("--end", type=int, help="終了タスク番号（--startと組み合わせて使用）")
    parser.add_argument("-o", "--output-dir", default="rubrics", 
                       help="出力ディレクトリ (デフォルト: rubrics)")
    parser.add_argument("--force", action="store_true", help="既存ファイルを上書き")
    
    args = parser.parse_args()
    
    # タスクリストを決定
    if args.all:
        task_numbers = list(range(1, 101))  # 001から100まで全て
    elif args.tasks:
        task_numbers = args.tasks
    elif args.start:
        end_num = args.end or args.start
        if end_num < args.start:
            parser.error("--end は --start より大きい値を指定してください")
        task_numbers = list(range(args.start, end_num + 1))
    
    # 入力ディレクトリ
    input_dir = Path("rubrics")
    if not input_dir.exists():
        print("エラー: rubricsディレクトリが見つかりません")
        return 1
    
    # 出力ディレクトリ
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"変換対象: {len(task_numbers)}個のタスク")
    print(f"出力ディレクトリ: {output_dir}")
    print()
    
    success_count = 0
    skip_count = 0
    
    for task_num in task_numbers:
        md_file = input_dir / f"{task_num:03d}.md"
        py_file = output_dir / f"{task_num:03d}.py"
        
        # ファイルが存在しない場合はスキップ
        if not md_file.exists():
            print(f"タスク #{task_num:03d} スキップ (ファイルなし)")
            skip_count += 1
            continue
        
        # 既存ファイルのスキップ判定
        if py_file.exists() and not args.force:
            print(f"タスク #{task_num:03d} スキップ (既存)")
            skip_count += 1
            continue
        
        print(f"タスク #{task_num:03d} を処理中... ", end="")
        
        if convert_md_to_py(md_file, py_file, task_num):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print(f"\n完了: {success_count}個変換、{skip_count}個スキップ")
    return 0


if __name__ == "__main__":
    exit(main())
