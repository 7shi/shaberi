#!/usr/bin/env python3
"""
shaberi3-evaluations.jsonから質問内容を分類してダンプするスクリプト

tengu: line_data[3]["contents"] (Few-shot形式)
elyza, mt: line_data[1]["contents"] (シンプル形式)
"""

import json
import os
from pathlib import Path


def classify_and_dump_questions(input_file):
    """質問内容を分類してJSONファイルにダンプ"""
    tengu_questions = []
    elyza_questions = []
    mt_questions = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                line_data = json.loads(line.strip())
                
                # line_dataの長さで分類
                if len(line_data) == 4:
                    # tengu_bench (Few-shot形式)
                    content = line_data[3]["content"]
                    tengu_questions.append(content)
                elif len(line_data) == 2:
                    # elyza または mt_bench
                    content = line_data[1]["content"]
                    
                    # プレフィックスで判定
                    if content.startswith("あなたは採点者です。"):
                        elyza_questions.append(content)
                    elif content.startswith("[指示]\n公平な判断者として行動し"):
                        mt_questions.append(content)
                    else:
                        print(f"Warning: Unclassified content at line {line_num}")
                        
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Error processing line {line_num}: {e}")
                continue
    
    # 結果をファイルに出力
    datasets = [
        ('1tengu.json', tengu_questions),
        ('2elyza.json', elyza_questions), 
        ('3mt.json', mt_questions)
    ]
    
    for filename, questions in datasets:
        with open(filename, 'w', encoding='utf-8') as f:
            for question in questions:
                json.dump(question, f, ensure_ascii=False)
                f.write('\n')
        print(f"Dumped {len(questions)} questions to {filename}")
    
    # 統計情報を表示
    total = len(tengu_questions) + len(elyza_questions) + len(mt_questions)
    print(f"\nSummary:")
    print(f"  tengu: {len(tengu_questions)} questions")
    print(f"  elyza: {len(elyza_questions)} questions") 
    print(f"  mt: {len(mt_questions)} questions")
    print(f"  Total: {total} questions")


def main():
    input_file = "shaberi3-evaluations.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        return
    
    classify_and_dump_questions(input_file)


if __name__ == "__main__":
    main()
