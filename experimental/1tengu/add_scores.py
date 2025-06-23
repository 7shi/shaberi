#!/usr/bin/env python3
"""
Add score field to existing evaluation JSON files
既存の評価結果JSONファイルにscoreフィールドを追加する
"""

import argparse
import json
from pathlib import Path
from tqdm import tqdm


def calculate_score(result_json):
    """Calculate total score from evaluation result JSON
    
    Args:
        result_json: dict containing evaluation results
        
    Returns:
        int: Total score
    """
    total = 0
    evaluation = result_json.get("evaluation", {})
    
    for criterion, data in evaluation.items():
        points = int(data.get("points", "0"))
        total += points
    
    return total


def process_json_file(json_path, dry_run=False):
    """Process a single JSON file to add score field
    
    Args:
        json_path: Path to JSON file
        dry_run: If True, only show what would be done without modifying files
        
    Returns:
        tuple: (was_modified, score)
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if score already exists
        if "score" in data:
            return False, data["score"]
        
        # Calculate score
        score = calculate_score(data)
        
        if not dry_run:
            # Add score to data
            data["score"] = score
            
            # Write back to file
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True, score
        
    except Exception as e:
        print(f"Error processing {json_path}: {e}")
        return False, None


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="既存の評価結果JSONファイルにscoreフィールドを追加",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  # 特定のディレクトリ内の全JSONファイルを処理
  uv run add_scores.py 1tengu/gemini-2.5-flash/gemini-2.5-pro
  
  # ドライラン（実際には変更しない）
  uv run add_scores.py 1tengu/gemini-2.5-flash/gemini-2.5-pro --dry-run
  
  # 再帰的に全サブディレクトリを処理
  uv run add_scores.py 1tengu --recursive"""
    )
    parser.add_argument("directory", help="処理対象のディレクトリパス")
    parser.add_argument("--dry-run", action="store_true", 
                        help="実際にファイルを変更せず、何が行われるかを表示")
    parser.add_argument("--recursive", "-r", action="store_true",
                        help="サブディレクトリも再帰的に処理")
    args = parser.parse_args()
    
    # Convert to Path object
    target_dir = Path(args.directory)
    
    # Validate directory exists
    if not target_dir.exists():
        parser.error(f"ディレクトリが存在しません: {target_dir}")
    if not target_dir.is_dir():
        parser.error(f"ディレクトリではありません: {target_dir}")
    
    # Find all JSON files
    if args.recursive:
        json_files = sorted(target_dir.rglob("*.json"))
    else:
        json_files = sorted(target_dir.glob("*.json"))
    
    if not json_files:
        print(f"JSONファイルが見つかりません: {target_dir}")
        return
    
    print(f"対象ファイル数: {len(json_files)}")
    if args.dry_run:
        print("ドライランモード: ファイルは変更されません")
    print()
    
    # Process each file
    modified_count = 0
    already_has_score = 0
    error_count = 0
    
    for json_path in tqdm(json_files, desc="処理中"):
        was_modified, score = process_json_file(json_path, args.dry_run)
        
        if score is None:
            error_count += 1
        elif was_modified:
            modified_count += 1
            if args.dry_run:
                print(f"追加予定: {json_path} (score={score})")
        else:
            already_has_score += 1
    
    # Summary
    print(f"\n処理完了:")
    print(f"  - 変更{'予定' if args.dry_run else '済み'}: {modified_count}件")
    print(f"  - score既存: {already_has_score}件")
    if error_count > 0:
        print(f"  - エラー: {error_count}件")
    
    if args.dry_run and modified_count > 0:
        print("\n実際にファイルを変更するには、--dry-runオプションを外して再実行してください")


if __name__ == "__main__":
    main()