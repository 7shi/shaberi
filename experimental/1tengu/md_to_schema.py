#!/usr/bin/env python3
"""
MD to JSON Schema Converter for Tengu Benchmark
data/xxx.md から data/xxx.json へJSONスキーマを生成するスクリプト
"""
import json
import re
from pathlib import Path

def parse_criteria_from_md(content):
    """MDファイルから評価項目を抽出"""
    
    lines = content.split('\n')
    state = 'search'
    criteria = []
    current_parent = None
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
                match = re.match(r'-(.+):(\d+)点$', line)
                if match:
                    description = match.group(1).strip()
                    points = int(match.group(2))
                    criteria.append({
                        'description': description,
                        'points': points
                    })
            elif re.match(r'-.+$', line):
                # 階層の親項目
                current_parent = re.match(r'-(.+)$', line).group(1).strip()
                state = 'checking_indent'
            else:
                return None  # 形式エラー
        
        elif state == 'checking_indent':
            if line == '':
                state = 'waiting_for_next'
                current_parent = None
            elif re.match(r'  -.+:\d+点$', line):
                # インデントされた子項目
                match = re.match(r'  -(.+):(\d+)点$', line)
                if match:
                    child_desc = match.group(1).strip()
                    points = int(match.group(2))
                    # 親：子の形式で結合
                    full_description = f"{current_parent}：{child_desc}"
                    criteria.append({
                        'description': full_description,
                        'points': points
                    })
            else:
                # インデントされていない場合はreading_criteriaに戻る
                current_parent = None
                state = 'reading_criteria'
                continue
        
        elif state == 'waiting_for_next':
            if line == '':
                pass  # 空行をスキップ
            elif line == '[評価するモデルの回答]':
                break  # 解析完了
            else:
                return None  # 期待しない内容
        
        i += 1
    
    return criteria

def generate_json_schema(criteria):
    """評価項目からJSONスキーマを生成"""
    
    properties = {}
    required = []
    
    for criterion in criteria:
        description = criterion['description']
        # ダブルクォートをシングルクォートに置換
        description = description.replace('"', "'")
        points = criterion['points']
        
        # enumを生成（0からmax_pointsまで）
        enum_values = [str(i) for i in range(points + 1)]
        
        properties[description] = {
            "type": "object",
            "properties": {
                "points": {
                    "type": "string",
                    "enum": enum_values,
                    "description": f"Points assigned (0-{points} scale based on how well this criterion is met)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Brief explanation in Japanese of why this score was assigned"
                }
            },
            "required": ["points", "reasoning"]
        }
        
        required.append(description)
    
    schema = {
        "type": "object",
        "properties": {
            "evaluation": {
                "type": "object",
                "properties": properties,
                "required": required
            },
            "summary": {
                "type": "string",
                "description": "Overall assessment summary in Japanese of the model's answer"
            }
        },
        "required": ["evaluation", "summary"]
    }
    
    return schema

def main():
    """メイン処理"""
    
    # dataディレクトリの確認
    input_dir = Path("data")
    if not input_dir.exists():
        print(f"エラー: {input_dir} ディレクトリが見つかりません")
        return
    
    total_files = 0
    success_count = 0
    error_count = 0
    
    print("MD → JSONスキーマ変換開始")
    
    # 各MDファイルを処理
    for md_file in sorted(input_dir.glob("*.md")):
        total_files += 1
        
        try:
            # MDファイルを読み込み
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 評価項目を抽出
            criteria = parse_criteria_from_md(content)
            if criteria is None:
                print(f"✗ {md_file.name}: 評価項目の解析に失敗")
                error_count += 1
                continue
            
            # JSONスキーマを生成
            schema = generate_json_schema(criteria)
            
            # JSONファイルに出力
            json_file = input_dir / f"{md_file.stem}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(schema, f, ensure_ascii=False, indent=2)
            
            success_count += 1
            print(f"✓ {md_file.name} → {json_file.name}")
            
        except Exception as e:
            print(f"✗ {md_file.name}: {e}")
            error_count += 1
    
    print(f"\n変換完了:")
    print(f"  処理ファイル: {total_files}件")
    print(f"  成功: {success_count}件")
    print(f"  エラー: {error_count}件")

if __name__ == "__main__":
    main()
