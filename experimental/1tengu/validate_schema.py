#!/usr/bin/env python3
"""
評価結果がスキーマに準拠しているかチェックするスクリプト

使用方法:
python validate_schema.py <評価結果ディレクトリ>

例:
python validate_schema.py judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """JSONファイルを読み込み"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"エラー: {file_path} の読み込みに失敗: {e}")
        return {}


def load_json_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """JSONデータを直接受け取る（辞書形式）"""
    return data if isinstance(data, dict) else {}


def get_schema_file_path(evaluation_file: Path) -> Path:
    """評価結果ファイルに対応するスキーマファイルのパスを取得"""
    schema_path = Path("data") / evaluation_file.name
    return schema_path


def extract_evaluation_criteria_from_schema(schema: Dict[str, Any]) -> List[str]:
    """スキーマから評価項目一覧を抽出"""
    try:
        evaluation_properties = schema["properties"]["evaluation"]["properties"]
        return list(evaluation_properties.keys())
    except KeyError as e:
        print(f"スキーマの構造が期待と異なります: {e}")
        return []


def extract_evaluation_items_from_result(result: Dict[str, Any]) -> List[str]:
    """評価結果から評価項目一覧を抽出"""
    try:
        evaluation = result["evaluation"]
        return list(evaluation.keys())
    except KeyError:
        print("評価結果に 'evaluation' キーが見つかりません")
        return []


def validate_point_values(result: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """評価項目のポイント値がスキーマのenum値に適合するかチェック"""
    errors = []
    
    try:
        evaluation = result["evaluation"]
        schema_props = schema["properties"]["evaluation"]["properties"]
        
        for criterion_name, criterion_data in evaluation.items():
            if criterion_name not in schema_props:
                continue
                
            # 実際のポイント値
            actual_points = criterion_data.get("points", "")
            
            # スキーマで許可されているenum値
            allowed_values = schema_props[criterion_name]["properties"]["points"]["enum"]
            
            if actual_points not in allowed_values:
                errors.append(f"'{criterion_name}': ポイント値 '{actual_points}' が許可された値 {allowed_values} にありません")
    
    except KeyError as e:
        errors.append(f"データ構造エラー: {e}")
    
    return errors


def validate_required_fields(result: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """必須フィールドの存在をチェック"""
    errors = []
    
    try:
        evaluation = result["evaluation"]
        schema_props = schema["properties"]["evaluation"]["properties"]
        
        for criterion_name, criterion_data in evaluation.items():
            if criterion_name not in schema_props:
                continue
                
            # points と reasoning が存在するかチェック
            if "points" not in criterion_data:
                errors.append(f"'{criterion_name}': 'points' フィールドが見つかりません")
            if "reasoning" not in criterion_data:
                errors.append(f"'{criterion_name}': 'reasoning' フィールドが見つかりません")
    
    except KeyError as e:
        errors.append(f"データ構造エラー: {e}")
    
    return errors


def validate_single_file(evaluation_file: Path) -> Tuple[bool, List[str]]:
    """単一ファイルの検証"""
    # ファイル読み込み
    evaluation_data = load_json_file(evaluation_file)
    
    if not evaluation_data:
        return False, ["ファイルの読み込みに失敗しました"]
    
    # ファイル名からタスク番号を抽出
    try:
        task_number = int(evaluation_file.stem)
    except ValueError:
        return False, [f"ファイル名からタスク番号を抽出できません: {evaluation_file.name}"]
    
    # validate_json_with_schema関数を使用
    return validate_json_with_schema(evaluation_data, task_number)


def validate_json_with_schema(evaluation_data: Dict[str, Any], task_number: int) -> Tuple[bool, List[str]]:
    """JSONデータとスキーマファイルを直接比較検証する
    
    Args:
        evaluation_data: 評価結果のJSONデータ（辞書形式）
        task_number: タスク番号（1-120）
        
    Returns:
        tuple: (is_valid, error_list)
    """
    # スキーマファイルのパスを取得
    task_id = f"{task_number:03d}"
    schema_file = Path(f"data/{task_id}.json")
    
    if not schema_file.exists():
        return False, [f"対応するスキーマファイルが見つかりません: {schema_file}"]
    
    # スキーマ読み込み
    schema_data = load_json_file(schema_file)
    
    if not schema_data:
        return False, ["スキーマファイルの読み込みに失敗しました"]
    
    errors = []
    
    # 評価項目の一致チェック
    schema_criteria = set(extract_evaluation_criteria_from_schema(schema_data))
    result_criteria = set(extract_evaluation_items_from_result(evaluation_data))
    
    missing_in_result = schema_criteria - result_criteria
    extra_in_result = result_criteria - schema_criteria
    
    if missing_in_result:
        errors.append(f"評価結果に不足している項目: {sorted(missing_in_result)}")
    
    if extra_in_result:
        errors.append(f"評価結果にある余分な項目: {sorted(extra_in_result)}")
    
    # ポイント値の検証
    point_errors = validate_point_values(evaluation_data, schema_data)
    errors.extend(point_errors)
    
    # 必須フィールドの検証
    field_errors = validate_required_fields(evaluation_data, schema_data)
    errors.extend(field_errors)
    
    return len(errors) == 0, errors


def validate_directory(directory_path: str) -> None:
    """指定ディレクトリ内の全JSONファイルを検証"""
    dir_path = Path(directory_path)
    
    if not dir_path.exists():
        print(f"エラー: ディレクトリが存在しません: {directory_path}")
        return
    
    # JSONファイルを検索
    json_files = list(dir_path.glob("*.json"))
    
    if not json_files:
        print(f"JSONファイルが見つかりません: {directory_path}")
        return
    
    print(f"検証開始: {len(json_files)} ファイル")
    print(f"対象ディレクトリ: {directory_path}")
    print()
    
    total_files = len(json_files)
    valid_files = 0
    
    for json_file in sorted(json_files):
        print(f"検証中: {json_file.name}")
        
        is_valid, errors = validate_single_file(json_file)
        
        if is_valid:
            print(f"✓ {json_file.name}: OK")
            valid_files += 1
        else:
            print(f"✗ {json_file.name}: エラーあり")
            for error in errors:
                print(f"  - {error}")
        print()
    
    # 結果サマリー
    print("=" * 50)
    print(f"検証完了:")
    print(f"  総ファイル数: {total_files}")
    print(f"  有効: {valid_files}")
    print(f"  エラー: {total_files - valid_files}")
    
    if valid_files == total_files:
        print("すべてのファイルがスキーマに適合しています ✓")
    else:
        print("一部のファイルにエラーがあります ✗")


def main():
    if len(sys.argv) != 2:
        print("使用方法: python validate_schema.py <評価結果ディレクトリ>")
        print("例: python validate_schema.py judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    validate_directory(directory_path)


if __name__ == "__main__":
    main()
