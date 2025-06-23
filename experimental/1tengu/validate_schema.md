# validate_schema.py - 評価結果スキーマ検証スクリプト

## 概要

`validate_schema.py`は、構造化出力で生成された評価結果がJSONスキーマに適合しているかを検証するスクリプトです。Tengu Benchmark評価タスクにおいて、LLM-as-a-Judge評価の品質保証と一貫性確保を目的として開発されました。

## 背景

### 構造化出力への移行

Shaberi評価フレームワークでは、従来のFew-shot形式からJSONスキーマベースの構造化出力への移行を実施しました。この移行により、以下の問題を解決：

1. **計算エラーの排除**: LLMによる合計点の誤計算を防止
2. **形式の統一**: 一貫したJSON構造による出力フォーマットの安定化
3. **効率的な処理**: 構造化データの直接利用によるパース処理の簡素化
4. **トークン節約**: Few-shot例が不要になり、コスト削減を実現

### 品質保証の必要性

構造化出力の導入により、評価結果の形式的な一貫性は向上しましたが、以下の検証が必要になりました：

- **スキーマ適合性**: 評価結果がJSONスキーマ定義に準拠しているか
- **項目完全性**: すべての評価項目が過不足なく含まれているか
- **値の妥当性**: ポイント値がスキーマで定義されたenum値の範囲内にあるか
- **必須フィールド**: `points`と`reasoning`が確実に存在するか

## 検証機能

### 1. 評価項目の完全性チェック

**スキーマとの項目一致確認:**
```python
schema_criteria = set(extract_evaluation_criteria_from_schema(schema_data))
result_criteria = set(extract_evaluation_items_from_result(evaluation_data))

missing_in_result = schema_criteria - result_criteria
extra_in_result = result_criteria - schema_criteria
```

**検出内容:**
- 評価結果に不足している項目
- 評価結果にある余分な項目

### 2. ポイント値の妥当性検証

**enum値との適合性チェック:**
```python
actual_points = criterion_data.get("points", "")
allowed_values = schema_props[criterion_name]["properties"]["points"]["enum"]

if actual_points not in allowed_values:
    errors.append(f"ポイント値 '{actual_points}' が許可された値 {allowed_values} にありません")
```

**検証対象:**
- 0-1点スケール: `["0", "1"]`
- 0-2点スケール: `["0", "1", "2"]`
- 0-3点スケール: `["0", "1", "2", "3"]`
- 0-4点スケール: `["0", "1", "2", "3", "4"]`

### 3. 必須フィールドの存在確認

**構造化データの完全性チェック:**
```python
if "points" not in criterion_data:
    errors.append(f"'{criterion_name}': 'points' フィールドが見つかりません")
if "reasoning" not in criterion_data:
    errors.append(f"'{criterion_name}': 'reasoning' フィールドが見つかりません")
```

### 4. ファイル対応関係の自動解決

**スキーマファイルの自動検索:**
```python
def get_schema_file_path(evaluation_file: Path) -> Path:
    schema_path = Path("data") / evaluation_file.name
    return schema_path
```

評価結果ファイル（例：`gemini-2.5-pro/001.json`）に対応するスキーマファイル（`data/001.json`）を自動的に特定します。

## 使用方法

### 基本実行

```bash
uv run validate_schema.py <評価結果ディレクトリ>
```

### 実行例

```bash
# Gemini 2.5 Proの評価結果を検証
uv run validate_schema.py judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro
```

### 出力例

#### 正常時
```
検証開始: 120 ファイル
対象ディレクトリ: judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro

検証中: 001.json
✓ 001.json: OK

...

==================================================
検証完了:
  総ファイル数: 120
  有効: 120
  エラー: 0
すべてのファイルがスキーマに適合しています ✓
```

#### エラー時
```
検証中: 042.json
✗ 042.json: エラーあり
  - '答えが正確である': ポイント値 '5' が許可された値 ['0', '1', '2', '3', '4'] にありません
  - 評価結果に不足している項目: ['自然な日本語である']
  - '不明な項目': 'reasoning' フィールドが見つかりません
```

## 技術仕様

### 依存関係
- **標準ライブラリのみ**: `json`, `sys`, `pathlib`, `typing`
- **外部依存なし**: 追加インストール不要

### パフォーマンス
- **高速処理**: 120件を数秒で完了
- **メモリ効率**: ファイル単位での逐次処理
- **エラー耐性**: 1件の失敗が全体処理に影響しない

### エラーハンドリング

#### 想定されるエラーパターン

1. **スキーマファイル未存在**
   ```
   対応するスキーマファイルが見つかりません: data/999.json
   ```

2. **JSONパースエラー**
   ```
   ファイルの読み込みに失敗しました
   ```

3. **データ構造エラー**
   ```
   データ構造エラー: 'evaluation'
   ```

4. **ポイント値範囲外**
   ```
   ポイント値 '10' が許可された値 ['0', '1', '2', '3'] にありません
   ```

## 検証結果

### Gemini 2.5 Pro評価結果の検証

**実行日**: 2025年6月19日
**対象**: `judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro/`
**結果**: 120/120ファイルが完全適合

```
検証完了:
  総ファイル数: 120
  有効: 120
  エラー: 0
すべてのファイルがスキーマに適合しています ✓
```

この結果により、以下が確認されました：

1. **構造化出力の完全機能**: Gemini 2.5 ProがJSONスキーマに完全準拠した出力を生成
2. **評価項目の網羅性**: 全120タスクで評価項目の過不足なし
3. **ポイント値の妥当性**: すべてのポイント値がenum定義の範囲内
4. **データ完整性**: 必須フィールド（points, reasoning）が全件で存在

## 活用場面

### 1. 評価システムの品質保証

新しいLLMモデルでの評価実行後、結果の形式的な正確性を即座に確認できます。

### 2. スキーマ変更時の影響確認

JSONスキーマを更新した際に、既存の評価結果との互換性を検証できます。

### 3. 評価プロセスのデバッグ

評価結果に問題がある場合、スキーマレベルでの不整合を迅速に特定できます。

### 4. 大規模評価の一括検証

数百件の評価結果ファイルを効率的に検証し、品質を保証できます。

## 拡張可能性

### 1. 他ベンチマーク対応

ELYZA-tasks-100、ja-mt-benchなど、他の評価データセットへの適用が可能です：

```python
# スキーマディレクトリの動的指定
def get_schema_file_path(evaluation_file: Path, schema_dir: str = "data") -> Path:
    schema_path = Path(schema_dir) / evaluation_file.name
    return schema_path
```

### 2. 詳細レポート生成

統計情報や傾向分析の追加：

```python
def generate_validation_report(results: List[ValidationResult]) -> Dict[str, Any]:
    return {
        "total_files": len(results),
        "valid_files": sum(1 for r in results if r.is_valid),
        "common_errors": analyze_error_patterns(results),
        "score_distribution": analyze_score_distribution(results)
    }
```

### 3. 継続的インテグレーション

CI/CDパイプラインに組み込んで、評価結果の自動検証：

```yaml
- name: Validate evaluation results
  run: uv run validate_schema.py ${{ matrix.eval_dir }}
```

## tengu.pyとの統合

### リアルタイムスキーマ検証

`tengu.py`スクリプトでは、LLMが評価結果JSONを生成した直後に`validate_json_with_schema`関数を使用してスキーマ適合性を検証します：

```python
from validate_schema import validate_json_with_schema

# LLM評価結果の生成後
result_json = evaluate_task(task_num, model_answer, args.model)

# 即座にスキーマ検証を実行
is_valid, errors = validate_json_with_schema(result_json, task_num)
if not is_valid:
    error_msg = f"スキーマ検証失敗: タスク {task_num:03d}\n" + "\n".join(f"  - {error}" for error in errors)
    raise ValueError(error_msg)
else:
    print(f"✓ スキーマ検証: OK")
```

### 検証失敗時の処理

**成功時の表示:**
```
タスク 001: 評価中...
✓ スキーマ検証: OK
タスク 001: 完了 (10/10点)
```

**失敗時の処理:**
```python
ValueError: スキーマ検証失敗: タスク 042
  - '答えが正確である': ポイント値 '5' が許可された値 ['0', '1', '2', '3', '4'] にありません
  - 評価結果に不足している項目: ['自然な日本語である']
```

検証に失敗した場合、処理を即座に停止してエラーの詳細を報告します。これにより、不適切な評価結果がファイルに保存されることを防ぎます。

### 統合機能の利点

1. **品質保証の自動化**: 手動検証が不要
2. **即座のフィードバック**: 問題を早期発見
3. **データ整合性の確保**: 不正な結果の保存を防止
4. **開発効率の向上**: エラーの迅速な特定と修正

## 関連ファイル

- **tengu.py**: 構造化出力評価スクリプト（スキーマ検証統合済み）
- **md_to_schema.py**: Markdown→JSONスキーマ変換（前段階）
- **data/*.json**: JSONスキーマ定義ファイル（120件）
- **judge/gemini-2.5-flash-preview-05-20/gemini-2.5-pro/*.json**: 検証対象の評価結果
- **md_to_schema.md**: スキーマ生成プロセスの詳細説明

## まとめ

`validate_schema.py`により、構造化出力による評価結果の品質保証が自動化されました。これにより、Shaberi評価フレームワークの信頼性が大幅に向上し、大規模な評価タスクでも一貫した品質を維持できるようになりました。

従来のFew-shot形式では困難だった形式的な検証が、構造化出力とスキーマ検証の組み合わせにより実現され、次世代の評価フレームワークとしての完成度を高めています。
