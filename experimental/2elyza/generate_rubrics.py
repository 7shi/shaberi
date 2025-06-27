#!/usr/bin/env python3
"""
ELYZA-tasks-100 評価基準を自動コード化するスクリプト

check_criteria.pyの機能を利用して各課題の評価基準を取得し、
few-shotとして rubrics-001.py, rubrics-002.py を使って
003以降の評価関数を自動生成する。
"""

import argparse
import glob
import os
from pathlib import Path
from llm7shi.compat import generate_with_schema
from llm7shi import DEFAULT_MODEL, do_show_params
from check_criteria import extract_criteria


examples = {}


def get_task_criteria(task_number: int) -> str:
    """
    指定されたタスク番号の評価基準を取得
    
    Args:
        task_number: タスク番号 (例: 3)
    
    Returns:
        str: 抽出された評価基準テキスト
    """
    # タスク番号を3桁にフォーマット
    task_id = f"{task_number:03d}"
    
    # data/XXX.mdファイルを探す
    data_file = f"data/{task_id}.md"
    if not os.path.exists(data_file):
        raise FileNotFoundError(f"タスクファイルが見つかりません: {data_file}")
    
    # 評価基準を抽出
    criteria_lines = extract_criteria(data_file)
    
    # 空行を除去
    criteria_lines = [line for line in criteria_lines if line.strip()]
    
    return '\n'.join(criteria_lines)


def generate_rubric_function(task_number: int, criteria_text: str, model: str, test_mode: bool = False) -> str:
    """
    LLMを使って評価基準からPython関数を生成
    
    Args:
        task_number: タスク番号
        criteria_text: 評価基準テキスト
        model: 使用するLLMモデル
        test_mode: テストモード（プロンプト表示のみ）
    
    Returns:
        str: 生成されたPython関数コード（テストモードではダミー）
    """
    
    # プロンプトを構築
    prompt = f"""あなたはELYZA-tasks-100の評価基準をPython関数としてコード化する専門家です。

以下のfew-shot例を参考に、タスク#{task_number:03d}の評価基準をPython関数として実装してください。

## Few-shot例1: rubrics-001.py
```python
{examples[1]}
```

## Few-shot例2: rubrics-002.py  
```python
{examples[2]}
```

## 実装ルール

1. **関数名**: `judge_{task_number:03d}(score: int, judge: callable) -> int`
2. **パラメータ**:
   - `score`: 初期スコア（通常5点）
   - `judge`: 判定関数（文字列を受け取りbooleanを返す）
3. **実装パターン**:
   - 評価基準をコメントとして記載
   - `judge()`関数で条件判定
   - 条件に応じてスコアを調整
   - 最終スコアを返す

以下の評価基準に基づいて、Python関数を実装してください。関数のみを出力し、追加の説明は不要です。

## タスク#{task_number:03d}の評価基準
{criteria_text}
""".rstrip()

    # テストモードならプロンプトを表示して空文字列を返す
    if test_mode:
        do_show_params([prompt], model=model)
        return ""

    # LLMで生成
    result = generate_with_schema([prompt], model=model)
    
    return result.text


def main():
    parser = argparse.ArgumentParser(
        description="ELYZA-tasks-100評価基準の自動コード化",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python generate_rubrics.py --start 3 --end 10        # 003-010を生成
  python generate_rubrics.py --tasks 5 7 12           # 005,007,012のみ生成
  python generate_rubrics.py --all                    # 003-100全て生成
  python generate_rubrics.py --start 3 --end 5 -m gpt-4o-mini  # 別モデル使用"""
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--start", type=int, help="開始タスク番号")
    group.add_argument("--tasks", type=int, nargs="+", help="生成するタスク番号のリスト")
    group.add_argument("--all", action="store_true", help="003-100の全タスクを生成")
    
    parser.add_argument("--end", type=int, help="終了タスク番号（--startと組み合わせて使用）")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                       help=f"使用するLLMモデル (デフォルト: {DEFAULT_MODEL})")
    parser.add_argument("-o", "--output-dir", default="rubrics", 
                       help="出力ディレクトリ (デフォルト: rubrics)")
    parser.add_argument("--test", action="store_true",
                       help="テストモード（プロンプト表示のみ、LLM呼び出しなし）")
    
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
    
    # dataディレクトリの存在確認
    if not os.path.exists("data"):
        print("エラー: dataディレクトリが見つかりません")
        return 1
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"LLMモデル: {args.model}")
    print(f"生成対象: {len(task_numbers)}個のタスク")
    print(f"出力ディレクトリ: {output_dir}")
    if args.test:
        print("テストモード: プロンプト表示のみ")
    print()
    
    rubrics_001_path = Path("rubrics-001.py")
    rubrics_002_path = Path("rubrics-002.py")
    
    if not rubrics_001_path.exists() or not rubrics_002_path.exists():
        raise FileNotFoundError("rubrics-001.py または rubrics-002.py が見つかりません")
    
    with open(rubrics_001_path, 'r', encoding='utf-8') as f:
        examples[1] = f.read().rstrip()
    
    with open(rubrics_002_path, 'r', encoding='utf-8') as f:
        examples[2] = f.read().rstrip()
    
    for task_num in task_numbers:
        output_file = output_dir / f"{task_num:03d}.md"
        
        # テストモードでない場合のみスキップ判定
        if not args.test and output_file.exists():
            print(f"タスク #{task_num:03d} スキップ (既存)")
            continue
            
        print(f"タスク #{task_num:03d} を処理中...", end=" ")
        
        # 001と002は既存ファイルをコピー
        if task_num == 1:
            if not args.test:
                generated_code = f"```python\n{examples[1]}\n```"
            else:
                print("✓ (テストモード)")
                continue
        elif task_num == 2:
            if not args.test:
                generated_code = f"```python\n{examples[2]}\n```"
            else:
                print("✓ (テストモード)")
                continue
        else:
            # 003以降はLLMで生成
            criteria_text = get_task_criteria(task_num)
            generated_code = generate_rubric_function(task_num, criteria_text, args.model, args.test)
            
            # テストモードならファイル保存せずに次へ
            if args.test:
                print("✓ (テストモード)")
                continue
        
        # ファイルに保存（テストモードでない場合のみ）
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        
        print("✓")
    
    # 完了メッセージ
    if not args.test:
        print(f"\n完了: {output_dir} に個別ファイルが生成されました")
    else:
        print("\nテストモード完了: ファイルは保存されませんでした")


if __name__ == "__main__":
    main()
